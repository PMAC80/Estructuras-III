from datetime import datetime
from config import db, ma

# ==========================================
# 1. MODELO PADRE: PERSON
# ==========================================
class Person(db.Model):
    __tablename__ = "person"
    id = db.Column(db.Integer, primary_key=True)
    lname = db.Column(db.String(32), unique=True)
    fname = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # RELACIÓN ONE-TO-ONE (Regla 1: uselist=False)
    # cascade="all, delete-orphan" asegura que si borras la persona, su detalle también se borre.
    detail = db.relationship(
        "PersonDetail", 
        back_populates="person", 
        uselist=False, 
        cascade="all, delete-orphan"
    )

# ==========================================
# 2. MODELO HIJO: PERSON DETAIL
# ==========================================
class PersonDetail(db.Model):
    __tablename__ = "person_detail"
    id = db.Column(db.Integer, primary_key=True)
    
    # RELACIÓN ONE-TO-ONE (Regla 2: unique=True en la ForeignKey)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"), unique=True, nullable=False)
    
    bio = db.Column(db.String(255)) 
    phone = db.Column(db.String(20)) 

    # Relación inversa
    person = db.relationship("Person", back_populates="detail")

# ==========================================
# 3. ESQUEMAS DE MARSHMALLOW (Para convertir a JSON)
# ==========================================
class PersonDetailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PersonDetail
        load_instance = True
        sqla_session = db.session

class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        load_instance = True
        sqla_session = db.session
        include_relationships = True  # Incluye el 'detail' automáticamente al convertir a JSON
        include_fk = True

# Instancias de los esquemas
person_detail_schema = PersonDetailSchema()
person_schema = PersonSchema()
people_schema = PersonSchema(many=True)