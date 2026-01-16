from flask import Blueprint, request, jsonify
from sqlalchemy import text
from database.connection import SessionLocal

bp = Blueprint("bot", __name__, url_prefix="/api/bot")

# =========================================================
# 🤖 CATÁLOGO
# =========================================================

@bp.get("/productos")
def listar_productos():
    db = SessionLocal()
    try:
        r = db.execute(text("""
            SELECT ID_PRODUCTO, NOMBRE
            FROM BT_PRODUCTOS
            WHERE ACTIVO = 1
            ORDER BY NOMBRE
        """))
        return jsonify([dict(x._mapping) for x in r])
    finally:
        db.close()


@bp.get("/productos/<int:id_producto>/variantes")
def listar_variantes(id_producto):
    db = SessionLocal()
    try:
        r = db.execute(text("""
            SELECT ID_VARIANTE, NOMBRE
            FROM BT_PRODUCTOS_VARIANTES
            WHERE ID_PRODUCTO = :id
              AND ACTIVO = 1
            ORDER BY NOMBRE
        """), {"id": id_producto})
        return jsonify([dict(x._mapping) for x in r])
    finally:
        db.close()


@bp.get("/catalogo")
def catalogo():
    db = SessionLocal()
    try:
        r = db.execute(text("""
            SELECT ID_PRODUCTO, NOMBRE
            FROM BT_PRODUCTOS
            WHERE ACTIVO = 1
            ORDER BY NOMBRE
        """))
        return jsonify({"ok": True, "data": [dict(x._mapping) for x in r]})
    finally:
        db.close()


@bp.get("/catalogo/<int:id_producto>")
def catalogo_detalle(id_producto):
    db = SessionLocal()
    try:
        producto = db.execute(text("""
            SELECT ID_PRODUCTO, NOMBRE
            FROM BT_PRODUCTOS
            WHERE ID_PRODUCTO = :id
        """), {"id": id_producto}).fetchone()

        if not producto:
            return jsonify({"ok": False, "msg": "Producto no encontrado"}), 404

        variantes = db.execute(text("""
            SELECT ID_VARIANTE, NOMBRE
            FROM BT_PRODUCTOS_VARIANTES
            WHERE ID_PRODUCTO = :id
              AND ACTIVO = 1
            ORDER BY NOMBRE
        """), {"id": id_producto})

        return jsonify({
            "ok": True,
            "data": {
                "id_producto": producto.ID_PRODUCTO,
                "nombre": producto.NOMBRE,
                "variantes": [dict(v._mapping) for v in variantes]
            }
        })
    finally:
        db.close()

# =========================================================
# 🤖 USUARIOS
# =========================================================

@bp.post("/usuario")
def registrar_usuario():
    data = request.json
    db = SessionLocal()
    try:
        db.execute(text("""
            UPDATE BT_USUARIOS_TG
            SET USERNAME = :username,
                NOMBRE = :nombre,
                APELLIDO = :apellido
            WHERE ID_USUARIO_TG = :id;

            IF @@ROWCOUNT = 0
            BEGIN
                INSERT INTO BT_USUARIOS_TG
                (ID_USUARIO_TG, USERNAME, NOMBRE, APELLIDO)
                VALUES (:id, :username, :nombre, :apellido);
            END
        """), {
            "id": data.get("id_usuario_tg"),
            "username": data.get("username"),
            "nombre": data.get("nombre"),
            "apellido": data.get("apellido")
        })
        db.commit()
        return jsonify({"ok": True})
    except Exception as e:
        db.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        db.close()

# =========================================================
# 🤖 PEDIDOS
# =========================================================

@bp.post("/pedido")
def crear_pedido():
    data = request.json
    if not data or "id_usuario_tg" not in data:
        return jsonify({"ok": False, "error": "id_usuario_tg requerido"}), 400

    db = SessionLocal()
    try:
        r = db.execute(text("""
            INSERT INTO BT_PEDIDOS (ID_USUARIO_TG)
            OUTPUT INSERTED.ID_PEDIDO
            VALUES (:id)
        """), {"id": data["id_usuario_tg"]})

        db.commit()
        return jsonify({"ok": True, "id_pedido": r.scalar()})
    finally:
        db.close()


@bp.post("/pedido/item")
def agregar_item():
    data = request.json
    db = SessionLocal()
    try:
        db.execute(text("""
            INSERT INTO BT_PEDIDOS_DETALLE
            (ID_PEDIDO, ID_PRODUCTO, ID_VARIANTE, CANTIDAD)
            VALUES (:p, :prod, :var, :cant)
        """), {
            "p": data.get("id_pedido"),
            "prod": data.get("id_producto"),
            "var": data.get("id_variante"),
            "cant": data.get("cantidad", 1)
        })
        db.commit()
        return jsonify({"ok": True})
    finally:
        db.close()


@bp.post("/pedido/cerrar")
def cerrar_pedido():
    data = request.json
    db = SessionLocal()
    try:
        db.execute(text("""
            UPDATE BT_PEDIDOS
            SET ESTATUS = 'cerrado'
            WHERE ID_PEDIDO = :id
        """), {"id": data.get("id_pedido")})
        db.commit()
        return jsonify({"ok": True})
    finally:
        db.close()
