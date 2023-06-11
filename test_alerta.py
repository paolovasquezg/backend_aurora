import unittest
from alerta import create_app as app_a
from registros import create_app as app_r
from psql import *
from mongodb import *
from flask_cors import CORS
from flask import Flask
import json
import random
import string
import time


class TestMensajeria(unittest.TestCase):

    def setUp(self):
        time.sleep(7)

        self.app = app_r(db_path0)
        self.client = self.app.test_client

        letters = string.ascii_lowercase
        correo = ''.join(random.choice(letters) for l in range(50))

        new_alumno = {"nombres": "Paolo", "apellidos": "Vasquez", "correo": correo, "celular": "+51983108669", "password": "1234", "role": "alumno", "sexo": "M",
                      "ciclo": 5, "carrera": "CS", "emociones": "depresion", "asistirpsi": True, "condSM": "Depresion", "difEst": True, "expect": "mejorar", "estAni": 10}

        temp = self.client().post("/signup", json=new_alumno)
        self.alumno_id = json.loads(temp.data)['user_id']

        self.app = app_a(db_path0)
        self.client = self.app.test_client
    
    def test_send_alert_success_flag(self):
        response = self.client().post('/enviar_alerta/'+ str(self.alumno_id), json={"content": "quiero morir"})
        data = json.loads(response.data)
        self.assertEqual(data['flag'],True)
    
    def test_send_alert_success_not_flag(self):
        response = self.client().post('/enviar_alerta/'+ str(self.alumno_id), json={"content": "hola"})
        data = json.loads(response.data)
        self.assertEqual(data['flag'],False)

    def test_send_alert_invalid_user(self):
        response = self.client().post('/enviar_alerta/0', json={"content": "hola"})
        data = json.loads(response.data)
        self.assertEqual(data['statusCode'],404)
    
    def test_send_alert_no_content(self):
        response = self.client().post('/enviar_alerta/0', json={})
        data = json.loads(response.data)
        self.assertEqual(data['statusCode'],404)
    
