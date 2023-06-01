from psql import *
from mongodb import *
from flask_cors import CORS
from flask import Flask, request, abort,jsonify

app = Flask(__name__)

with app.app_context():
    setup_psql(app)
CORS(app, origin="*")

@app.route("/get_id_by_correo", methods = ["GET"])
def get_id_by_correo():

    body = request.get_json()

    if body is None:
        abort(422)
    
    correo = body.get("correo", None)

    if correo is None:
        abort(422)

    user = Usuario.query.filter(Usuario.correo == correo).one_or_none()

    if user is None:
        abort(404)
    
    return jsonify({
        "success": True,
        "user_id": user.id
    })

@app.route("/signup", methods = ["POST"])
def signup():
    body = request.get_json()

    if body is None:
        abort(422)
    
    nombres = body.get('nombres', None)
    apellidos = body.get('apellidos', None)
    correo = body.get('correo', None)
    celular = body.get('celular', None)
    password = body.get('password', None)
    role = body.get('role', None)

    area = body.get('area', None)
    ciclo = body.get('ciclo', None)
    carrera = body.get('carrera', None)
    emociones = body.get('emociones', None)
    P1 = body.get('P1', None)
    P2 = body.get('P2', None)
    P3 = body.get('P3', None)
    

    user = Usuario.query.filter(Usuario.correo == correo).one_or_none()
    if user is not None or role is None:
        abort(422)

    usuario = Usuario(nombres=nombres,apellidos=apellidos, correo=correo, celular=celular,password=password)

    if role == 'administrador':
        if nombres is None or apellidos is None or correo is None or celular is None or password is None or area is None:
            abort(422)
        else:
            new_user_id = usuario.insert()
            administrador = Administrador(id=new_user_id, area=area)
            administrador.insert()

    else:
        if nombres is None or apellidos is None or correo is None or celular is None or password is None or ciclo is None or carrera is None or emociones is None or P1 is None or P2 is None or P3 is None:
            abort(422)
        else:
            new_user_id = usuario.insert()
            alumno = Alumno(id=new_user_id, ciclo=ciclo, carrera=carrera)
            new_alumno_id = alumno.insert()
            perfil = Perfil(userid=new_alumno_id,emociones=emociones,P1=P1,P2=P2,P3=P3)
            perfil.insert()

    return jsonify({
        'success': True
    })

@app.route("/login", methods=['GET', 'POST'])
def login():
    body = request.get_json()

    if body is None:
        abort(404)

    correo = body.get("correo", None)
    password = body.get("password", None)

    if correo is None or password is None:
        abort(404)

    user = Usuario.query.filter((Usuario.correo == correo) & (Usuario.password == password)).one_or_none()

    if user is None:
        abort(404)

    return jsonify({
        'success': True
    })

@app.route("/get_user/<user_id>", methods = ['GET'])
def get_user(user_id):

    user = Usuario.query.filter(Usuario.id == user_id).one_or_none()
    
    if user is None:
        abort(404)

    alumno = Alumno.query.filter(Alumno.id == user.id).one_or_none()
    administrador = Administrador.query.filter(Administrador.id==user.id).one_or_none()

    if alumno is not None:
        especifico = alumno.format()
    else:
        especifico = administrador.format()
    
    return jsonify({
        "success": True,
        "general": user.format(),
        "especifico": especifico
    })

@app.route("/update_user/<user_id>", methods = ["PATCH"])
def update_user(user_id):
    user = Usuario.query.filter(Usuario.id == user_id).one_or_none()

    if user is None:
        abort(404)

    body = request.get_json()

    correo = body.get("correo",None)

    existing_user = Usuario.query.filter(Usuario.correo == correo).one_or_none()
    if existing_user is not None:
        abort(422)

    if "nombres" in body:
        if body.get("nombres") != "":
            user.nombres = body.get("nombres")
    if "apellidos" in body:
        if body.get("apellidos") != "":
            user.apellidos = body.get("apellidos")
    if "correo" in body:
        if body.get("correo") != "":
            user.correo = body.get("correo")
    if "celular" in body:
        if body.get("celular") != "":
            user.celular = body.get("celular")
    if "password" in body:
        if body.get("password") != "":
            user.password = body.get("password")

    admin = Administrador.query.filter(Administrador.id == user_id).one_or_none()
    alumno = Alumno.query.filter(Alumno.id == user_id).one_or_none()

    if admin is not None:
        if "area" in body:
            if body.get("area") != "":
                admin.area = body.get("area")
        
        if body.get("nombres") == "" and body.get("apellidos") == "" and body.get("correo") == "" and body.get("celular") == "" and body.get("password") == "" and body.get("area") == "":
            abort(422)

        user.update()
        admin.update()

    else:
        if "ciclo" in body:
            if body.get("ciclo") != "":
                alumno.ciclo = body.get("ciclo")
        if "carrera" in body:
            if body.get("carrera") != "":
                alumno.carrera = body.get("carrera")
        
        if body.get("nombres") == "" and body.get("apellidos") == "" and body.get("correo") == "" and body.get("celular") == "" and body.get("password") == "" and body.get("ciclo") == "" and body.get("carrera") == "":
            abort(422)

        user.update()
        alumno.update()

    return jsonify({
        'success': True,
        "id": user_id
    })

@app.route("/delete_user/<user_id>", methods = ["DELETE"])
def delete_user(user_id):

    user = Usuario.query.filter(Usuario.id == user_id).one_or_none()

    if user is None:
        abort(404)

    sesions = []
    query = {"AlumnoID": user.id}
    result = sesion.find(query)

    for r in result:
        sesions.append(r['SessionID'])

    sesion.delete_many(query)

    for id in sesions:
        message.delete_many({"SessionID":id})

    admin = Administrador.query.filter(Administrador.id == user_id).one_or_none()
    alumno = Alumno.query.filter(Alumno.id == user_id).one_or_none()

    if admin is not None:
        admin.delete()
        user.delete()
    else:
        perfil = Perfil.query.filter(Perfil.userid == user_id).one_or_none()
        perfil.delete()
        alumno.delete()
        user.delete()

    return jsonify({
        "success":True,
        "deleted": user_id
    })

@app.route("/get_perfil/<user_id>", methods = ["GET"])
def get_perfil(user_id):
    perfil = Perfil.query.filter(Perfil.userid==user_id).one_or_none()

    if perfil is None:
        abort(404)
    
    return jsonify({
        "sucess": True,
        "perfil": perfil.format()
    })

@app.route("/update_perfil/<user_id>", methods= ["PATCH"])
def update_perfil(user_id):

    perfil = Perfil.query.filter(Perfil.userid == user_id).one_or_none()

    if perfil is None:
        abort(404)

    body = request.get_json()

    if "emociones" in body:
        if body.get("emociones") != "":
            perfil.emociones = body.get("emociones")
    if "P1" in body:
        if body.get("P1") != "":
            perfil.P1 = body.get("P1")
    if "P2" in body:
        if body.get("P2") != "":
            perfil.P2 = body.get("P2")
    if "P3" in body:
        if body.get("P3") != "":
            perfil.P3 = body.get("P1")

    if body.get('emociones') == "" and body.get("P1") == "" and body.get("P2") == ""and body.get("P3") == "":
        abort(422)
    
    perfil.update()

    return jsonify({
        'success': True,
        "userid": perfil.userid,
        "perfilid": perfil.id
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'statusCode': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'statusCode': 500,
        'message': 'Internal Server error'
    }), 500


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'statusCode': 422,
        'message': 'Unprocessable'
    }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "statusCode": 400,
        "message": "bad request"
    }), 400

@app.route("/")
def indice():
    return "Api para RDB"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)



