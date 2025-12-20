from flask import Blueprint, render_template, request, jsonify, redirect, flash,current_app,url_for,send_from_directory
from database.connection import SessionLocal
from database.models_biblia import CatLibrosBiblia, DatAprendizajeBiblia, Biblia, DatArchivosBiblia,DatTagsBiblia,CatTagsBiblia,CatTagsTipoBiblia
import os
import uuid
from werkzeug.utils import secure_filename
from sqlalchemy import select

bp = Blueprint('biblia', __name__, url_prefix="/biblia")

UPLOAD_ROOT = os.path.join(os.getcwd(), "Data", "biblia")
RESOURCES_ROOT = os.path.join(os.getcwd(), "resources")


# Extensiones permitidas y mapeo a carpeta + ID de CAT_ARCHIVO_TIPO
EXT_MAP = {
    # imágenes
    ".jpg":  {"folder": "imagen",   "tipo_id": 1},
    ".jpeg": {"folder": "imagen",   "tipo_id": 1},
    ".png":  {"folder": "imagen",   "tipo_id": 1},
    ".gif":  {"folder": "imagen",   "tipo_id": 1},

    # documentos
    ".pdf":  {"folder": "documento","tipo_id": 2},
    ".docx": {"folder": "documento","tipo_id": 2},
    ".doc":  {"folder": "documento","tipo_id": 2},
    ".txt":  {"folder": "documento","tipo_id": 2},

    # video
    ".mp4":  {"folder": "video",    "tipo_id": 3},
    ".mov":  {"folder": "video",    "tipo_id": 3},
    ".mkv":  {"folder": "video",    "tipo_id": 3},

    # audio
    ".mp3":  {"folder": "audio",    "tipo_id": 4},
    ".wav":  {"folder": "audio",    "tipo_id": 4},
}

def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# ======================================
# INDEX PRINCIPAL
# ======================================
@bp.route("/")
def index():
    session = SessionLocal()
    try:
        # Cargar aprendizajes existentes
        aprendizajes = (
            session.query(DatAprendizajeBiblia)
            .order_by(DatAprendizajeBiblia.id.desc())
            .all()
        )

        # Cargar libros del catálogo
        libros = (
            session.query(CatLibrosBiblia)
            .order_by(CatLibrosBiblia.nombre)
            .all()
        )

        return render_template(
            "biblia/index.html",
            aprendizajes=aprendizajes,
            libros=libros
        )
    finally:
        session.close()



# ======================================
# CARGAR FORMULARIO
# ======================================
#@bp.route("/registrar", methods=["GET"])
#def registrar():
#    session = SessionLocal()
#    libros = session.query(CatLibrosBiblia).order_by(CatLibrosBiblia.nombre).all()
#    session.close()
#    return render_template("biblia/index.html", libros=libros)



# ======================================
# API — CAPÍTULOS
# ======================================
@bp.route("/api/capitulos")
def api_capitulos():
    libro = request.args.get("libro")

    session = SessionLocal()
    capitulos = (
        session.query(Biblia.capitulo)
        .filter(Biblia.libro == libro)
        .distinct()
        .order_by(Biblia.capitulo)
        .all()
    )
    session.close()

    return jsonify([c[0] for c in capitulos])


# ======================================
# API — VERSÍCULOS
# ======================================
@bp.route("/api/versiculos")
def api_versiculos():
    libro = request.args.get("libro")
    cap = request.args.get("capitulo")

    session = SessionLocal()
    versiculos = (
        session.query(Biblia.versiculo)
        .filter(Biblia.libro == libro, Biblia.capitulo == cap)
        .distinct()
        .order_by(Biblia.versiculo)
        .all()
    )
    session.close()

    return jsonify([v[0] for v in versiculos])


# ======================================
# INSERTAR TEXTO DE APRENDIZAJE
# ======================================
@bp.route("/registrar", methods=["POST"])
def registrar_post():
    # datos del formulario
    libro_nombre = request.form.get("libro")
    cap_str = request.form.get("capitulo")
    ini_str = request.form.get("versiculoinicio")
    fin_str = request.form.get("versiculofin")
    texto = request.form.get("texto", "")

    # validaciones mínimas
    if not (libro_nombre and cap_str and ini_str and fin_str and texto):
        flash("Faltan campos obligatorios.", "danger")
        return redirect(url_for("biblia.index"))

    try:
        cap = int(cap_str)
        ini = int(ini_str)
        fin = int(fin_str)
    except ValueError:
        flash("Capítulo/versículos deben ser números.", "danger")
        return redirect(url_for("biblia.index"))

    session = SessionLocal()
    try:
        # obtener ID del libro
        libro_id = session.query(CatLibrosBiblia.id).filter(
            CatLibrosBiblia.nombre == libro_nombre
        ).scalar()

        if not libro_id:
            flash("Libro no encontrado en catálogo.", "danger")
            return redirect(url_for("biblia.index"))

        # crear registro de aprendizaje
        nuevo = DatAprendizajeBiblia(
            tipo_id=1,
            libro_id=libro_id,
            capitulo=cap,
            versiculo_inicio=ini,
            versiculo_fin=fin,
            modulo_id=1,
            texto=texto
        )
        session.add(nuevo)
        session.flush()  # para obtener ID sin hacer commit aún
        aprendizaje_id = nuevo.id

        # --- procesamiento de archivos ---
        files = request.files.getlist("archivos")
        if files:
            # asegurar carpeta base
            ensure_folder(UPLOAD_ROOT)

            for f in files:
                if f and f.filename:
                    nombre_original = secure_filename(f.filename)
                    _, ext = os.path.splitext(nombre_original)
                    ext = ext.lower()

                    if ext not in EXT_MAP:
                        # rechazar archivo no permitido
                        # puedes cambiar a flash + continuar, aquí optamos por ignorar y saltar
                        flash(f"Tipo de archivo no permitido: {nombre_original}", "warning")
                        continue

                    meta = EXT_MAP[ext]
                    carpeta = meta["folder"]
                    tipo_archivo_id = meta["tipo_id"]

                    carpeta_dest = os.path.join(UPLOAD_ROOT, carpeta)
                    ensure_folder(carpeta_dest)

                    # generar UUID único como nombre del archivo
                    while True:
                        nuevo_nombre = f"{uuid.uuid4()}{ext}"
                        ruta_relativa = os.path.join("Data", "biblia", carpeta, nuevo_nombre).replace("\\", "/")
                        ruta_fisica = os.path.join(carpeta_dest, nuevo_nombre)
                        if not os.path.exists(ruta_fisica):
                            break  # nombre único

                    # guardar archivo físicamente
                    try:
                        f.save(ruta_fisica)
                    except Exception as e:
                        # si falla el guardado, registrar aviso y continuar
                        flash(f"Error guardando archivo {nombre_original}: {e}", "warning")
                        continue

                    # insertar registro en DAT_ARCHIVOS_BIBLIA
                    archivo_reg = DatArchivosBiblia(
                        movimiento_id=aprendizaje_id,
                        archivo_id=tipo_archivo_id,
                        ubicacion=ruta_relativa
                    )
                    session.add(archivo_reg)

        # terminar transacción
        session.commit()
        flash("Aprendizaje y archivos registrados correctamente.", "success")
        return redirect(url_for("biblia.index"))

    except Exception as exc:
        session.rollback()
        flash(f"Error al guardar: {exc}", "danger")
        return redirect(url_for("biblia.index"))
    finally:
        session.close()

@bp.route("/api/aprendizajes")
def api_aprendizajes():
    session = SessionLocal()

    # JOIN con catálogo de libros
    datos = session.query(
        DatAprendizajeBiblia.id,
        CatLibrosBiblia.nombre,
        CatLibrosBiblia.abreviatura,
        DatAprendizajeBiblia.capitulo,
        DatAprendizajeBiblia.versiculo_inicio,
        DatAprendizajeBiblia.versiculo_fin,
        DatAprendizajeBiblia.texto
    ).join(
        CatLibrosBiblia, DatAprendizajeBiblia.libro_id == CatLibrosBiblia.id
    ).order_by(
        DatAprendizajeBiblia.id.desc()
    ).all()

    session.close()

    # Convertir a JSON
    respuesta = []
    for d in datos:
        respuesta.append({
            "id": d.id,
            "nombre": d.nombre,
            "abreviatura": d.abreviatura,
            "capitulo": d.capitulo,
            "ini": d.versiculo_inicio,
            "fin": d.versiculo_fin,
            "texto": d.texto
        })

    return jsonify(respuesta)

@bp.route("/api/archivos")
def api_archivos():
    aprendizaje_id = request.args.get("id")

    session = SessionLocal()

    datos = session.query(
        DatArchivosBiblia.id,
        DatArchivosBiblia.archivo_id,
        DatArchivosBiblia.ubicacion,
        DatAprendizajeBiblia.texto
    ).join(
        DatAprendizajeBiblia,
        DatAprendizajeBiblia.id == DatArchivosBiblia.movimiento_id
    ).filter(
        DatArchivosBiblia.movimiento_id == aprendizaje_id
    ).all()

    session.close()

    respuesta = []
    for d in datos:
        respuesta.append({
            "id": d.id,
            "tipo": int(d.archivo_id),                        # <-- convertir a INT
            "ubicacion": d.ubicacion.replace("\\", "/"),      # <-- corregir slashes
        })

    return jsonify(respuesta)

@bp.route('/obtener_versiculos/<int:id_aprendizaje>')
def obtener_versiculos(id_aprendizaje):
    session = SessionLocal()

    # 1) Buscar el aprendizaje
    apr = session.query(DatAprendizajeBiblia).filter_by(id=id_aprendizaje).first()
    if not apr:
        session.close()
        return {"error": "No encontrado"}, 404

    libro_id = apr.libro_id
    cap = apr.capitulo
    ini = apr.versiculo_inicio
    fin = apr.versiculo_fin

    # 2) Obtener nombre del libro
    libro = session.query(CatLibrosBiblia).filter_by(id=libro_id).first()

    # 3) Buscar versículos del rango
    versos = session.query(Biblia).filter(
        Biblia.libronumero == libro_id,
        Biblia.capitulo == cap,
        Biblia.versiculo.between(ini, fin)
    ).order_by(Biblia.versiculo.asc()).all()

    session.close()

    # 4) Armar textual limpio
    lineas = []
    for v in versos:
        lineas.append(v.texto.strip())

    texto_unido = "\n\n".join(lineas)

    cabecera = f"{libro.nombre} {cap}:{ini}-{fin}"

    return {
        "cabecera": cabecera,
        "texto": texto_unido
    }


@bp.route("/api/resources")
def api_resources():
    rel_path = request.args.get("path", "")
    
    base = os.path.abspath(RESOURCES_ROOT)
    target = os.path.abspath(os.path.join(base, rel_path))

    # 🔐 Seguridad: no salir de /resources
    if not target.startswith(base):
        return {"error": "Acceso no permitido"}, 403

    if not os.path.exists(target):
        return {"items": []}

    items = []
    for name in os.listdir(target):
        full = os.path.join(target, name)
        items.append({
            "name": name,
            "type": "folder" if os.path.isdir(full) else "file",
            "path": os.path.join(rel_path, name).replace("\\", "/")
        })

    # Carpetas primero
    items.sort(key=lambda x: (x["type"] != "folder", x["name"].lower()))

    return {"items": items}


@bp.route("/descargar/<path:archivo>")
def descargar_archivo(archivo):
    base = os.path.abspath(RESOURCES_ROOT)
    full = os.path.abspath(os.path.join(base, archivo))

    if not full.startswith(base):
        return "Acceso denegado", 403

    carpeta = os.path.dirname(full)
    nombre = os.path.basename(full)

    return send_from_directory(carpeta, nombre, as_attachment=True)


