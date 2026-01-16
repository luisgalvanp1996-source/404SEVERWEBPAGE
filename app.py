from flask import Flask, render_template, send_from_directory, request, jsonify
from sqlalchemy import text
import os
import psutil
import win32api
from datetime import datetime
from dotenv import load_dotenv

# Importa tu sesión
from database.connection import SessionLocal

# Importa tus módulos existentes
from modules.biblia.routes import bp as biblia_bp
from modules.medico.routes import bp as medico_bp
from modules.finanzas.routes import bp as finanzas_bp
from modules.personal.routes import bp as personal_bp


def get_drives_info():
    drives_info = []
    partitions = psutil.disk_partitions(all=False)

    for p in partitions:
        if "cdrom" in p.opts or not os.path.exists(p.mountpoint):
            continue

        try:
            usage = psutil.disk_usage(p.mountpoint)
        except PermissionError:
            continue

        try:
            volume_name = win32api.GetVolumeInformation(p.mountpoint)[0] or "Sin nombre"
        except Exception:
            volume_name = "Desconocido"

        drives_info.append({
            "path": p.mountpoint,
            "label": volume_name,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        })

    return drives_info


def create_app():
    app = Flask(__name__)

    load_dotenv()  # ✅ necesario
    app.secret_key = os.getenv("SECRET_KEY")
    DATA_FOLDER = os.path.join(os.getcwd(), "Data")

    @app.route('/Data/<path:filename>')
    def data_files(filename):
        return send_from_directory(DATA_FOLDER, filename)

    # Blueprints existentes
    app.register_blueprint(biblia_bp)
    app.register_blueprint(medico_bp)
    app.register_blueprint(finanzas_bp)
    app.register_blueprint(personal_bp)

    # =========================================================
    # 🤖 BOT TELEGRAM – API PEDIDOS
    # =========================================================

    @app.get("/api/bot/pedidos/pendientes")
    def bot_listar_pedidos_pendientes():
        db = SessionLocal()

        try:
            result = db.execute(
                text("""
                    SELECT
                        p.ID_PEDIDO,
                        u.USERNAME,
                        u.NOMBRE AS nombre_usuario,
                        u.APELLIDO AS apellido_usuario,
                        pr.NOMBRE AS producto,
                        v.NOMBRE AS variante,
                        d.CANTIDAD
                    FROM BT_PEDIDOS p
                    JOIN BT_PEDIDOS_DETALLE d ON d.ID_PEDIDO = p.ID_PEDIDO
                    JOIN BT_PRODUCTOS pr ON pr.ID_PRODUCTO = d.ID_PRODUCTO
                    JOIN BT_PRODUCTOS_VARIANTES v ON v.ID_VARIANTE = d.ID_VARIANTE
                    JOIN BT_USUARIOS_TG u ON u.ID_USUARIO_TG = p.ID_USUARIO_TG
                    WHERE p.ESTATUS = 'pendiente'
                    ORDER BY p.ID_PEDIDO
                """)
            )

            pedidos = {}

            for r in result:
                r = r._mapping
                pid = r["ID_PEDIDO"]

                if pid not in pedidos:
                    pedidos[pid] = []

                pedidos[pid].append({
                    "producto": r["producto"],
                    "variante": r["variante"],
                    "cantidad": r["CANTIDAD"],
                    "usuario": {
                        "username": r["USERNAME"],
                        "nombre": r["nombre_usuario"],
                        "apellido": r["apellido_usuario"]
                    }
                })

            return jsonify(pedidos)

        except Exception as e:
            print("🔥 BOT pedidos pendientes:", e)
            return jsonify({"error": str(e)}), 500

        finally:
            db.close()


    @app.post("/api/bot/usuario")
    def bot_registrar_usuario():
        data = request.json
        db = SessionLocal()

        try:
            db.execute(
    text("""
        UPDATE BT_USUARIOS_TG
        SET
            USERNAME = :username,
            NOMBRE   = :nombre,
            APELLIDO = :apellido
        WHERE ID_USUARIO_TG = :id;

        IF @@ROWCOUNT = 0
        BEGIN
            INSERT INTO BT_USUARIOS_TG
                (ID_USUARIO_TG, USERNAME, NOMBRE, APELLIDO)
            VALUES
                (:id, :username, :nombre, :apellido);
        END
    """),
    {
        "id": data.get("id_usuario_tg"),
        "username": data.get("username"),
        "nombre": data.get("nombre"),
        "apellido": data.get("apellido")
    }
)


            db.commit()
            return jsonify({"ok": True})

        except Exception as e:
            db.rollback()
            print("🔥 BOT usuario:", e)
            return jsonify({"error": str(e)}), 500

        finally:
            db.close()


    @app.post("/api/bot/pedido")
    def bot_crear_pedido():
        data = request.json
        db = SessionLocal()

        try:
            result = db.execute(
                text("""
                    INSERT INTO BT_PEDIDOS (ID_USUARIO_TG)
                    OUTPUT INSERTED.ID_PEDIDO
                    VALUES (:id_usuario)
                """),
                {"id_usuario": data.get("id_usuario_tg")}
            )

            pedido_id = result.scalar()
            db.commit()

            return jsonify({"id_pedido": pedido_id})

        except Exception as e:
            db.rollback()
            print("🔥 BOT pedido:", e)
            return jsonify({"error": str(e)}), 500

        finally:
            db.close()


    @app.post("/api/bot/pedido/item")
    def bot_agregar_item():
        data = request.json
        db = SessionLocal()

        try:
            db.execute(
                text("""
                    INSERT INTO BT_PEDIDOS_DETALLE
                    (ID_PEDIDO, ID_PRODUCTO, ID_VARIANTE, CANTIDAD)
                    SELECT
                        :id_pedido,
                        p.ID_PRODUCTO,
                        v.ID_VARIANTE,
                        :cantidad
                    FROM BT_PRODUCTOS p
                    JOIN BT_PRODUCTOS_VARIANTES v
                        ON v.ID_PRODUCTO = p.ID_PRODUCTO
                    WHERE p.NOMBRE = :producto
                      AND v.NOMBRE = :variante
                """),
                {
                    "id_pedido": data.get("id_pedido"),
                    "producto": data.get("producto"),
                    "variante": data.get("variante"),
                    "cantidad": data.get("cantidad", 1)
                }
            )

            db.commit()
            return jsonify({"ok": True})

        except Exception as e:
            db.rollback()
            print("🔥 BOT item:", e)
            return jsonify({"error": str(e)}), 500

        finally:
            db.close()


    @app.get("/api/bot/pedido/<int:id_pedido>")
    def bot_ver_pedido(id_pedido):
        db = SessionLocal()

        try:
            result = db.execute(
                text("""
                    SELECT
                        p.NOMBRE AS producto,
                        v.NOMBRE AS variante,
                        d.CANTIDAD
                    FROM BT_PEDIDOS_DETALLE d
                    JOIN BT_PRODUCTOS p ON p.ID_PRODUCTO = d.ID_PRODUCTO
                    JOIN BT_PRODUCTOS_VARIANTES v ON v.ID_VARIANTE = d.ID_VARIANTE
                    WHERE d.ID_PEDIDO = :id
                """),
                {"id": id_pedido}
            )

            items = [
                {k.lower(): v for k, v in r._mapping.items()}
                for r in result
            ]

            return jsonify({
                "id_pedido": id_pedido,
                "items": items
            })

        except Exception as e:
            print("🔥 BOT ver pedido:", e)
            return jsonify({"error": str(e)}), 500

        finally:
            db.close()


    @app.post("/api/bot/pedido/cerrar")
    def bot_cerrar_pedido():
        data = request.json
        db = SessionLocal()

        try:
            db.execute(
                text("""
                    UPDATE BT_PEDIDOS
                    SET ESTATUS = 'cerrado'
                    WHERE ID_PEDIDO = :id
                """),
                {"id": data.get("id_pedido")}
            )

            db.commit()
            return jsonify({"ok": True})

        except Exception as e:
            db.rollback()
            print("🔥 BOT cerrar:", e)
            return jsonify({"error": str(e)}), 500

        finally:
            db.close()

    # =========================================================

    @app.route('/')
    def index():
        discos = get_drives_info()
        return render_template("index.html", discos=discos)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
