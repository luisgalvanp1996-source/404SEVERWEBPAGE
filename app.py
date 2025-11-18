from flask import Flask, render_template, send_from_directory
import os
import psutil
import win32api  # para obtener el nombre del volumen en Windows

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

        # Nombre del volumen (por ejemplo: "SSD Sistema", "Datos", etc.)
        try:
            volume_name = win32api.GetVolumeInformation(p.mountpoint)[0]
            if not volume_name:
                volume_name = "Sin nombre"
        except Exception:
            volume_name = "Desconocido"

        drives_info.append({
            "path": p.mountpoint,  # ejemplo: "C:\\"
            "label": volume_name,  # ejemplo: "SSD Sistema"
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

    app.register_blueprint(biblia_bp)
    app.register_blueprint(medico_bp)
    app.register_blueprint(finanzas_bp)

    @app.route('/')
    def index():
        discos = get_drives_info()
        return render_template("index.html", discos=discos)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
