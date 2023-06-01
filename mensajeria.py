from flask import Flask, request, jsonify, abort
import datetime
from flask_cors import CORS
from psql import *
from mongodb import *
import json
import requests

app = Flask(__name__)

with app.app_context():
    setup_psql(app)

CORS(app, origins='*')

@app.route("/enviar_recibir/<user_id>", methods = ["POST"])
def send_receive(user_id):
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    body = request.get_json()

    alumno = Alumno.query.filter(Alumno.id == user_id).one_or_none()

    enviado = body.get("content", None)
    sesionid = body.get("sesionid", None)

    if alumno is None or enviado is None or sesionid is None:
        abort(422)

    result = sesion.find({"SessionID": sesionid})
    result = list(result)

    if len(result) == 0:
        sesion.insert_one({"SessionID": sesionid, "AlumnoID": alumno.id,
                        "Start": date_time, "Context": "Eres un bot de salud mental."})
    
    message.insert_one({"SessionID": sesionid, "Role": "user", "Content": enviado})

    entrada = {"messages": [
        {
            "role": "system",
            "content": "Eres un bot de salud mental."
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
    alumno = Alumno.query.filter(Alumno.id == user_id).one_or_none()

    if alumno is None:
        abort(404)

    entrada = {"messages": [{
        "role": "system",
        "content": "Eres un bot de salud mental."
    }
    ]}

    sesions = []
    query = {"AlumnoID": alumno.id}
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
        'code': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'code': 500,
        'message': 'Internal Server error'
    }), 500


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'code': 422,
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)
