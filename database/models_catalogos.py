from sqlalchemy import Column, Integer, String, Text, ForeignKey, NVARCHAR, DateTime
from sqlalchemy.orm import relationship
from .connection import Base
from .models_biblia import *

class CatModulos(Base):
    __tablename__ = "CAT_MODULOS"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    modulo = Column("MODULO", NVARCHAR(100))

    


class CatArchivoTipo(Base):
    __tablename__ = "CAT_ARCHIVO_TIPO"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    tipo_archivo = Column("TIPO_ARCHIVO", NVARCHAR(100))

  

class CatTipos(Base):
    __tablename__ = "CAT_TIPOS"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    tipo = Column("TIPO", NVARCHAR(100), nullable=True)
    categoria = Column("CATEGORIA", Integer, ForeignKey("CAT_CAT.ID"), nullable=True )  

