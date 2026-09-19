from flask import Blueprint, request, jsonify
from datetime import datetime

from database.connection import SessionLocal

from database.bot.models_bot import (
    BtClientes,
    BtUsuariosTG,
    BtEquipos,
    BtTrabajos,
    BtTrabajosConceptos,
    BtTrabajosHistorial
)


bp = Blueprint("bot", __name__, url_prefix="/api/bot")


# =========================================================
# 🤖 USUARIOS TELEGRAM
# =========================================================

@bp.post("/usuario")
def registrar_usuario():
    data = request.json

    if not data or "id_usuario_tg" not in data:
        return jsonify({
            "ok": False,
            "error": "id_usuario_tg requerido"
        }), 400

    db = SessionLocal()

    try:
        id_usuario_tg = data["id_usuario_tg"]

        usuario = db.query(BtUsuariosTG).filter(
            BtUsuariosTG.id_usuario_tg == id_usuario_tg
        ).first()

        if usuario:
            usuario.username = data.get("username")
            usuario.nombre = data.get("nombre")
            usuario.apellido = data.get("apellido")
        else:
            usuario = BtUsuariosTG(
                id_usuario_tg=id_usuario_tg,
                username=data.get("username"),
                nombre=data.get("nombre"),
                apellido=data.get("apellido"),
                tipo_usuario=data.get("tipo_usuario", "CLIENTE"),
                activo=True
            )

            db.add(usuario)

        db.commit()

        return jsonify({
            "ok": True,
            "data": {
                "id_usuario_tg": usuario.id_usuario_tg,
                "tipo_usuario": usuario.tipo_usuario,
                "id_cliente": usuario.cliente_id
            }
        })

    except Exception as e:
        db.rollback()

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

    finally:
        db.close()

@bp.get("/usuario/<int:id_usuario_tg>")
def obtener_usuario(id_usuario_tg):
    db = SessionLocal()

    try:
        usuario = db.query(BtUsuariosTG).filter(
            BtUsuariosTG.id_usuario_tg == id_usuario_tg,
            BtUsuariosTG.activo == True
        ).first()

        if not usuario:
            return jsonify({
                "ok": False,
                "error": "Usuario no encontrado"
            }), 404

        return jsonify({
            "ok": True,
            "data": {
                "id_usuario_tg": usuario.id_usuario_tg,
                "id_cliente": usuario.cliente_id,
                "username": usuario.username,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "tipo_usuario": usuario.tipo_usuario
            }
        })

    finally:
        db.close()

# =========================================================
# 🤖 CLIENTES
# =========================================================

@bp.get("/clientes")
def listar_clientes():
    db = SessionLocal()

    try:
        clientes = db.query(BtClientes).filter(
            BtClientes.activo == True
        ).order_by(
            BtClientes.nombre
        ).all()

        return jsonify({
            "ok": True,
            "data": [
                {
                    "id_cliente": cliente.id,
                    "nombre": cliente.nombre,
                    "telefono": cliente.telefono,
                    "correo": cliente.correo,
                    "observaciones": cliente.observaciones
                }
                for cliente in clientes
            ]
        })

    finally:
        db.close()


@bp.get("/cliente/<int:id_cliente>")
def obtener_cliente(id_cliente):
    db = SessionLocal()

    try:
        cliente = db.query(BtClientes).filter(
            BtClientes.id == id_cliente,
            BtClientes.activo == True
        ).first()

        if not cliente:
            return jsonify({
                "ok": False,
                "error": "Cliente no encontrado"
            }), 404

        return jsonify({
            "ok": True,
            "data": {
                "id_cliente": cliente.id,
                "nombre": cliente.nombre,
                "telefono": cliente.telefono,
                "correo": cliente.correo,
                "observaciones": cliente.observaciones
            }
        })

    finally:
        db.close()


@bp.post("/cliente")
def crear_cliente():
    data = request.json

    if not data or not data.get("nombre"):
        return jsonify({
            "ok": False,
            "error": "nombre requerido"
        }), 400

    db = SessionLocal()

    try:
        cliente = BtClientes(
            nombre=data["nombre"],
            telefono=data.get("telefono"),
            correo=data.get("correo"),
            observaciones=data.get("observaciones"),
            activo=True
        )

        db.add(cliente)
        db.commit()
        db.refresh(cliente)

        return jsonify({
            "ok": True,
            "data": {
                "id_cliente": cliente.id,
                "nombre": cliente.nombre
            }
        })

    except Exception as e:
        db.rollback()

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

    finally:
        db.close()


# =========================================================
# 🤖 EQUIPOS
# =========================================================

@bp.get("/clientes/<int:id_cliente>/equipos")
def listar_equipos_cliente(id_cliente):
    db = SessionLocal()

    try:
        equipos = db.query(BtEquipos).filter(
            BtEquipos.cliente_id == id_cliente,
            BtEquipos.activo == True
        ).order_by(
            BtEquipos.nombre_equipo,
            BtEquipos.marca,
            BtEquipos.modelo
        ).all()

        return jsonify({
            "ok": True,
            "data": [
                {
                    "id_equipo": equipo.id,
                    "tipo": equipo.tipo,
                    "marca": equipo.marca,
                    "modelo": equipo.modelo,
                    "numero_serie": equipo.numero_serie,
                    "nombre_equipo": equipo.nombre_equipo,
                    "observaciones": equipo.observaciones
                }
                for equipo in equipos
            ]
        })

    finally:
        db.close()


@bp.post("/equipo")
def crear_equipo():
    data = request.json

    if not data:
        return jsonify({
            "ok": False,
            "error": "Datos requeridos"
        }), 400

    if not data.get("id_cliente"):
        return jsonify({
            "ok": False,
            "error": "id_cliente requerido"
        }), 400

    if not data.get("tipo"):
        return jsonify({
            "ok": False,
            "error": "tipo requerido"
        }), 400

    db = SessionLocal()

    try:
        cliente = db.query(BtClientes).filter(
            BtClientes.id == data["id_cliente"],
            BtClientes.activo == True
        ).first()

        if not cliente:
            return jsonify({
                "ok": False,
                "error": "Cliente no encontrado"
            }), 404

        equipo = BtEquipos(
            cliente_id=data["id_cliente"],
            tipo=data["tipo"],
            marca=data.get("marca"),
            modelo=data.get("modelo"),
            numero_serie=data.get("numero_serie"),
            nombre_equipo=data.get("nombre_equipo"),
            observaciones=data.get("observaciones"),
            activo=True
        )

        db.add(equipo)
        db.commit()
        db.refresh(equipo)

        return jsonify({
            "ok": True,
            "data": {
                "id_equipo": equipo.id,
                "id_cliente": equipo.cliente_id
            }
        })

    except Exception as e:
        db.rollback()

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

    finally:
        db.close()


# =========================================================
# 🤖 TRABAJOS
# =========================================================

@bp.post("/trabajo")
def crear_trabajo():
    data = request.json

    if not data:
        return jsonify({
            "ok": False,
            "error": "Datos requeridos"
        }), 400

    if not data.get("id_cliente"):
        return jsonify({
            "ok": False,
            "error": "id_cliente requerido"
        }), 400

    if not data.get("tipo_trabajo"):
        return jsonify({
            "ok": False,
            "error": "tipo_trabajo requerido"
        }), 400

    db = SessionLocal()

    try:
        cliente = db.query(BtClientes).filter(
            BtClientes.id == data["id_cliente"],
            BtClientes.activo == True
        ).first()

        if not cliente:
            return jsonify({
                "ok": False,
                "error": "Cliente no encontrado"
            }), 404

        # =================================================
        # GENERAR FOLIO
        # =================================================

        ultimo_trabajo = db.query(BtTrabajos).order_by(
            BtTrabajos.id.desc()
        ).first()

        if ultimo_trabajo:
            numero = ultimo_trabajo.id + 1
        else:
            numero = 1

        folio = f"TR-{numero:06d}"

        trabajo = BtTrabajos(
            folio=folio,
            cliente_id=data["id_cliente"],
            equipo_id=data.get("id_equipo"),
            tipo_trabajo=data["tipo_trabajo"],
            descripcion=data.get("descripcion"),
            observaciones=data.get("observaciones"),
            requisitos=data.get("requisitos"),
            estatus=data.get("estatus", "PENDIENTE"),
            fecha_registro=datetime.now(),
            activo=True
        )

        db.add(trabajo)
        db.flush()

        # =================================================
        # HISTORIAL INICIAL
        # =================================================

        historial = BtTrabajosHistorial(
            trabajo_id=trabajo.id,
            estatus=trabajo.estatus,
            descripcion="Trabajo creado",
            fecha=datetime.now(),
            usuario_tg_id=data.get("id_usuario_tg")
        )

        db.add(historial)

        db.commit()
        db.refresh(trabajo)

        return jsonify({
            "ok": True,
            "data": {
                "id_trabajo": trabajo.id,
                "folio": trabajo.folio,
                "estatus": trabajo.estatus
            }
        })

    except Exception as e:
        db.rollback()

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

    finally:
        db.close()


@bp.get("/trabajo/<int:id_trabajo>")
def obtener_trabajo(id_trabajo):
    db = SessionLocal()

    try:
        trabajo = db.query(BtTrabajos).filter(
            BtTrabajos.id == id_trabajo,
            BtTrabajos.activo == True
        ).first()

        if not trabajo:
            return jsonify({
                "ok": False,
                "error": "Trabajo no encontrado"
            }), 404

        return jsonify({
            "ok": True,
            "data": {
                "id_trabajo": trabajo.id,
                "folio": trabajo.folio,
                "id_cliente": trabajo.cliente_id,
                "id_equipo": trabajo.equipo_id,
                "tipo_trabajo": trabajo.tipo_trabajo,
                "descripcion": trabajo.descripcion,
                "observaciones": trabajo.observaciones,
                "requisitos": trabajo.requisitos,
                "estatus": trabajo.estatus,
                "fecha_registro": trabajo.fecha_registro.isoformat()
                if trabajo.fecha_registro else None,
                "fecha_actualizacion": trabajo.fecha_actualizacion.isoformat()
                if trabajo.fecha_actualizacion else None,
                "fecha_terminado": trabajo.fecha_terminado.isoformat()
                if trabajo.fecha_terminado else None
            }
        })

    finally:
        db.close()


# =========================================================
# 🤖 TRABAJOS POR CLIENTE
# =========================================================

@bp.get("/cliente/<int:id_cliente>/trabajos")
def listar_trabajos_cliente(id_cliente):
    db = SessionLocal()

    try:
        trabajos = db.query(BtTrabajos).filter(
            BtTrabajos.cliente_id == id_cliente,
            BtTrabajos.activo == True
        ).order_by(
            BtTrabajos.id.desc()
        ).all()

        return jsonify({
            "ok": True,
            "data": [
                {
                    "id_trabajo": trabajo.id,
                    "folio": trabajo.folio,
                    "tipo_trabajo": trabajo.tipo_trabajo,
                    "descripcion": trabajo.descripcion,
                    "estatus": trabajo.estatus,
                    "fecha_registro": trabajo.fecha_registro.isoformat()
                    if trabajo.fecha_registro else None
                }
                for trabajo in trabajos
            ]
        })

    finally:
        db.close()


# =========================================================
# 🤖 TRABAJOS PENDIENTES
# =========================================================

@bp.get("/trabajos/pendientes")
def listar_trabajos_pendientes():
    db = SessionLocal()

    try:
        trabajos = db.query(BtTrabajos).filter(
            BtTrabajos.activo == True,
            BtTrabajos.estatus.notin_([
                "TERMINADO",
                "ENTREGADO"
            ])
        ).order_by(
            BtTrabajos.id.desc()
        ).all()

        return jsonify({
            "ok": True,
            "data": [
                {
                    "id_trabajo": trabajo.id,
                    "folio": trabajo.folio,
                    "id_cliente": trabajo.cliente_id,
                    "cliente": trabajo.cliente.nombre
                    if trabajo.cliente else None,
                    "id_equipo": trabajo.equipo_id,
                    "tipo_trabajo": trabajo.tipo_trabajo,
                    "descripcion": trabajo.descripcion,
                    "estatus": trabajo.estatus,
                    "fecha_registro": trabajo.fecha_registro.isoformat()
                    if trabajo.fecha_registro else None
                }
                for trabajo in trabajos
            ]
        })

    finally:
        db.close()


# =========================================================
# 🤖 ACTUALIZAR ESTATUS
# =========================================================

@bp.put("/trabajo/<int:id_trabajo>/estatus")
def actualizar_estatus(id_trabajo):
    data = request.json

    if not data or not data.get("estatus"):
        return jsonify({
            "ok": False,
            "error": "estatus requerido"
        }), 400

    db = SessionLocal()

    try:
        trabajo = db.query(BtTrabajos).filter(
            BtTrabajos.id == id_trabajo,
            BtTrabajos.activo == True
        ).first()

        if not trabajo:
            return jsonify({
                "ok": False,
                "error": "Trabajo no encontrado"
            }), 404

        nuevo_estatus = data["estatus"]

        trabajo.estatus = nuevo_estatus
        trabajo.fecha_actualizacion = datetime.now()

        if nuevo_estatus == "TERMINADO":
            trabajo.fecha_terminado = datetime.now()

        historial = BtTrabajosHistorial(
            trabajo_id=trabajo.id,
            estatus=nuevo_estatus,
            descripcion=data.get("descripcion"),
            fecha=datetime.now(),
            usuario_tg_id=data.get("id_usuario_tg")
        )

        db.add(historial)
        db.commit()

        return jsonify({
            "ok": True,
            "data": {
                "id_trabajo": trabajo.id,
                "folio": trabajo.folio,
                "estatus": trabajo.estatus
            }
        })

    except Exception as e:
        db.rollback()

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

    finally:
        db.close()


# =========================================================
# 🤖 HISTORIAL
# =========================================================

@bp.get("/trabajo/<int:id_trabajo>/historial")
def obtener_historial(id_trabajo):
    db = SessionLocal()

    try:
        historial = db.query(BtTrabajosHistorial).filter(
            BtTrabajosHistorial.trabajo_id == id_trabajo
        ).order_by(
            BtTrabajosHistorial.fecha.asc()
        ).all()

        return jsonify({
            "ok": True,
            "data": [
                {
                    "id_historial": item.id,
                    "estatus": item.estatus,
                    "descripcion": item.descripcion,
                    "fecha": item.fecha.isoformat()
                    if item.fecha else None,
                    "id_usuario_tg": item.usuario_tg_id
                }
                for item in historial
            ]
        })

    finally:
        db.close()


# =========================================================
# 🤖 CONCEPTOS
# =========================================================

@bp.post("/trabajo/<int:id_trabajo>/concepto")
def agregar_concepto(id_trabajo):
    data = request.json

    if not data:
        return jsonify({
            "ok": False,
            "error": "Datos requeridos"
        }), 400

    if not data.get("tipo"):
        return jsonify({
            "ok": False,
            "error": "tipo requerido"
        }), 400

    if not data.get("descripcion"):
        return jsonify({
            "ok": False,
            "error": "descripcion requerida"
        }), 400

    db = SessionLocal()

    try:
        trabajo = db.query(BtTrabajos).filter(
            BtTrabajos.id == id_trabajo,
            BtTrabajos.activo == True
        ).first()

        if not trabajo:
            return jsonify({
                "ok": False,
                "error": "Trabajo no encontrado"
            }), 404

        concepto = BtTrabajosConceptos(
            trabajo_id=id_trabajo,
            tipo=data["tipo"],
            descripcion=data["descripcion"],
            cantidad=data.get("cantidad", 1),
            costo=data.get("costo", 0),
            precio=data.get("precio", 0),
            observaciones=data.get("observaciones"),
            activo=True
        )

        db.add(concepto)
        db.commit()
        db.refresh(concepto)

        return jsonify({
            "ok": True,
            "data": {
                "id_concepto": concepto.id,
                "id_trabajo": concepto.trabajo_id,
                "tipo": concepto.tipo,
                "descripcion": concepto.descripcion,
                "cantidad": float(concepto.cantidad),
                "costo": float(concepto.costo),
                "precio": float(concepto.precio)
            }
        })

    except Exception as e:
        db.rollback()

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

    finally:
        db.close()


@bp.get("/trabajo/<int:id_trabajo>/conceptos")
def listar_conceptos(id_trabajo):
    db = SessionLocal()

    try:
        conceptos = db.query(BtTrabajosConceptos).filter(
            BtTrabajosConceptos.trabajo_id == id_trabajo,
            BtTrabajosConceptos.activo == True
        ).order_by(
            BtTrabajosConceptos.id
        ).all()

        return jsonify({
            "ok": True,
            "data": [
                {
                    "id_concepto": concepto.id,
                    "tipo": concepto.tipo,
                    "descripcion": concepto.descripcion,
                    "cantidad": float(concepto.cantidad),
                    "costo": float(concepto.costo),
                    "precio": float(concepto.precio),
                    "observaciones": concepto.observaciones
                }
                for concepto in conceptos
            ]
        })

    finally:
        db.close()