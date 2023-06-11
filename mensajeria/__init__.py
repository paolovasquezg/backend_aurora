from flask import Flask, request, jsonify, abort
import datetime
from flask_cors import CORS
from psql import *
from mongodb import *
import json
import requests


def create_app(db_path=db_path):
    app = Flask(__name__)
    with app.app_context():
        setup_psql(app,db_path)
    CORS(app, origin="*")

    @app.route("/enviar_recibir/<user_id>", methods = ["POST"])
    def send_receive(user_id):
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

        body = request.get_json()

        alumno = Alumno.query.filter(Alumno.user_id == user_id).one_or_none()

        enviado = body.get("content", None)
        sesionid = body.get("sesionid", None)

        if alumno is None or enviado is None or sesionid is None:
            abort(422)

        user = Usuario.query.filter(Usuario.user_id == user_id).one_or_none()
        perfil = Perfil.query.filter(Perfil.user_id == user_id).one_or_none()

        if alumno.sexo == "M":
            sexo = "un joven universitario"
        else:
            sexo = "una joven universitaria"
        
        if perfil.asistirpsicologo == True:
            psicologo = "Ya ha asistido al psicólogo"
        else:
            psicologo = "Nunca ha asistido al psicólogo"
        
        if perfil.difEst == True:
            dif = "se siente abrumado y tiene dificultades para concentrarse en los estudios"
        else:
            dif = "no se siente abrumado y tampoco tiene dificultades para concentrarse en los estudios"
        
        context = "Eres un bot de salud mental para " + user.nombres + " " + user.apellidos + ", " + sexo + " de " + str(alumno.ciclo) + " ciclo de la carrera de " + alumno.carrera + " en Perú. " + psicologo + ". " + "Se le ha diagnosticado con: " + perfil.condicionSM + "; y últimamente ha estado sintiendo estas emociones: " + perfil.emociones + ". En las ultimas semanas ha tenido un estado anímico de " + str(perfil.estadoAnimico) + " de 10 y " + dif + ". Tiene como expectativas de conversar con este bot lo siguiente: " + perfil.expectativas + "." 
        

        result = sesion.find({"SessionID": sesionid})
        result = list(result)

        if len(result) == 0:
            sesion.insert_one({"SessionID": sesionid, "AlumnoID": alumno.user_id,
                            "Start": date_time, "Context": context})
        
        message.insert_one({"SessionID": sesionid, "Role": "user", "Content": enviado})

        entrada = {"messages": [
            {
                "role": "system",
                "content": context
            },
            {
                "role": "user",
                "content": enviado
            }
        ]}

        response = requests.post(
                "https://ojq5bhiphe.execute-api.us-east-1.amazonaws.com/test/messages", data=json.dumps(entrada))

        response = response.json()

        if response["statusCode"] != 200:
            abort(400, description="No se retorna un mensaje al usuario")

        message.insert_one({"SessionID": sesionid, "Role": "assistant", "Content": response["body"]})

        return jsonify({
            "enviado": enviado,
            "respuesta": response["body"],
            "statusCode": response["statusCode"]
        })

    @app.route("/enviar_contexto/<user_id>", methods = ["GET"])
    def send_context(user_id):
        alumno = Alumno.query.filter(Alumno.user_id == user_id).one_or_none()

        if alumno is None:
            abort(404)

        user = Usuario.query.filter(Usuario.user_id == user_id).one_or_none()
        perfil = Perfil.query.filter(Perfil.user_id == user_id).one_or_none()

        if alumno.sexo == "M":
            sexo = "un joven universitario"
        else:
            sexo = "una joven universitaria"
        
        if perfil.asistirpsicologo == True:
            psicologo = "Ya ha asistido al psicólogo"
        else:
            psicologo = "Nunca ha asistido al psicólogo"
        
        if perfil.difEst == True:
            dif = "se siente abrumado y tiene dificultades para concentrarse en los estudios"
        else:
            dif = "no se siente abrumado y tampoco tiene dificultades para concentrarse en los estudios"
        
        context = "Eres un bot de salud mental para " + user.nombres + " " + user.apellidos + ", " + sexo + " de " + str(alumno.ciclo) + " ciclo de la carrera de " + alumno.carrera + " en Perú. " + psicologo + ". " + "Se le ha diagnosticado con: " + perfil.condicionSM + "; y ultimamente ha estado sintiendo estas emociones: " + perfil.emociones + ". En las ultimas semanas ha tenido un estado anímico de " + str(perfil.estadoAnimico) + " de 10 y " + dif + ". Tiene como expectativas de conversar con este bot lo siguiente: " + perfil.expectativas + "." 

        entrada = {"messages": [{
            "role": "system",
            "content": context
        }
        ]}

        sesions = []
        query = {"AlumnoID": alumno.user_id}
        result = sesion.find(query)

        for r in result:
            sesions.append(r['SessionID'])

        sesion.delete_many(query)

        result2 = message.find()

        for m in result2:
            if m["SessionID"] in sesions:
                entrada["messages"].append({"role": m["Role"], "content": m["Content"]})

        for id in sesions:
            message.delete_many({"SessionID":id})

        response = requests.post(
            "https://ojq5bhiphe.execute-api.us-east-1.amazonaws.com/test/messages", data=json.dumps(entrada))

        response = response.json()

        if response["statusCode"] != 200:
            abort(400)

        return jsonify({
            "respuesta": response["body"],
            "statusCode": response["statusCode"]
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
    def main():
        return "Api para mensajeria"

    return app
