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
    id = db.Column(db.Integer, primary_key = True, nullable=True)
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
            return self.id
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
        return f"User('{self.userid}', \nNombres:'{self.nombres}', \nApellidos:'{self.apellidos}', \nCorreo:'{self.correo}', \nCelular:'{self.celular}', \nPassword:'{self.password}')"

    def format(self):
        return{
            "userid": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "correo": self.correo,
            "celular": self.celular,
            "password": self.password
        }


class Administrador(db.Model):
    __tablenamme__ = 'administrador'
    id = db.Column(db.Integer, db.ForeignKey("usuario.id"),primary_key=True, nullable = False)
    area = db.Column(db.String(200), nullable = False)

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.id
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
        return f"Administrador('{self.id}', '{self.area}')"

    def format(self):
        return{
            "userid": self.id,
            "rol": "administrador",
            "area": self.area
        }

class Alumno(db.Model):
    __tablename__ = "alumno"
    id = db.Column(db.Integer, db.ForeignKey("usuario.id"),primary_key=True, nullable = False)
    ciclo = db.Column(db.Integer, nullable = False)
    carrera = db.Column(db.String(200), nullable=False)
    perfil = db.relationship('Perfil', backref='usuario',lazy=True,cascade= "all, delete-orphan")

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.id
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
        return f"Alumno('{self.id}', '{self.ciclo}', '{self.carrera}')"

    def format(self):
        return {
            "userid":self.id,
            "rol": "alumno",
            "ciclo": self.ciclo,
            "carrera":self.carrera
        }

class Perfil(db.Model):
    __tablename__ = 'perfil'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey("alumno.id"), primary_key=False)
    emociones = db.Column(db.String(200), nullable=False)
    P1 = db.Column(db.String(200), nullable=False)
    P2 = db.Column(db.String(200), nullable=False)
    P3 = db.Column(db.String(200), nullable=False)

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.id
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
        return f"Perfil('{self.id}', \nUser:'{self.userid}', \nEmociones:'{self.emociones}', \nP1:'{self.P1}', \nP2:'{self.P2}', \nP3:'{self.P3}')"
    
    def format(self):
        return {
            "perfilid": self.id,
            "userid": self.userid,
            "emociones": self.emociones,
            "P1": self.P1,
            "P2": self.P2,
            "P3": self.P3
        }

