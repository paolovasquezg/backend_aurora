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


def create_app(db_path=db_path):
    app = Flask(__name__)
    with app.app_context():
        setup_psql(app,db_path)
    CORS(app, origins='*')
    load_dotenv()
    API_KEY = os.getenv('PUSH_KEY')

    @app.route("/enviar_alerta/<user_id>", methods=["POST"])
    def send_alert(user_id):
        time.sleep(5)

        user = Usuario.query.filter(Usuario.user_id == user_id).one_or_none()
        
        if user is None:
            abort(404)

        body = request.get_json()

        enviado = body.get("content", None)

        if enviado is None:
            abort(422)

        perfil = Perfil.query.filter(Perfil.user_id == user_id).one_or_none()
        alumno = Alumno.query.filter(Alumno.user_id == user_id).one_or_none()

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
        

        nombres = user.nombres
        apellidos = user.apellidos
        email = user.correo
        celular = user.celular

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
            abort(400)

        if response["flag"] == True:
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

            alert = "El usuario " + nombres + " " + apellidos + " envio " + "'" + enviado + "' el " + \
                    date_time + ". Porfavor contactarse a " + email + " o " + celular + ". Dicho usuario ha sido diagnosticado con: " + perfil.condicionSM + "; y últimamente ha estado sintiendo estas emociones: " + perfil.emociones + "."

            pb = PushBullet(API_KEY)
            push = pb.push_note('ALERTA', alert)

        return jsonify({
            "enviado": enviado,
            "flag": response['flag'],
            "statusCode": response['statusCode']
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
        return "api de alerta"

    return app
