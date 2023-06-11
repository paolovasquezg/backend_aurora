from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


db_name = os.getenv('PSQL_DATABASE')
db_name2 = os.getenv('PSQL_DATABASE2')
password = os.getenv('PSQL_PASSWORD')
host = os.getenv('PSQL_HOST')
user = os.getenv('PSQL_USER')
port = 5432
db_path = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
db_path0 = f'postgresql://{user}:{password}@{host}:{port}/{db_name2}'

db = SQLAlchemy()

def setup_psql(app, database_path=db_path):
    app.config['SQLALCHEMY_DATABASE_URI']=database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    db.app = app
    db.init_app(app)
    db.create_all()
    
class Usuario(db.Model):
    __tablenamme__= 'usuario'
    user_id = db.Column(db.Integer, primary_key = True, nullable=True)
    nombres = db.Column(db.String(200), nullable=False)
    apellidos = db.Column(db.String(200), nullable=False)
    correo = db.Column(db.String(200), nullable=False, unique =True)
    celular = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    admins = db.relationship('Administrador', backref = 'admin', lazy=True, cascade='all, delete-orphan')
    alumnos = db.relationship('Alumno', backref='alumni', lazy=True, cascade="all, delete-orphan")

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.user_id
        except Exception as e:
            db.session.rollback()
            print(e)
        finally:
            db.session.close()

    def update(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

    def __repr__(self):
        return f"User('{self.user_id}', \nNombres:'{self.nombres}', \nApellidos:'{self.apellidos}', \nCorreo:'{self.correo}', \nCelular:'{self.celular}', \nPassword:'{self.password}')"

    def format(self):
        return{
            "userid": self.user_id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "correo": self.correo,
            "celular": self.celular,
            "password": self.password
        }


class Administrador(db.Model):
    __tablenamme__ = 'administrador'
    user_id = db.Column(db.Integer, db.ForeignKey("usuario.user_id"),primary_key=True, nullable = False)
    area = db.Column(db.String(200), nullable = False)

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.user_id
        except Exception as e:
            db.session.rollback()
            print(e)
        finally:
            db.session.close()

    def update(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

    def __repr__(self):
        return f"Administrador('{self.user_id}', '{self.area}')"

    def format(self):
        return{
            "user_id": self.user_id,
            "rol": "administrador",
            "area": self.area
        }

class Alumno(db.Model):
    __tablename__ = "alumno"
    user_id = db.Column(db.Integer, db.ForeignKey("usuario.user_id"),primary_key=True, nullable = False)
    sexo = db.Column(db.String(1), nullable = False)
    ciclo = db.Column(db.Integer, nullable = False)
    carrera = db.Column(db.String(200), nullable=False)
    perfil = db.relationship('Perfil', backref='usuario',lazy=True,cascade= "all, delete-orphan")

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.user_id
        except Exception as e:
            db.session.rollback()
            print(e)
        finally:
            db.session.close()

    def update(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
    
    def __repr__(self):
        return f"Alumno('{self.user_id}', '{self.sexo}','{self.ciclo}', '{self.carrera}')"

    def format(self):
        return {
            "user_id":self.user_id,
            "rol": "alumno",
            "sexo": self.sexo,
            "ciclo": self.ciclo,
            "carrera":self.carrera
        }

class Perfil(db.Model):
    __tablename__ = 'perfil'
    form_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("alumno.user_id"), primary_key=False)
    emociones = db.Column(db.String(200), nullable=False)
    asistirpsicologo = db.Column(db.Boolean, nullable = False)
    condicionSM = db.Column(db.String(200), nullable = False)
    difEst = db.Column(db.Boolean, nullable = False)
    expectativas = db.Column(db.String(200), nullable = False)
    estadoAnimico = db.Column(db.Integer, nullable = False)

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.form_id
        except Exception as e:
            db.session.rollback()
            print(e)
        finally:
            db.session.close()

    def update(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
        # finally:
        #     db.session.close()

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

    def __repr__(self):
        return f"Perfil('{self.form_id}', \nUser:'{self.user_id}', \nEmociones:'{self.emociones}', \nAsistirPsicologo:'{self.asistirpsicologo}', \nCondicionSM:'{self.condicionSM}', \nDifEst:'{self.difEst}', \nExpectativas:'{self.expectativas}', \nEstadoAnimico:'{self.estadoAnimico}')"
    
    def format(self):
        return {
            "form_id": self.form_id,
            "user_id": self.user_id,
            "emociones": self.emociones,
            "AsistirPsicologo": self.asistirpsicologo,
            "CondicionSM": self.condicionSM,
            "DifEst": self.difEst,
            "Expectativas": self.expectativas,
            "EstadoAnimico": self.expectativas
        }

