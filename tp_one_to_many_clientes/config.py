import pathlib
import connexion
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

# Obtiene la ruta de la carpeta actual
basedir = pathlib.Path(__file__).parent.resolve()

# Crea la aplicación usando Connexion
connex_app = connexion.App(__name__, specification_dir=basedir)
app = connex_app.app

# Configuración de la base de datos SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{basedir / 'customers.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializa las extensiones
db = SQLAlchemy(app)
ma = Marshmallow(app)