from flask import Blueprint, render_template, request, redirect, flash, jsonify, current_app
from database.connection import SessionLocal
from database.models_medico import (
    CatMedicamentosMedico,
    DatConsultasMedico,
    DatMedicamentosMedico,
    DatArchivosMedico,
    CatMedicosMedico,
    CatClinicasMedico,
    CatEventosMedico,
    CatImportanciaMedico,
)
import os, uuid
from werkzeug.utils import secure_filename

bp = Blueprint('medico', __name__, url_prefix="/medico")

# Carpeta base para subir archivos (Data/MEDICO/...)
UPLOAD_ROOT = os.path.join(os.getcwd(), "Data", "MEDICO")

EXT_MAP = {
    # imágenes
    ".jpg":  {"folder": "IMAGEN",   "tipo_id": 1},
    ".jpeg": {"folder": "IMAGEN",   "tipo_id": 1},
    ".png":  {"folder": "IMAGEN",   "tipo_id": 1},
    ".gif":  {"folder": "IMAGEN",   "tipo_id": 1},

    # documentos
    ".pdf":  {"folder": "DOCUMENTO","tipo_id": 2},
    ".docx": {"folder": "DOCUMENTO","tipo_id": 2},
    ".doc":  {"folder": "DOCUMENTO","tipo_id": 2},
    ".txt":  {"folder": "DOCUMENTO","tipo_id": 2},

    # video
    ".mp4":  {"folder": "VIDEO",    "tipo_id": 3},
    ".mov":  {"folder": "VIDEO",    "tipo_id": 3},
    ".mkv":  {"folder": "VIDEO",    "tipo_id": 3},

    # audio
    ".mp3":  {"folder": "AUDIO",    "tipo_id": 4},
    ".wav":  {"folder": "AUDIO",    "tipo_id": 4},
}

def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# -------------------------
# INDEX / DASHBOARD
# -------------------------
@bp.route("/")
def index():
    session = SessionLocal()
    try:
        # últimas 3 citas por fecha descendente
        ultimas = (
            session.query(DatConsultasMedico)
            .order_by(DatConsultasMedico.fecha.desc())
            .limit(3)
            .all()
        )

        # para los formularios (selects)
        medicos = session.query(CatMedicosMedico).order_by(CatMedicosMedico.nombre).all()
        clinicas = session.query(CatClinicasMedico).order_by(CatClinicasMedico.unidad_medica).all()
        eventos = session.query(CatEventosMedico).order_by(CatEventosMedico.evento).all()
        importancias = session.query(CatImportanciaMedico).order_by(CatImportanciaMedico.importancia).all()
        medicamentos = session.query(CatMedicamentosMedico).order_by(CatMedicamentosMedico.medicamento).all()

        # todas las consultas (para la sección detalle)
        todas = session.query(DatConsultasMedico).order_by(DatConsultasMedico.fecha.desc()).all()

        return render_template(
            "medico/index.html",
            ultimas=ultimas,
            consultas=todas,
            medicos=medicos,
            clinicas=clinicas,
            eventos=eventos,
            importancias=importancias,
            medicamentos=medicamentos,
        )
    finally:
        session.close()

# -------------------------
# API: traer archivos de una consulta (para modal)
# -------------------------
@bp.route("/api/archivos")
def api_archivos():
    aprendizaje_id = request.args.get("id")
    session = SessionLocal()
    try:
        datos = (
            session.query(
                DatArchivosMedico.id,
                DatArchivosMedico.archivo_id,
                DatArchivosMedico.ubicacion
            )
            .filter(DatArchivosMedico.movimiento_id == aprendizaje_id)
            .all()
        )

        respuesta = []
        for d in datos:
            respuesta.append({
                "id": d.id,
                "tipo": d.archivo_id,       # 1 imagen, 2 doc, 3 video, 4 audio
                "ubicacion": d.ubicacion,   # ruta relativa
            })
        return jsonify(respuesta)
    finally:
        session.close()

# -------------------------
# Registrar nueva consulta (POST)
# -------------------------
@bp.route("/registrar_consulta", methods=["POST"])
def registrar_consulta():
    session = SessionLocal()

    # campos esperados del formulario
    fecha = request.form.get("fecha")  # espera 'YYYY-MM-DD' o ISO
    evento_id = request.form.get("evento_id")
    importancia_id = request.form.get("importancia_id")
    unidad_medica_id = request.form.get("unidad_medica_id")
    medico_id = request.form.get("medico_id")
    observaciones = request.form.get("observaciones", "")

    # medicamentos (select multiple) puede venir como lista
    medicamentos_sel = request.form.getlist("medicamentos[]") or request.form.getlist("medicamentos")

    # validaciones mínimas
    if not (fecha and medico_id and unidad_medica_id):
        flash("Fecha, médico y clínica son obligatorios.", "danger")
        session.close()
        return redirect("/medico/")

    try:
        # crear registro
        nueva = DatConsultasMedico(
            fecha = fecha,
            modulo_id = 1,
            evento_id = int(evento_id) if evento_id else None,
            importancia_id = int(importancia_id) if importancia_id else None,
            unidad_medica_id = int(unidad_medica_id),
            medico_id = int(medico_id),
            observaciones = observaciones
        )
        session.add(nueva)
        session.flush()  # para obtener nueva.id
        consulta_id = nueva.id

        # manejar archivos subidos
        files = request.files.getlist("archivos")
        if files:
            ensure_folder(UPLOAD_ROOT)
            for f in files:
                if f and f.filename:
                    nombre_original = secure_filename(f.filename)
                    _, ext = os.path.splitext(nombre_original)
                    ext = ext.lower()
                    if ext not in EXT_MAP:
                        flash(f"Tipo no permitido: {nombre_original}", "warning")
                        continue

                    meta = EXT_MAP[ext]
                    carpeta = meta["folder"]
                    tipo_archivo_id = meta["tipo_id"]
                    carpeta_dest = os.path.join(UPLOAD_ROOT, carpeta)
                    ensure_folder(carpeta_dest)

                    # generar UUID y checar que no exista
                    while True:
                        nuevo_nombre = f"{uuid.uuid4()}{ext}"
                        ruta_fisica = os.path.join(carpeta_dest, nuevo_nombre)
                        if not os.path.exists(ruta_fisica):
                            break

                    try:
                        f.save(ruta_fisica)
                    except Exception as e:
                        flash(f"Error guardando archivo {nombre_original}: {e}", "warning")
                        continue

                    ruta_relativa = os.path.join("Data", "MEDICO", carpeta, nuevo_nombre).replace("\\","/")
                    archivo_reg = DatArchivosMedico(
                        movimiento_id = consulta_id,
                        archivo_id = tipo_archivo_id,
                        ubicacion = ruta_relativa
                    )
                    session.add(archivo_reg)

        # relacionar medicamentos si llegaron
        for med in medicamentos_sel:
            try:
                med_id = int(med)
            except:
                continue
            dm = DatMedicamentosMedico(
                consulta_id = consulta_id,
                medicamento_id = med_id
            )
            session.add(dm)

        session.commit()
        flash("Consulta registrada correctamente.", "success")
    except Exception as e:
        session.rollback()
        flash(f"Error al registrar consulta: {e}", "danger")
    finally:
        session.close()

    return redirect("/medico/")

# -------------------------
# Registrar médico, clínica o medicamento (endpoints simples POST)
# -------------------------
@bp.route("/registrar_medico", methods=["POST"])
def registrar_medico():
    nombre = request.form.get("nombre")
    if not nombre:
        flash("Nombre de médico requerido.", "danger")
        return redirect("/medico/")
    session = SessionLocal()
    try:
        nuevo = CatMedicosMedico(nombre=nombre)
        session.add(nuevo)
        session.commit()
        flash("Médico registrado.", "success")
    except Exception as e:
        session.rollback()
        flash(f"Error al registrar médico: {e}", "danger")
    finally:
        session.close()
    return redirect("/medico/")

@bp.route("/registrar_clinica", methods=["POST"])
def registrar_clinica():
    nombre = request.form.get("nombre")
    if not nombre:
        flash("Nombre de clínica requerido.", "danger")
        return redirect("/medico/")
    session = SessionLocal()
    try:
        nuevo = CatClinicasMedico(unidad_medica=nombre)
        session.add(nuevo)
        session.commit()
        flash("Clínica registrada.", "success")
    except Exception as e:
        session.rollback()
        flash(f"Error al registrar clínica: {e}", "danger")
    finally:
        session.close()
    return redirect("/medico/")

@bp.route("/registrar_medicamento", methods=["POST"])
def registrar_medicamento():
    nombre = request.form.get("nombre")
    if not nombre:
        flash("Nombre de medicamento requerido.", "danger")
        return redirect("/medico/")
    session = SessionLocal()
    try:
        nuevo = CatMedicamentosMedico(medicamento=nombre)
        session.add(nuevo)
        session.commit()
        flash("Medicamento registrado.", "success")
    except Exception as e:
        session.rollback()
        flash(f"Error al registrar medicamento: {e}", "danger")
    finally:
        session.close()
    return redirect("/medico/")

@bp.route("/api/medicamentos/<int:consulta_id>")
def api_medicamentos(consulta_id):
    session = SessionLocal()
    try:
        medicamentos = (
            session.query(DatMedicamentosMedico, CatMedicamentosMedico)
            .join(CatMedicamentosMedico, DatMedicamentosMedico.medicamento_id == CatMedicamentosMedico.id)
            .filter(DatMedicamentosMedico.consulta_id == consulta_id)
            .all()
        )

        lista = [{"id": m[0].id, "medicamento": m[1].medicamento} for m in medicamentos]

        return {"success": True, "medicamentos": lista}

    finally:
        session.close()

@bp.route("/api/detalle/<int:consulta_id>")
def api_detalle(consulta_id):
    session = SessionLocal()
    try:
        c = session.query(DatConsultasMedico).filter(DatConsultasMedico.id == consulta_id).first()
        if not c:
            return jsonify({"error": "Consulta no encontrada"}), 404

        # buscar textos de los catálogos
        medico = session.query(CatMedicosMedico).filter(CatMedicosMedico.id == c.medico_id).first()
        clinica = session.query(CatClinicasMedico).filter(CatClinicasMedico.id == c.unidad_medica_id).first()
        evento = session.query(CatEventosMedico).filter(CatEventosMedico.id == c.evento_id).first()
        importancia = session.query(CatImportanciaMedico).filter(CatImportanciaMedico.id == c.importancia_id).first()

        resp = {
            "id": c.id,
            "fecha": str(c.fecha) if c.fecha else "",
            "evento": evento.evento if evento else "",
            "importancia": importancia.importancia if importancia else "",
            "clinica": clinica.unidad_medica if clinica else "",
            "medico": medico.nombre if medico else "",
            "observaciones": c.observaciones or ""
        }
        return jsonify(resp)

    finally:
        session.close()

