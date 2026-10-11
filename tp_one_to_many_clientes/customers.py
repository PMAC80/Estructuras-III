from flask import abort, make_response
from config import db
from models import Customer, customer_schema, customers_schema

def read_all():
    # Le pedimos a la base de datos que nos traiga TODOS los clientes
    customers = Customer.query.all()
    # Marshmallow (customers_schema) traduce los objetos de Python a JSON
    return customers_schema.dump(customers)

def create(customer):
    # Buscamos si ya existe un cliente con ese nombre
    name = customer.get("name")
    existing_customer = Customer.query.filter(Customer.name == name).one_or_none()
    
    # Si NO existe, lo creamos
    if existing_customer is None:
        # Marshmallow (customer_schema) traduce el JSON recibido a un objeto Python
        new_customer = customer_schema.load(customer, session=db.session)
        db.session.add(new_customer)
        db.session.commit() # Guardamos los cambios en el archivo .db
        return customer_schema.dump(new_customer), 201
    else:
        # Si ya existe, abortamos con un error 406 (No Aceptable)
        abort(406, f"Customer with name {name} already exists")

def read_one(name):
    # Buscamos un cliente específico por su nombre
    customer = Customer.query.filter(Customer.name == name).one_or_none()
    if customer is not None:
        return customer_schema.dump(customer)
    else:
        abort(404, f"Customer with name {name} not found")

def delete(name):
    # Buscamos el cliente para borrarlo
    existing_customer = Customer.query.filter(Customer.name == name).one_or_none()
    if existing_customer:
        db.session.delete(existing_customer)
        db.session.commit()
        # ¡Magia del cascade! Al borrar el cliente, sus pedidos se borran solos.
        return make_response(f"{name} successfully deleted", 200)
    else:
        abort(404, f"Customer with name {name} not found")