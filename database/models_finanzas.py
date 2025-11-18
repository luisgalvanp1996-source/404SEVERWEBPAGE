from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from .connection import Base
from .models_catalogos import CatModulos, CatArchivoTipo
# =====================================================
# CATALOGO DE CONCEPTOS FINANCIEROS
# =====================================================
class CatConceptosFinanzas(Base):
    __tablename__ = "CAT_CONCEPTOS_FINANZAS"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    concepto = Column("CONCEPTO", String(50), nullable=False)
    factor = Column("FACTOR", Integer)  # Puede ser tipo, multiplicador, etc.




# =====================================================
# CATALOGO DE PROVEEDORES FINANCIEROS
# =====================================================
class CatProveedoresFinanzas(Base):
    __tablename__ = "CAT_PROVEEDORES_FINANZAS"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    nombre = Column("NOMBRE", String(100), nullable=False)




# =====================================================
# TABLA DE MOVIMIENTOS FINANCIEROS
# =====================================================
class DatMovimientosFinanzas(Base):
    __tablename__ = "DAT_MOVIMIENTOS_FINANZAS"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    tipo_movimiento = Column("TIPO_MOVIMIENTO", Integer)  # relación con CAT_TIPOS o tipo interno
    concepto_id = Column("CONCEPTO_ID", Integer, ForeignKey("CAT_CONCEPTOS_FINANZAS.ID"))
    proveedor_id = Column("PROVEEDOR_ID", Integer, ForeignKey("CAT_PROVEEDORES_FINANZAS.ID"))
    fecha = Column("FECHA", Date)
    modulo = Column("MODULO", Integer, ForeignKey("CAT_MODULOS.ID"))
    importe = Column("IMPORTE", Numeric(18, 2))






# =====================================================
# TABLA DE ARCHIVOS ASOCIADOS A MOVIMIENTOS FINANCIEROS
# =====================================================
class DatArchivosFinanzas(Base):
    __tablename__ = "DAT_ARCHIVOS_FINANZAS"

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    movimiento_id = Column("MOVIMIENTO", Integer, ForeignKey("DAT_MOVIMIENTOS_FINANZAS.ID"))
    archivo_id = Column("ARCHIVO", Integer, ForeignKey("CAT_ARCHIVO_TIPO.ID"))
    ubicacion = Column("UBICACION", String(100))


