from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, NVARCHAR
from sqlalchemy.orm import relationship
from .connection import Base
from .models_catalogos import CatModulos, CatArchivoTipo


# ----------------------------------------
# CATÁLOGOS
# ----------------------------------------




class CatMedicosMedico(Base):
    __tablename__ = "CAT_MEDICOS_MEDICO"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    nombre = Column("NOMBRE", NVARCHAR(100))




class CatClinicasMedico(Base):
    __tablename__ = "CAT_CLINICAS_MEDICO"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    unidad_medica = Column("UNIDAD_MEDICA", NVARCHAR(50))




class CatEventosMedico(Base):
    __tablename__ = "CAT_EVENTOS_MEDICO"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    evento = Column("EVENTO", NVARCHAR(50))




class CatImportanciaMedico(Base):
    __tablename__ = "CAT_IMPORTANCIA_MEDICO"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    importancia = Column("IMPORTANCIA", NVARCHAR(50))




class CatMedicamentosMedico(Base):
    __tablename__ = "CAT_MEDICAMENTOS_MEDICO"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    medicamento = Column("MEDICAMENTO", NVARCHAR(150))




# ----------------------------------------
# TABLAS DE DATOS
# ----------------------------------------

class DatConsultasMedico(Base):
    __tablename__ = "DAT_CONSULTAS_MEDICO"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    fecha = Column("FECHA", DateTime)
    modulo_id = Column("MODULO_ID", Integer, ForeignKey("CAT_MODULOS.ID"))
    evento_id = Column("EVENTO", Integer, ForeignKey("CAT_EVENTOS_MEDICO.ID"))
    importancia_id = Column("IMPORTANCIA", Integer, ForeignKey("CAT_IMPORTANCIA_MEDICO.ID"))
    unidad_medica_id = Column("UNIDAD_MEDICA", Integer, ForeignKey("CAT_CLINICAS_MEDICO.ID"))
    medico_id = Column("MEDICO", Integer, ForeignKey("CAT_MEDICOS_MEDICO.ID"))
    observaciones = Column("OBSERVACIONES", Text)

    # Relaciones



class DatMedicamentosMedico(Base):
    __tablename__ = "DAT_MEDICAMENTOS_MEDICO"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    consulta_id = Column("CONSULTA", Integer, ForeignKey("DAT_CONSULTAS_MEDICO.ID"))
    medicamento_id = Column("MEDICAMENTO", Integer, ForeignKey("CAT_MEDICAMENTOS_MEDICO.ID"))




class DatArchivosMedico(Base):
    __tablename__ = "DAT_ARCHIVOS_MEDICO"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    movimiento_id = Column("MOVIMIENTO", Integer, ForeignKey("DAT_CONSULTAS_MEDICO.ID"))
    archivo_id = Column("ARCHIVO", Integer, ForeignKey("CAT_ARCHIVO_TIPO.ID"))
    ubicacion = Column("UBICACION", NVARCHAR(100))



