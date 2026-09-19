from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..connection import Base


# =====================================================
# CLIENTES
# =====================================================
class BtClientes(Base):
    __tablename__ = "BT_CLIENTES"

    id = Column("ID_CLIENTE", Integer, primary_key=True, autoincrement=True)
    nombre = Column("NOMBRE", String(150), nullable=False)
    telefono = Column("TELEFONO", String(30))
    correo = Column("CORREO", String(150))
    observaciones = Column("OBSERVACIONES", String(500))
    fecha_registro = Column("FECHA_REGISTRO", DateTime)
    activo = Column("ACTIVO", Boolean)

    usuarios_tg = relationship("BtUsuariosTG", back_populates="cliente")
    equipos = relationship("BtEquipos", back_populates="cliente")
    trabajos = relationship("BtTrabajos", back_populates="cliente")


# =====================================================
# USUARIOS DE TELEGRAM
# =====================================================
class BtUsuariosTG(Base):
    __tablename__ = "BT_USUARIOS_TG"

    id_usuario_tg = Column("ID_USUARIO_TG", BigInteger, primary_key=True)
    cliente_id = Column("ID_CLIENTE", Integer, ForeignKey("BT_CLIENTES.ID_CLIENTE"))
    username = Column("USERNAME", String(100))
    nombre = Column("NOMBRE", String(100))
    apellido = Column("APELLIDO", String(100))
    tipo_usuario = Column("TIPO_USUARIO", String(20), nullable=False)
    fecha_registro = Column("FECHA_REGISTRO", DateTime)
    activo = Column("ACTIVO", Boolean)

    cliente = relationship("BtClientes", back_populates="usuarios_tg")
    historiales = relationship("BtTrabajosHistorial", back_populates="usuario_tg")


# =====================================================
# EQUIPOS
# =====================================================
class BtEquipos(Base):
    __tablename__ = "BT_EQUIPOS"

    id = Column("ID_EQUIPO", Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(
        "ID_CLIENTE",
        Integer,
        ForeignKey("BT_CLIENTES.ID_CLIENTE"),
        nullable=False
    )
    tipo = Column("TIPO", String(50), nullable=False)
    marca = Column("MARCA", String(100))
    modelo = Column("MODELO", String(100))
    numero_serie = Column("NUMERO_SERIE", String(150))
    nombre_equipo = Column("NOMBRE_EQUIPO", String(100))
    observaciones = Column("OBSERVACIONES", String(500))
    fecha_registro = Column("FECHA_REGISTRO", DateTime)
    activo = Column("ACTIVO", Boolean)

    cliente = relationship("BtClientes", back_populates="equipos")
    trabajos = relationship("BtTrabajos", back_populates="equipo")


# =====================================================
# TRABAJOS
# =====================================================
class BtTrabajos(Base):
    __tablename__ = "BT_TRABAJOS"

    id = Column("ID_TRABAJO", Integer, primary_key=True, autoincrement=True)
    folio = Column("FOLIO", String(30), nullable=False, unique=True)

    cliente_id = Column(
        "ID_CLIENTE",
        Integer,
        ForeignKey("BT_CLIENTES.ID_CLIENTE"),
        nullable=False
    )

    equipo_id = Column(
        "ID_EQUIPO",
        Integer,
        ForeignKey("BT_EQUIPOS.ID_EQUIPO")
    )

    tipo_trabajo = Column("TIPO_TRABAJO", String(100), nullable=False)
    descripcion = Column("DESCRIPCION", String(500))
    observaciones = Column("OBSERVACIONES", String(1000))
    requisitos = Column("REQUISITOS", String(1000))
    estatus = Column("ESTATUS", String(30), nullable=False)

    fecha_registro = Column("FECHA_REGISTRO", DateTime)
    fecha_actualizacion = Column("FECHA_ACTUALIZACION", DateTime)
    fecha_terminado = Column("FECHA_TERMINADO", DateTime)

    activo = Column("ACTIVO", Boolean)

    cliente = relationship("BtClientes", back_populates="trabajos")
    equipo = relationship("BtEquipos", back_populates="trabajos")

    conceptos = relationship(
        "BtTrabajosConceptos",
        back_populates="trabajo"
    )

    historial = relationship(
        "BtTrabajosHistorial",
        back_populates="trabajo"
    )


# =====================================================
# CONCEPTOS DE TRABAJOS
# =====================================================
class BtTrabajosConceptos(Base):
    __tablename__ = "BT_TRABAJOS_CONCEPTOS"

    id = Column("ID_CONCEPTO", Integer, primary_key=True, autoincrement=True)

    trabajo_id = Column(
        "ID_TRABAJO",
        Integer,
        ForeignKey("BT_TRABAJOS.ID_TRABAJO"),
        nullable=False
    )

    tipo = Column("TIPO", String(30), nullable=False)
    descripcion = Column("DESCRIPCION", String(255), nullable=False)

    cantidad = Column("CANTIDAD", Numeric(10, 2), nullable=False)
    costo = Column("COSTO", Numeric(12, 2), nullable=False)
    precio = Column("PRECIO", Numeric(12, 2), nullable=False)

    observaciones = Column("OBSERVACIONES", String(500))
    activo = Column("ACTIVO", Boolean)

    trabajo = relationship(
        "BtTrabajos",
        back_populates="conceptos"
    )


# =====================================================
# HISTORIAL DE TRABAJOS
# =====================================================
class BtTrabajosHistorial(Base):
    __tablename__ = "BT_TRABAJOS_HISTORIAL"

    id = Column("ID_HISTORIAL", Integer, primary_key=True, autoincrement=True)

    trabajo_id = Column(
        "ID_TRABAJO",
        Integer,
        ForeignKey("BT_TRABAJOS.ID_TRABAJO"),
        nullable=False
    )

    estatus = Column("ESTATUS", String(30), nullable=False)
    descripcion = Column("DESCRIPCION", String(1000))
    fecha = Column("FECHA", DateTime)

    usuario_tg_id = Column(
        "ID_USUARIO_TG",
        BigInteger,
        ForeignKey("BT_USUARIOS_TG.ID_USUARIO_TG")
    )

    trabajo = relationship(
        "BtTrabajos",
        back_populates="historial"
    )

    usuario_tg = relationship(
        "BtUsuariosTG",
        back_populates="historiales"
    )