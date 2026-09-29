from config import app, db
from models import Person

with app.app_context():
    db.create_all()
    
    PEOPLE = [
        {"fname": "Tooth", "lname": "Fairy"},
        {"fname": "Knecht", "lname": "Ruprecht"},
        {"fname": "Easter", "lname": "Bunny"},
    ]

    for data in PEOPLE:
        person = Person(lname=data["lname"], fname=data["fname"])
        db.session.add(person)

    db.session.commit()