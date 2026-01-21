from flask import Flask, render_template, send_from_directory, request, jsonify
from sqlalchemy import text
import os
import psutil
import win32api
from dotenv import load_dotenv

# Importa tu sesión
from database.connection import SessionLocal

# Importa tus módulos existentes
from modules.biblia.routes import bp as biblia_bp
from modules.medico.routes import bp as medico_bp
from modules.finanzas.routes import bp as finanzas_bp
from modules.personal.routes import bp as personal_bp

#importa el blueprint del bot telegram
from bot.routes import bp as bot_bp



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

    load_dotenv()
    app.secret_key = os.getenv("SECRET_KEY")

    DATA_FOLDER = os.path.join(os.getcwd(), "Data")

    @app.route('/Data/<path:filename>')
    def data_files(filename):
        return send_from_directory(DATA_FOLDER, filename)

    # Blueprints
    app.register_blueprint(biblia_bp)
    app.register_blueprint(medico_bp)
    app.register_blueprint(finanzas_bp)
    app.register_blueprint(personal_bp)
    app.register_blueprint(bot_bp)

    
    # =========================================================

    @app.route('/')
    def index():
        discos = get_drives_info()
        return render_template("index.html", discos=discos)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
