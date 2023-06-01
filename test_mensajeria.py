import unittest
from mensajeria import create_app as app_m
from registros import create_app as app_r
from psql import *
from mongodb import *
from flask_cors import CORS
from flask import Flask
import json
import random
import string

class TestMensajeria(unittest.TestCase):
    
    def setUp(self):
        self.app = app_r(db_path0)
        self.client = self.app.test_client

        letters = string.ascii_lowercase
        correo = ''.join(random.choice(letters) for l in range(50))
        self.sessionid = ''.join(random.choice(letters) for l in range(50))

        new_alumno = {"nombres": "Paolo", "apellidos": "Vasquez", "correo": correo, "celular": "+51983108669", "password": "1234", "role": "alumno", "ciclo": "5", "carrera": "CS", "emociones": "depresion","P1": "xd1","P2": "xd2","P3": "xd3"}
      
        temp = self.client().post("/signup", json=new_alumno)
        self.alumno_id = json.loads(temp.data)['user_id']

        self.app = app_m(db_path0)
        self.client = self.app.test_client

    def test_send_receive_success(self):
        response = self.client().post('/enviar_recibir/'+ str(self.alumno_id), json={"content": "hola", "sesionid": self.sessionid})
        data = json.loads(response.data)
        self.client().get('/enviar_contexto/'+str(self.alumno_id))
        self.assertEqual(data["enviado"],"hola")
    
    def test_send_receive_invalid_user(self):
         response = self.client().post('/enviar_recibir/0', json={"content": "hola", "sesionid": self.sessionid})
         data = json.loads(response.data)
         self.assertEqual(data["statusCode"], 422)

    def test_send_receive_invalid_body(self):
        response = self.client().post('/enviar_recibir/'+ str(self.alumno_id), json={"content": "hola"})
        data = json.loads(response.data)
        self.assertEqual(data["statusCode"], 422)

    def test_send_context_success(self):
        response = self.client().get('/enviar_contexto/'+ str(self.alumno_id))
        data = json.loads(response.data)
        self.assertEqual(data["statusCode"], 200)

    def test_send_context_invalid_user(self):
        response = self.client().get('/enviar_contexto/0')
        data = json.loads(response.data)
        self.assertEqual(data["statusCode"], 404)
    
