from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from pushbullet import PushBullet
import json
import requests
import smtplib
import time
import datetime
from psql import *
from mongodb import *
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

with app.app_context():
    setup_psql(app)

CORS(app, origins='*')

API_KEY = os.getenv('PUSH_KEY')

@app.route("/enviar_alerta/<user_id>", methods=["POST"])
def send_alert(user_id):

    try:
        user = Usuario.query.filter(Usuario.id == user_id).one_or_none()
        
        if user is None:
            abort(404)

        body = request.get_json()

        enviado = body.get("content", None)

        if enviado is None:
            abort(422)

        nombres = user.nombres
        apellidos = user.apellidos
        email = user.correo
        celular = user.celular

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
            abort(400)

        if response["flag"] == True:
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

            alert = "El usuario " + nombres + " " + apellidos + " envio " + "'" + enviado + "' el " + \
                    date_time + ". Porfavor contactarse a " + email + " o " + celular + "."

            pb = PushBullet(API_KEY)
            push = pb.push_note('ALERTA', alert)

        return jsonify({
            "enviado": enviado,
            "flag": response['flag'],
            "statusCode": response['statusCode']
        })
    except:
        abort(400)

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
    return "api de alerta"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=False)
