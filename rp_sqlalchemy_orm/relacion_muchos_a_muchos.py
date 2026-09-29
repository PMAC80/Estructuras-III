import os
from typing import List
from sqlalchemy import create_engine, String, ForeignKey, Table, Column, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

# 1. Configuración del Motor y Base de Datos (SQLite local)
DATABASE_URL = "sqlite:///blog_tags.db"
engine = create_engine(DATABASE_URL, echo=False) # echo=False para no llenar la consola
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 2. Definición del Modelo Base
class Base(DeclarativeBase):
    pass

# 3. Tabla de Asociación (El "Puente")
# Es una tabla pura que mapea las claves primarias de ambas entidades.
# No necesita una clase completa porque solo almacena los IDs.
post_tag_association = Table(
    "post_tag",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

# 4. Modelo: Artículo (Post)
class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relación Muchos a Muchos hacia Tag
    # 'secondary' especifica la tabla intermedia que conecta ambos modelos
    tags: Mapped[List["Tag"]] = relationship(
        secondary=post_tag_association, back_populates="posts"
    )

    def __repr__(self) -> str:
        return f"<Post(id={self.id}, title='{self.title}')>"

# 5. Modelo: Etiqueta (Tag)
class Tag(Base):
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    
    # Relación Inversa Muchos a Muchos hacia Post
    posts: Mapped[List["Post"]] = relationship(
        secondary=post_tag_association, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"

# 6. Ejecución del Script y Pruebas Relacionales
def main():
    # Crear todas las tablas (incluyendo la tabla de asociación automáticamente)
    Base.metadata.create_all(bind=engine)
    
    with SessionLocal() as session:
        print("\n--- 1. CREAR REGISTROS Y ASOCIACIONES ---")
        # Instanciamos las etiquetas
        tag_python = Tag(name="Python")
        tag_db = Tag(name="Bases de Datos")
        tag_web = Tag(name="Desarrollo Web")
        
        # Instanciamos los posts
        post1 = Post(title="Tutorial de SQLAlchemy 2.0")
        post2 = Post(title="Cómo usar FastAPI con PostgreSQL")
        
        # Asignamos las relaciones cruzadas usando listas normales de Python
        post1.tags.extend([tag_python, tag_db]) # Post 1 tiene Python y BD
        post2.tags.extend([tag_python, tag_web]) # Post 2 tiene Python y Web
        
        # Guardamos todo en la base de datos
        session.add_all([post1, post2])
        session.commit()
        print("Posts y etiquetas creados con sus respectivas relaciones.")

        print("\n--- 2. LEER RELACIONES DESDE EL PADRE (Post -> Tags) ---")
        # Consultamos un post específico
        stmt_post = select(Post).where(Post.title == "Tutorial de SQLAlchemy 2.0")
        p1 = session.scalars(stmt_post).first()
        
        if p1:
            # Obtenemos las etiquetas asociadas a este post
            nombres_etiquetas = [t.name for t in p1.tags]
            print(f"El post '{p1.title}' tiene las etiquetas: {nombres_etiquetas}")

        print("\n--- 3. LEER RELACIONES DESDE EL HIJO (Tag -> Posts) ---")
        # Consultamos una etiqueta específica para ver qué posts la comparten
        stmt_tag = select(Tag).where(Tag.name == "Python")
        t_python = session.scalars(stmt_tag).first()
        
        if t_python:
            # Obtenemos los posts que usan la etiqueta 'Python'
            titulos_posts = [p.title for p in t_python.posts]
            print(f"La etiqueta '{t_python.name}' está presente en: {titulos_posts}")

        print("\n--- 4. ELIMINAR UNA ASOCIACIÓN ---")
        # Quitamos la etiqueta 'Bases de Datos' únicamente del Post 1
        if p1 and tag_db in p1.tags:
            p1.tags.remove(tag_db) # SQLAlchemy borra solo la fila de la tabla intermedia
            session.commit()
            print(f"Etiqueta '{tag_db.name}' removida del post '{p1.title}'.")
            print(f"Etiquetas restantes del post: {[t.name for t in p1.tags]}")

if __name__ == "__main__":
    main()