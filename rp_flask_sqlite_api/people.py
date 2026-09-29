from flask import abort, make_response
from config import db
from models import Person

def read_all():
    people = Person.query.all()
    return [
        {"fname": p.fname, "lname": p.lname, "timestamp": p.timestamp}
        for p in people
    ]

def read_one(lname):
    person = Person.query.filter(Person.lname == lname).one_or_none()
    if person is not None:
        return {"fname": person.fname, "lname": person.lname, "timestamp": person.timestamp}
    else:
        abort(404, f"Person with last name {lname} not found")

def create(person):
    lname = person.get("lname")
    fname = person.get("fname", "")
    existing = Person.query.filter(Person.lname == lname).one_or_none()
    if existing is None:
        new_person = Person(lname=lname, fname=fname)
        db.session.add(new_person)
        db.session.commit()
        return {"fname": new_person.fname, "lname": new_person.lname, "timestamp": new_person.timestamp}, 201
    else:
        abort(406, f"Person with last name {lname} already exists")

def update(lname, person):
    existing = Person.query.filter(Person.lname == lname).one_or_none()
    if existing is not None:
        existing.fname = person.get("fname", existing.fname)
        db.session.commit()
        return {"fname": existing.fname, "lname": existing.lname, "timestamp": existing.timestamp}
    else:
        abort(404, f"Person with last name {lname} not found")

def delete(lname):
    existing = Person.query.filter(Person.lname == lname).one_or_none()
    if existing is not None:
        db.session.delete(existing)
        db.session.commit()
        return make_response(f"{lname} successfully deleted", 200)
    else:
        abort(404, f"Person with last name {lname} not found")