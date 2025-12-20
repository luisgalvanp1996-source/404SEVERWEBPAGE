from sqlalchemy import Column, Integer, ForeignKey, NVARCHAR, Text
from sqlalchemy.orm import relationship
from .connection import Base
from .models_catalogos import CatTipos, CatModulos, CatArchivoTipo


# ============================================
# CATALOGO DE LIBROS DE LA BIBLIA
# ============================================
class CatLibrosBiblia(Base):
    __tablename__ = "CAT_LIBROS_BIBLIA"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    libro = Column("LIBRO", Integer)
    nombre = Column("NOMBRE", NVARCHAR(50))
    abreviatura = Column("ABREVIATURA", NVARCHAR(10))
    capitulos = Column("CAPITULOS", Integer)

    # Relaciones
  


# ============================================
# TABLA DAT_APRENDIZAJE_BIBLIA
# ============================================
class DatAprendizajeBiblia(Base):
    __tablename__ = "DAT_APRENDIZAJE_BIBLIA"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    tipo_id = Column("TIPO_ID", Integer, ForeignKey("CAT_TIPOS.ID"))
    libro_id = Column("LIBRO_ID", Integer, ForeignKey("CAT_LIBROS_BIBLIA.ID"))
    capitulo = Column("CAPITULO", Integer)
    versiculo_inicio = Column("VERSICULO_INICIO", Integer)
    versiculo_fin = Column("VERSICULO_FIN", Integer)
    modulo_id = Column("MODULO", Integer, ForeignKey("CAT_MODULOS.ID"))
    texto = Column("TEXTO", NVARCHAR)

    # Relaciones



# ============================================
# TABLA DAT_ARCHIVOS_BIBLIA
# ============================================
class DatArchivosBiblia(Base):
    __tablename__ = "DAT_ARCHIVOS_BIBLIA"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    movimiento_id = Column("MOVIMIENTO", Integer, ForeignKey("DAT_APRENDIZAJE_BIBLIA.ID"))
    archivo_id = Column("ARCHIVO", Integer, ForeignKey("CAT_ARCHIVO_TIPO.ID"))
    ubicacion = Column("UBICACION", NVARCHAR(100))

    # Relaciones
 


# ============================================
# TABLA BIBLIA
# ============================================
class Biblia(Base):
    __tablename__ = "BIBLIA"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    libro = Column("LIBRO", NVARCHAR(50))
    capitulo = Column("CAPITULO", Integer)
    versiculo = Column("VERSICULO", Integer)
    texto = Column("TEXTO", NVARCHAR)
    libronumero = Column("LibroNum", Integer, ForeignKey("CAT_LIBROS_BIBLIA.ID"))

    # Relación hacia el catálogo
  
class CatTagsTipoBiblia(Base):
    __tablename__ = "CAT_TAGS_TIPO_BIBLIA"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    tipo_tag = Column("TIPO_TAG", Integer)

class CatTagsBiblia(Base):
    __tablename__ = "CAT_TAGS_BIBLIA"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    tipo_tag_id = Column("TIPO_TAG_ID",Integer,ForeignKey("CAT_TAGS_TIPO_BIBLIA.ID"))
    tag = Column("TAG", NVARCHAR)

class DatTagsBiblia(Base):
    __tablename__ = "DAT_TAGS_BIBLIA"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    libro_id = Column("LIBRO_ID",Integer,ForeignKey("CAT_LIBROS_BIBLIA.ID"))
    versiculo = Column("VERSICULO", Integer)
    tag_tipo_id = Column("TAG_TIPO_ID",Integer,ForeignKey("CAT_TAGS_TIPO_BIBLIA.ID"))
    tag_id = Column("TAG_ID",Integer,ForeignKey("CAT_TAGS_BIBLIA.ID"))
