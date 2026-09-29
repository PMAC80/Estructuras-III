import os
from typing import List, Optional
from sqlalchemy import create_engine, String, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

# 1. Configuración del Motor y Base de Datos (SQLite local)
DATABASE_URL = "sqlite:///blog.db"
engine = create_engine(DATABASE_URL, echo=False) # echo=False para no llenar la consola
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 2. Definición del Modelo Base
class Base(DeclarativeBase):
    pass

# 3. Modelo Padre: Usuario (User)
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relación Uno a Muchos: Un usuario tiene una lista de Posts
    # back_populates conecta esto con el atributo 'author' de la clase Post
    # cascade="all, delete-orphan" es clave: si borro al usuario, se borran sus posts.
    posts: Mapped[List["Post"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"

# 4. Modelo Hijo: Artículo (Post)
class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    # Clave Foránea (Foreign Key): Apunta al ID de la tabla de usuarios
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relación Inversa: Cada post pertenece a un único autor
    author: Mapped["User"] = relationship(back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post(id={self.id}, title='{self.title}', user_id={self.user_id})>"

# 5. Ejecución del Script y Pruebas Relacionales
def main():
    # Crear las tablas en la base de datos
    Base.metadata.create_all(bind=engine)
    
    with SessionLocal() as session:
        print("\n--- 1. CREAR REGISTROS CON RELACIÓN ---")
        # Creamos el usuario
        autor = User(username="carlos_dev", email="carlos@example.com")
        
        # Creamos los posts
        post1 = Post(title="Intro a SQLAlchemy 2.0", content="Contenido del post 1...")
        post2 = Post(title="Relaciones Avanzadas", content="Contenido del post 2...")
        
        # Asignamos los posts al autor (SQLAlchemy se encarga de los IDs y las claves foráneas)
        autor.posts.extend([post1, post2])
        
        # Al guardar al autor, SQLAlchemy guarda los posts en cascada
        session.add(autor)
        session.commit()
        print(f"Usuario creado con {len(autor.posts)} posts asociados.")

        print("\n--- 2. LEER DATOS RELACIONADOS ---")
        # Consultamos el usuario
        stmt = select(User).where(User.username == "carlos_dev")
        usuario_db = session.scalars(stmt).first()
        
        if usuario_db:
            print(f"Autor: {usuario_db.username}")
            # Accedemos a la relación de manera perezosa (Lazy Loading)
            for post in usuario_db.posts:
                print(f"-> Post: '{post.title}' (Escrito por user_id: {post.user_id})")

        print("\n--- 3. ELIMINAR EN CASCADA ---")
        # Al tener configurado cascade="all, delete-orphan", si borramos al usuario,
        # se borrarán automáticamente todos sus posts de la base de datos.
        if usuario_db:
            session.delete(usuario_db)
            session.commit()
            print("Usuario y todos sus posts asociados han sido eliminados automáticamente.")

if __name__ == "__main__":
    main()