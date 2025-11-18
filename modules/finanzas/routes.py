# modules/finanzas/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from database.connection import SessionLocal
from database.models_finanzas import DatMovimientosFinanzas, CatConceptosFinanzas, CatProveedoresFinanzas, DatArchivosFinanzas
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
import os, uuid
from datetime import date, timedelta, datetime

bp = Blueprint('finanzas', __name__, url_prefix="/finanzas")

# Rutas de almacenamiento
UPLOAD_ROOT = os.path.join(os.getcwd(), "Data", "Finanzas")
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
    # videos
    ".mp4":  {"folder": "video",    "tipo_id": 3},
    ".mov":  {"folder": "video",    "tipo_id": 3},
    ".mkv":  {"folder": "video",    "tipo_id": 3},
    # audios
    ".mp3":  {"folder": "audio",    "tipo_id": 4},
    ".wav":  {"folder": "audio",    "tipo_id": 4},
}

def ensure_folder(path):
    os.makedirs(path, exist_ok=True)

# -------------------------
# Helpers de fecha semana
# -------------------------
def week_start_by_friday(target: date) -> date:
    # Friday is weekday() == 4 (Mon=0)
    days_since_friday = (target.weekday() - 4) % 7
    return target - timedelta(days=days_since_friday)

# --------------------------------
# Página principal del módulo
# --------------------------------
@bp.route("/")
def index():
    session = SessionLocal()
    try:
        # Movimientos — orden ascendente por fecha para cálculo de saldo acumulado
        movimientos_raw = session.query(DatMovimientosFinanzas).order_by(DatMovimientosFinanzas.fecha.asc()).all()

        # Cargar catálogos para formularios (conceptos y proveedores)
        conceptos = session.query(CatConceptosFinanzas).order_by(CatConceptosFinanzas.concepto).all()
        proveedores = session.query(CatProveedoresFinanzas).order_by(CatProveedoresFinanzas.nombre).all()

        # Prepara lista de dicts con factor y cálculo de balance acumulado
        movimientos = []
        saldo_acumulado = 0
        for m in movimientos_raw:
            # buscar factor del concepto
            concepto = session.query(CatConceptosFinanzas).filter(CatConceptosFinanzas.id == m.concepto_id).first()
            factor = int(concepto.factor) if concepto and concepto.factor is not None else 1
            importe = float(m.importe) if m.importe is not None else 0.0
            importe_signed = importe * factor
            saldo_acumulado += importe_signed

            # proveedor nombre
            proveedor = session.query(CatProveedoresFinanzas).filter(CatProveedoresFinanzas.id == m.proveedor_id).first()
            proveedor_nombre = proveedor.nombre if proveedor else ""

            movimientos.append({
                "id": m.id,
                "tipo_movimiento": m.tipo_movimiento,
                "concepto_id": m.concepto_id,
                "concepto": concepto.concepto if concepto else "",
                "proveedor_id": m.proveedor_id,
                "proveedor": proveedor_nombre,
                "fecha": m.fecha,
                "importe": importe,
                "factor": factor,
                "importe_signed": importe_signed,
                "saldo_acumulado": saldo_acumulado
            })

        # --- resumen semanal (desde viernes más reciente) ---
        hoy = date.today()
        ws = week_start_by_friday(hoy)
        we = ws + timedelta(days=6)

        semana_movs = session.query(DatMovimientosFinanzas).filter(DatMovimientosFinanzas.fecha >= ws).filter(DatMovimientosFinanzas.fecha <= we).all()
        ingresos_sem = 0.0
        egresos_sem = 0.0
        for m in semana_movs:
            concepto = session.query(CatConceptosFinanzas).filter(CatConceptosFinanzas.id == m.concepto_id).first()
            factor = int(concepto.factor) if concepto and concepto.factor is not None else 1
            importe = float(m.importe) if m.importe is not None else 0.0
            if factor >= 0:
                ingresos_sem += importe
            else:
                egresos_sem += abs(importe)

        balance_sem = ingresos_sem - egresos_sem

        return render_template(
            "finanzas/index.html",
            movimientos=movimientos,
            conceptos=conceptos,
            proveedores=proveedores,
            ingresos_sem=ingresos_sem,
            egresos_sem=egresos_sem,
            balance_sem=balance_sem,
            semana_inicio=ws,
            semana_fin=we
        )

    except SQLAlchemyError as e:
        flash(f"Error al cargar movimientos financieros: {e}", "danger")
        return render_template("finanzas/index.html", movimientos=[], conceptos=[], proveedores=[])

    finally:
        session.close()

# --------------------------------
# API: obtener archivos asociados a un movimiento
# --------------------------------
@bp.route("/api/archivos")
def api_archivos():
    movimiento_id = request.args.get("id")
    session = SessionLocal()

    datos = session.query(
        DatArchivosFinanzas.id,
        DatArchivosFinanzas.archivo_id,
        DatArchivosFinanzas.ubicacion
    ).filter(DatArchivosFinanzas.movimiento_id == movimiento_id).all()

    session.close()

    respuesta = []
    for d in datos:
        respuesta.append({
            "id": int(d.id),
            "tipo": int(d.archivo_id),
            "ubicacion": d.ubicacion.replace("\\", "/")
        })

    return jsonify(respuesta)

# =====================================================
# REGISTRAR MOVIMIENTO FINANCIERO
# =====================================================
@bp.route("/registrar_movimiento", methods=["POST"])
def registrar_movimiento():
    concepto_id = request.form.get("concepto_id")
    proveedor_id = request.form.get("proveedor_id")
    fecha_str = request.form.get("fecha")
    importe_str = request.form.get("importe")

    # proveedor es opcional
    if proveedor_id == "" or proveedor_id is None:
        proveedor_id = None

    # validar obligatorios
    if not (concepto_id and fecha_str and importe_str):
        flash("Concepto, fecha e importe son obligatorios.", "danger")
        return redirect("/finanzas/")

    try:
        importe = float(importe_str)
    except:
        flash("El importe debe ser numérico.", "danger")
        return redirect("/finanzas/")

    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except:
        flash("Fecha inválida.", "danger")
        return redirect("/finanzas/")

    session = SessionLocal()

    try:
        concepto = session.query(CatConceptosFinanzas).filter_by(id=concepto_id).first()

        if not concepto:
            flash("Concepto no encontrado.", "danger")
            return redirect("/finanzas/")

        factor = concepto.factor
        tipo_movimiento = 4 if factor == 1 else 5

        movimiento = DatMovimientosFinanzas(
            tipo_movimiento=tipo_movimiento,
            concepto_id=concepto_id,
            proveedor_id=proveedor_id,
            fecha=fecha,
            modulo=3,
            importe=importe
        )

        session.add(movimiento)
        session.commit()

        flash("Movimiento registrado correctamente.", "success")
        return redirect("/finanzas/")

    except SQLAlchemyError as e:
        session.rollback()
        flash(f"Error al registrar movimiento: {e}", "danger")
        return redirect("/finanzas/")

    finally:
        session.close()


# --------------------------------
# Registrar proveedor
# --------------------------------
@bp.route("/registrar_proveedor", methods=["POST"])
def registrar_proveedor():
    session = SessionLocal()
    try:
        nombre = request.form.get("nombre", "").strip()

        if not nombre:
            flash("El nombre del proveedor no puede estar vacío.", "danger")
            return redirect("/finanzas/")

        nuevo = CatProveedoresFinanzas(nombre=nombre)
        session.add(nuevo)
        session.commit()

        flash("Proveedor registrado correctamente.", "success")
        return redirect("/finanzas/")
    except Exception as e:
        session.rollback()
        flash(f"Error al registrar proveedor: {e}", "danger")
        return redirect("/finanzas/")
    finally:
        session.close()


# --------------------------------
# Registrar concepto
# --------------------------------
@bp.route("/registrar_concepto", methods=["POST"])
def registrar_concepto():
    session = SessionLocal()
    try:
        concepto = request.form.get("concepto", "").strip()
        factor = request.form.get("factor", "").strip()

        if not concepto:
            flash("El nombre del concepto no puede estar vacío.", "danger")
            return redirect("/finanzas/")

        try:
            factor = int(factor)
            if factor not in (1, -1):
                raise ValueError()
        except:
            flash("El factor debe ser 1 (ingreso) o -1 (egreso).", "danger")
            return redirect("/finanzas/")

        nuevo = CatConceptosFinanzas(concepto=concepto, factor=factor)
        session.add(nuevo)
        session.commit()

        flash("Concepto registrado correctamente.", "success")
        return redirect("/finanzas/")

    except Exception as e:
        session.rollback()
        flash(f"Error al registrar concepto: {e}", "danger")
        return redirect("/finanzas/")
    finally:
        session.close()
