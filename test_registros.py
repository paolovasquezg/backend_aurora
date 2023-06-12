import unittest
from registros import create_app
from psql import *
from mongodb import *
from flask_cors import CORS
from flask import Flask
import json
import random
import string
import time

class TestRegistros(unittest.TestCase):

    def setUp(self):
        time.sleep(2)
        self.app = create_app(db_path0)
        self.client = self.app.test_client

        self.letters = string.ascii_lowercase
        correo1 = ''.join(random.choice(self.letters) for l in range(50))
        correo2 = ''.join(random.choice(self.letters) for l in range(50))

        self.new_alumno = {"nombres": "Paolo", "apellidos": "Vasquez", "correo": correo1, "celular": "+51983108669", "password": "1234", "role": "alumno", "sexo": "M", "ciclo": 5, "carrera": "CS", "emociones": "depresion","asistirpsi": True, "condSM": "Depresion","difEst": True, "expect": "mejorar", "estAni": 10}
        self.new_admin = {"nombres": "Paolo", "apellidos": "Vasquez", "correo": correo2, "celular": "+51983108669","password": "1234","role": "administrador", "area": "jefatura"}
        
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
        correo = ''.join(random.choice(self.letters) for l in range(50))
        alumno = {"nombres": "Paolo", "apellidos": "Vasquez", "correo": correo, "celular": "+51983108669", "password": "1234", "role": "alumno", "sexo": "M", "ciclo": 5, "carrera": "CS", "emociones": "depresion","asistirpsi": True, "condSM": "Depresion","difEst": True, "expect": "mejorar", "estAni": 10}
        response = self.client().post('/signup', json=alumno)
        data = response.get_json()
        self.assertEqual(data['success'],True)

    def test_signup_admin(self):
        correo = ''.join(random.choice(self.letters) for l in range(50))
        admin = {"nombres": "Paolo", "apellidos": "Vasquez", "correo": correo, "celular": "+51983108669","password": "1234","role": "administrador", "area": "jefatura"}
        response = self.client().post('/signup', json=admin)
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
    
    def test_update_user_success_alumno(self):
        correo = ''.join(random.choice(self.letters) for l in range(50))
        response = self.client().patch('/update_user/'+str(self.alumno_id), json={"correo":correo,"ciclo":"5"})
        data = response.get_json()
        self.assertEqual(data['success'], True)

    def test_update_user_success_admin(self):
        correo = ''.join(random.choice(self.letters) for l in range(50))
        response = self.client().patch('/update_user/'+str(self.admin_id), json={"correo":correo,"area":"recursos humanos"})
        data = response.get_json()
        self.assertEqual(data['success'], True)
    
    def test_update_user_invalid_user(self):
        correo = ''.join(random.choice(self.letters) for l in range(50))
        response = self.client().patch('/update_user/0', json={"correo":correo,"area":"recursos humanos"})
        data = response.get_json()
        self.assertEqual(data['statusCode'], 404)
    
    def test_update_user_not_body(self):
        response = self.client().patch('/update_user/'+str(self.admin_id), json={})
        data = response.get_json()
        self.assertEqual(data['statusCode'], 422)

    def test_update_user_existing_email(self):
        response = self.client().patch('/update_user/'+str(self.admin_id), json={"correo":self.new_alumno['correo']})
        data = response.get_json()
        self.assertEqual(data['statusCode'], 422)

    def test_update_user_existing_body_incomplete_alumno(self):
        response = self.client().patch('/update_user/'+str(self.admin_id), json={"correo":""})
        data = response.get_json()
        self.assertEqual(data['statusCode'], 422)

    def test_update_user_existing_body_incomplete_admin(self):
        response = self.client().patch('/update_user/'+str(self.admin_id), json={"area":""})
        data = response.get_json()
        self.assertEqual(data['statusCode'], 422)

    def test_delete_user_success_alumno(self):
        response = self.client().delete('/delete_user/'+str(self.alumno_id))
        data = response.get_json()
        self.assertEqual(data['success'], True)
    
    def test_delete_user_success_admin(self):
        response = self.client().delete('/delete_user/'+str(self.admin_id))
        data = response.get_json()
        self.assertEqual(data['success'], True)

    def test_delete_user_invalid_user(self):
        response = self.client().delete('/delete_user/0')
        data = response.get_json()
        self.assertEqual(data['statusCode'], 404)

    def test_get_perfil_success(self):
        response = self.client().get('/get_perfil/'+str(self.alumno_id))
        data = response.get_json()
        self.assertEqual(data['success'], True)
    
    def test_get_perfil_invalid_user(self):
        response = self.client().get('/get_perfil/0')
        data = response.get_json()
        self.assertEqual(data['statusCode'], 404)

    def test_update_perfil_sucess(self):
        response = self.client().patch('/update_perfil/'+str(self.alumno_id), json = {"emociones": "felicidad"})
        data = response.get_json()
        self.assertEqual(data['success'], True)

    def test_update_perfil_invalid_user(self):
        response = self.client().patch('/update_perfil/0', json = {"emociones": "felicidad"})
        data = response.get_json()
        self.assertEqual(data['statusCode'], 404)
    
    def test_update_perfil_not_body(self):
        response = self.client().patch('/update_perfil/'+str(self.alumno_id), json = {})
        data = response.get_json()
        self.assertEqual(data['statusCode'], 422)

    def test_update_perfil_invalid_body(self):
        response = self.client().patch('/update_perfil/'+str(self.alumno_id), json={"emociones":""})
        data = response.get_json()
        self.assertEqual(data['statusCode'], 422)
