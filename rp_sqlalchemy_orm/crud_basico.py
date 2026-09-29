import os
from typing import Optional
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# 1. CONFIGURACIÓN DEL MOTOR (ENGINE)
# Le decimos a SQLAlchemy que use SQLite y guarde los datos en el archivo 'usuarios.db'
DATABASE_URL = "sqlite:///usuarios.db"
engine = create_engine(DATABASE_URL, echo=False) # echo=False para no llenar la pantalla de SQL

# 2. CREACIÓN DE LA SESIÓN
# La sesión es como nuestra "mesa de trabajo" temporal antes de guardar los cambios en la BD
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 3. DEFINICIÓN DEL MODELO BASE
class Base(DeclarativeBase):
    pass

# 4. DEFINICIÓN DE LA CLASE/TABLA 'USER'
class User(Base):
    __tablename__ = "users"
    
    # Definimos las columnas usando la sintaxis moderna Mapped
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(nullable=True) # Optional permite que sea NULL

    # Método para que al imprimir el usuario se vea bonito en la consola
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

# 5. EJECUCIÓN DEL CRUD (Crear, Leer, Actualizar, Borrar)
def main():
    # Creamos las tablas en la base de datos física si no existen
    Base.metadata.create_all(bind=engine)
    
    # Abrimos una sesión limpia para trabajar
    with SessionLocal() as session:
        
        print("\n--- 1. CREAR (Insertar registros) ---")
        user1 = User(username="juan_perez", email="juan@example.com", age=30)
        user2 = User(username="ana_gomez", email="ana@example.com", age=25)
        session.add_all([user1, user2])
        session.commit() # Guarda los cambios permanentemente en usuarios.db
        print(f"Usuarios creados: {user1}, {user2}")

        print("\n--- 2. LEER (Consultar registros) ---")
        # Obtener todos los usuarios
        query_all = select(User)
        users = session.scalars(query_all).all()
        print(f"Todos los usuarios: {users}")
        
        # Filtrar un usuario por una condición específica
        query_filter = select(User).where(User.username == "juan_perez")
        juan = session.scalars(query_filter).first()
        print(f"Usuario filtrado: {juan}")

        print("\n--- 3. ACTUALIZAR (Modificar registros) ---")
        if juan:
            juan.age = 31 # Modificamos el atributo directamente en Python
            session.commit() # Sincroniza el cambio con la base de datos
            print(f"Usuario actualizado: {juan} con edad {juan.age}")

        print("\n--- 4. ELIMINAR (Borrar registros) ---")
        query_delete = select(User).where(User.username == "ana_gomez")
        ana = session.scalars(query_delete).first()
        if ana:
            session.delete(ana) # Marcamos el objeto para eliminación
            session.commit() # Aplicamos el borrado
            print("Usuario 'ana_gomez' eliminado con éxito.")

        # Verificación final
        todos_restantes = session.scalars(select(User)).all()
        print(f"\nUsuarios restantes en BD: {todos_restantes}")

if __name__ == "__main__":
    main()