from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, NVARCHAR,Date,Time
from sqlalchemy.orm import relationship
from .connection import Base






class DatEventosPersonal(Base):
    __tablename__ = "DAT_EVENTOS_PERSONAL"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    TIPO_ID = Column(Integer)
    MODULO_ID = Column(Integer)
    LUGAR = Column(String(100))
    FECHA = Column(Date)
    HORA = Column(Time)
    DESCRIPCION = Column(Text)
    OBSERVACIONES = Column(Text)


class DatDetallesEventosPersonal(Base):
    __tablename__ = "DAT_DETALLES_EVENTOS_PERSONAL"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    EVENTO_ID = Column(Integer, ForeignKey("DAT_EVENTOS_PERSONAL.ID"))
    TITULO = Column(String(50))
    CONTENIDO = Column(Text)


class DatArchivosPersonal(Base):
    __tablename__ = "DAT_ARCHIVOS_PERSONAL"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    EVENTO = Column(Integer, ForeignKey("DAT_EVENTOS_PERSONAL.ID"))
    ARCHIVO = Column(Integer)
    UBICACION = Column(String(100))


class DatDetallesArchivosPersonal(Base):
    __tablename__ = "DAT_DETALLES_ARCHIVOS_PERSONAL"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    MEDIA_ID = Column(Integer, ForeignKey("DAT_ARCHIVOS_PERSONAL.ID"))
    TITULO = Column(String(50))
    PERSONAS = Column(String(100))
    LUGAR = Column(String(100))
    FECHA = Column(Date)
    HORA = Column(Time)
    DESCRIPCION = Column(Text)

