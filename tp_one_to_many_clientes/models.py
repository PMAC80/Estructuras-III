from datetime import datetime
from config import db, ma

# ==========================================
# 1. MODELO PADRE: CUSTOMER (Cliente)
# ==========================================
class Customer(db.Model):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # RELACIÓN UNO A MUCHOS:
    # Un cliente tiene una LISTA de pedidos.
    # cascade="all, delete-orphan" asegura que si borras el cliente, se borren sus pedidos.
    orders = db.relationship(
        "Order", 
        back_populates="customer", 
        cascade="all, delete-orphan"
    )

# ==========================================
# 2. MODELO HIJO: ORDER (Pedido)
# ==========================================
class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    # CLAVE FORÁNEA: Apunta al ID de la tabla customer
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    
    # Relación inversa: Este pedido pertenece a un único cliente
    customer = db.relationship("Customer", back_populates="orders")

# ==========================================
# 3. ESQUEMAS DE MARSHMALLOW (Para convertir a JSON)
# ==========================================
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
        sqla_session = db.session

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        sqla_session = db.session
        include_relationships = True  # Incluye la lista de 'orders' al convertir a JSON
        include_fk = True

# Instancias de los esquemas
order_schema = OrderSchema()
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)