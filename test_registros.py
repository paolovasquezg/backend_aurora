import unittest
from registros import create_app
from psql import *
from mongodb import *
from flask_cors import CORS
from flask import Flask
import json
import random
import string

class TestRegistros(unittest.TestCase):

    def setUp(self):
        self.app = create_app(db_path0)
        self.client = self.app.test_client

        letters = string.ascii_lowercase
        correo1 = ''.join(random.choice(letters) for l in range(50))
        correo2 = ''.join(random.choice(letters) for l in range(50))
        correo3 = ''.join(random.choice(letters) for l in range(50))
        correo4 = ''.join(random.choice(letters) for l in range(50))

        self.new_alumno = {"nombres": "Paolo", "apellidos": "Vasquez", "correo": correo1, "celular": "+51983108669", "password": "1234", "role": "alumno", "ciclo": "5", "carrera": "CS", "emociones": "depresion","P1": "xd1","P2": "xd2","P3": "xd3"}
        self.new_admin = {"nombres": "Paolo", "apellidos": "Vasquez", "correo": correo2, "celular": "+51983108669","password": "1234","role": "administrador", "area": "jefatura"}
        
        self.new_alumno_ex = {"nombres": "Paolo", "apellidos": "Vasquez", "correo": correo3, "celular": "+51983108669", "password": "1234", "role": "alumno", "ciclo": "5", "carrera": "CS", "emociones": "depresion","P1": "xd1","P2": "xd2","P3": "xd3"}
        self.new_admin_ex = {"nombres": "Paolo", "apellidos": "Vasquez", "correo": correo4, "celular": "+51983108669","password": "1234","role": "administrador", "area": "jefatura"}

        temp1 = self.client().post("/signup", json=self.new_alumno)
        self.alumno_id = json.loads(temp1.data)['user_id']

        temp2 = self.client().post('/signup', json = self.new_admin)
        self.admin_id = json.loads(temp2.data)['user_id']

    def test_id_by_nombre_alumno(self):
        response = self.client().get('/get_id_by_correo', json={"correo": self.new_alumno['correo']})
        data = json.loads(response.data)
        self.assertEqual(data["success"],True)
    
    def test_id_by_nombre_admin(self):
        response = self.client().get('/get_id_by_correo', json={"correo": self.new_admin['correo']})
        data = json.loads(response.data)
        self.assertEqual(data["success"],True)

    def test_id_by_correo_not_body(self):
        response = self.client().get('/get_id_by_correo', json={})
        data = response.get_json()
        self.assertEqual(data["statusCode"], 422)

    def test_id_by_correo_not_found(self):
        response = self.client().get('/get_id_by_correo', json={"correo":"pruebax"})
        data = response.get_json()
        self.assertEqual(data["statusCode"], 404)
    
    def test_signup_alumno(self):
        response = self.client().post('/signup', json=self.new_alumno_ex)
        data = response.get_json()
        self.assertEqual(data['success'],True)

    def test_signup_admin(self):
        response = self.client().post('/signup', json=self.new_alumno_ex)
        data = response.get_json()
        self.assertEqual(data['success'], True)

    def test_signup_not_body(self):
        response = self.client().post('/signup', json={"nombres": "Paolo"})
        data = response.get_json()
        self.assertEqual(data["statusCode"], 422)

    def test_login_success(self):
        response = self.client().get('/login', json={"correo": self.new_alumno["correo"], "password": self.new_alumno["password"]})
        data = response.get_json()
        self.assertEqual(data["success"], True)
    
    def test_login_not_body(self):
        response = self.client().get('/login', json={"correo": self.new_alumno["correo"], "password": "xd"})
        data = response.get_json()
        self.assertEqual(data["statusCode"], 404)

    def test_get_user_success_alumno(self):
        response = self.client().get('/get_user/'+ str(self.alumno_id))
        data = response.get_json()
        self.assertEqual(data['success'],True)
    
    def test_get_user_success_admin(self):
        response = self.client().get('/get_user/' + str(self.admin_id))
        data = response.get_json()
        self.assertEqual(data['success'], True)

    def test_get_user_fails(self):
        response = self.client().get('/get_user/0')
        data = response.get_json()
        self.assertEqual(data["statusCode"], 404)