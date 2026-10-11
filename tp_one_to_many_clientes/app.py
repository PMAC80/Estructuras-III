from flask import render_template
from config import connex_app
from models import Customer

# Obtenemos la aplicación Flask desde Connexion
app = connex_app.app

# Le decimos a Connexion que lea el swagger.yml y arme las rutas
connex_app.add_api("swagger.yml")

# Ruta opcional para ver los datos en HTML (no es obligatoria para la API)
@app.route("/")
def home():
    customers = Customer.query.all()
    return render_template("home.html", customers=customers)

# Encender el servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)