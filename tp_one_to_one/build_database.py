from config import app, db
from models import Person, PersonDetail

with app.app_context():
    # Crea las tablas en la base de datos
    db.create_all()
    
    # Datos de ejemplo con su detalle Uno a Uno
    PEOPLE_DATA = [
        {
            "fname": "Tooth", 
            "lname": "Fairy",
            "detail": {"bio": "Deja monedas bajo las almohadas", "phone": "555-0101"}
        },
        {
            "fname": "Knecht", 
            "lname": "Ruprecht",
            "detail": {"bio": "Compañero de Santa Claus", "phone": "555-0202"}
        },
        {
            "fname": "Easter", 
            "lname": "Bunny",
            "detail": {"bio": "Experto en esconder huevos de chocolate", "phone": "555-0303"}
        }
    ]

    for data in PEOPLE_DATA:
        # Usamos el esquema para cargar los datos anidados correctamente
        new_person = Person(
            lname=data["lname"], 
            fname=data["fname"],
            detail=PersonDetail(bio=data["detail"]["bio"], phone=data["detail"]["phone"])
        )
        db.session.add(new_person)

    db.session.commit()
    print("Base de datos 'people.db' creada y cargada con éxito.")