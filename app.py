from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import psutil
import win32api
from datetime import datetime

# Importa tu modelo y la sesión correcta
from database.connection import SessionLocal
from database.models import DeviceClientInfo

# Importa tus módulos
from modules.biblia.routes import bp as biblia_bp
from modules.medico.routes import bp as medico_bp
from modules.finanzas.routes import bp as finanzas_bp


def get_drives_info():
    """Obtiene información de los discos: letra, nombre, total, usado y libre."""
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
            volume_name = win32api.GetVolumeInformation(p.mountpoint)[0]
            if not volume_name:
                volume_name = "Sin nombre"
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

    DATA_FOLDER = os.path.join(os.getcwd(), "Data")

    @app.route('/Data/<path:filename>')
    def data_files(filename):
        return send_from_directory(DATA_FOLDER, filename)

    app.secret_key = "F1c9fE71A2b4D8e3_99D4-a7C6Ff2B1eE3c8_44D9E1aaFF7283cCbD91E0fA2bC6d"

    # Blueprints
    app.register_blueprint(biblia_bp)
    app.register_blueprint(medico_bp)
    app.register_blueprint(finanzas_bp)

    # -----------------------------------------------------------
    # 📌 ENDPOINT PARA GUARDAR INFORMACIÓN DEL DISPOSITIVO
    # -----------------------------------------------------------
    @app.post("/api/deviceinfo")
    def save_device_info():
        data = request.json
        db = SessionLocal()

        try:
            record = DeviceClientInfo(
                user_agent=data.get("userAgent"),
                platform=data.get("platform"),
                language=data.get("language"),
                timezone=data.get("timezone"),
                screen_width=data.get("screenWidth"),
                screen_height=data.get("screenHeight"),
                available_width=data.get("availableWidth"),
                available_height=data.get("availableHeight"),
                color_depth=data.get("colorDepth"),
                pixel_ratio=data.get("pixelRatio"),
                touch_points=data.get("maxTouchPoints"),
                orientation=data.get("orientation"),
                vendor=data.get("vendor"),
                hardware_concurrency=data.get("hardwareConcurrency"),
                memory_gb=data.get("memoryGB"),
                connection_effective_type=data.get("connectionEffectiveType"),
                connection_rtt=data.get("connectionRTT"),
                connection_downlink=data.get("connectionDownlink"),
                created_at=datetime.now()
            )

            db.add(record)
            db.commit()
            db.refresh(record)

            return jsonify({"msg": "OK", "id": record.id})

        except Exception as e:
            print("🔥 ERROR en /api/deviceinfo:", e)  # 👈 AQUI SE AGREGA
            db.rollback()
            return jsonify({"error": str(e)}), 500

        finally:
            db.close()

    # -----------------------------------------------------------

    @app.route('/')
    def index():
        discos = get_drives_info()
        return render_template("index.html", discos=discos)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
