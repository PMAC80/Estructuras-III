from config import app, db
from models import Customer, Order

# Necesitamos el contexto de la aplicación para poder hablar con la base de datos
with app.app_context():
    # 1. Crear las tablas físicas en el archivo customers.db
    db.create_all()
    
    # 2. Datos de prueba (Clientes y sus Pedidos)
    CUSTOMERS_DATA = [
        {
            "name": "Juan Perez",
            "email": "juan@example.com",
            "orders": [
                {"order_number": "ORD-001", "amount": 150.50},
                {"order_number": "ORD-002", "amount": 89.99}
            ]
        },
        {
            "name": "Maria Gomez",
            "email": "maria@example.com",
            "orders": [
                {"order_number": "ORD-003", "amount": 250.00}
            ]
        },
        {
            "name": "Carlos Lopez",
            "email": "carlos@example.com",
            "orders": [] # Este cliente no tiene pedidos aún
        }
    ]

    # 3. Recorrer los datos y guardarlos
    for data in CUSTOMERS_DATA:
        # Creamos el objeto Cliente
        new_customer = Customer(name=data["name"], email=data["email"])
        
        # Creamos los objetos Pedido y los "atachamos" al cliente
        for order_data in data["orders"]:
            new_order = Order(
                order_number=order_data["order_number"],
                amount=order_data["amount"]
            )
            # ¡Magia de la relación 1:N! Agregamos el pedido a la lista del cliente
            new_customer.orders.append(new_order)
        
        # Agregamos el cliente (y sus pedidos en cascada) a la sesión
        db.session.add(new_customer)

    # 4. Guardar todos los cambios en el archivo físico
    db.session.commit()
    print("✅ Base de datos 'customers.db' creada y cargada con éxito.")