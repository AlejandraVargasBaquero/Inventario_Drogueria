"""Rutas de la aplicación web."""

import hmac
import secrets
from datetime import date

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.datos.repositorio import (
    cambiar_cantidad_lote,
    cambiar_minimo,
    eliminar_lote,
    eliminar_medicamento,
    guardar_lote,
    guardar_medicamento,
    listar_lotes,
    listar_medicamentos,
)
from app.reglas.existencias import cajas_vigentes, es_vigente
from app.reglas.pedidos import productos_por_pedir
from app.web import obtener_bd
from app.web.formularios import texto_a_entero, texto_a_fecha

bp = Blueprint("web", __name__)

MENSAJE_ELIGE_MEDICAMENTO = "Elige un medicamento"


def hoy() -> date:
    return current_app.config["HOY"] or date.today()


# ---------- Token de los formularios (CSRF) ----------

@bp.before_app_request
def revisar_token():
    """Todo POST debe traer el token de la sesión; si no, 400 y no se guarda nada."""
    if request.method != "POST":
        return
    esperado = session.get("csrf", "")
    recibido = request.form.get("csrf", "")
    if not esperado or not hmac.compare_digest(esperado, recibido):
        abort(400)


@bp.app_context_processor
def token_del_formulario():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return {"csrf": session["csrf"]}


# ---------- Pantallas ----------

@bp.get("/")
def por_pedir():
    """HU-05: medicamentos con menos cajas vigentes que su mínimo."""
    bd = obtener_bd()
    productos = productos_por_pedir(listar_medicamentos(bd), listar_lotes(bd), hoy())
    return render_template("por_pedir.html", productos=productos, hoy=hoy())


@bp.get("/inventario")
def inventario():
    """Medicamentos con su mínimo y cajas vigentes, lotes y formularios de registro."""
    bd = obtener_bd()
    medicamentos = listar_medicamentos(bd)
    lotes = listar_lotes(bd)
    nombres = {m.id: m.nombre for m in medicamentos}
    filas_medicamentos = [
        {"medicamento": m, "vigentes": cajas_vigentes(m.id, lotes, hoy())}
        for m in medicamentos
    ]
    filas_lotes = [
        {
            "lote": lote,
            "nombre": nombres[lote.medicamento_id],
            "vigente": es_vigente(lote, hoy()),
        }
        for lote in lotes
    ]
    return render_template(
        "inventario.html",
        medicamentos=filas_medicamentos,
        lotes=filas_lotes,
        hoy=hoy(),
    )


# ---------- Formularios ----------

@bp.post("/medicamentos")
def registrar_medicamento():
    nombre = request.form.get("nombre", "")
    try:
        guardar_medicamento(
            obtener_bd(), nombre, texto_a_entero(request.form.get("minimo"))
        )
    except ValueError as error:
        flash(str(error), "error")
    else:
        flash(f"Se registró {nombre.strip()}", "ok")
    return redirect(url_for("web.inventario"))


@bp.post("/medicamentos/<int:medicamento_id>/minimo")
def cambiar_minimo_de_medicamento(medicamento_id: int):
    """HU-05, escenario 2: un mínimo inválido no se guarda y se muestra el mensaje."""
    nuevo = texto_a_entero(request.form.get("minimo"))
    bd = obtener_bd()
    try:
        cambiar_minimo(bd, medicamento_id, nuevo)
    except ValueError as error:
        flash(str(error), "error")
    else:
        nombres = {m.id: m.nombre for m in listar_medicamentos(bd)}
        flash(f"Se cambió el mínimo de {nombres[medicamento_id]} a {nuevo}", "ok")
    return redirect(url_for("web.inventario"))


@bp.post("/lotes")
def registrar_lote():
    medicamento_id = texto_a_entero(request.form.get("medicamento_id"))
    numero = request.form.get("numero_lote", "")
    if medicamento_id is None:
        flash(MENSAJE_ELIGE_MEDICAMENTO, "error")
        return redirect(url_for("web.inventario"))
    try:
        guardar_lote(
            obtener_bd(),
            medicamento_id,
            numero,
            texto_a_fecha(request.form.get("fecha_vencimiento")),
            texto_a_entero(request.form.get("cantidad")),
        )
    except ValueError as error:
        flash(str(error), "error")
    else:
        flash(f"Se registró el lote {numero.strip()}", "ok")
    return redirect(url_for("web.inventario"))


@bp.post("/lotes/cantidad")
def cambiar_cantidad_de_lote():
    medicamento_id = texto_a_entero(request.form.get("medicamento_id"))
    numero = request.form.get("numero_lote", "")
    nueva = texto_a_entero(request.form.get("cantidad"))
    if medicamento_id is None:
        flash(MENSAJE_ELIGE_MEDICAMENTO, "error")
        return redirect(url_for("web.inventario"))
    try:
        cambiar_cantidad_lote(obtener_bd(), medicamento_id, numero, nueva)
    except ValueError as error:
        flash(str(error), "error")
    else:
        flash(f"Se cambió la cantidad del lote {numero} a {nueva}", "ok")
    return redirect(url_for("web.inventario"))


@bp.post("/lotes/eliminar")
def eliminar_un_lote():
    medicamento_id = texto_a_entero(request.form.get("medicamento_id"))
    numero = request.form.get("numero_lote", "")
    if medicamento_id is None:
        flash(MENSAJE_ELIGE_MEDICAMENTO, "error")
        return redirect(url_for("web.inventario"))
    try:
        eliminar_lote(obtener_bd(), medicamento_id, numero)
    except ValueError as error:
        flash(str(error), "error")
    else:
        flash(f"Se eliminó el lote {numero}", "ok")
    return redirect(url_for("web.inventario"))


@bp.post("/medicamentos/<int:medicamento_id>/eliminar")
def eliminar_un_medicamento(medicamento_id: int):
    bd = obtener_bd()
    nombres = {m.id: m.nombre for m in listar_medicamentos(bd)}
    try:
        lotes = eliminar_medicamento(bd, medicamento_id)
    except ValueError as error:
        flash(str(error), "error")
    else:
        flash(f"Se eliminó {nombres[medicamento_id]} y sus {lotes} lotes", "ok")
    return redirect(url_for("web.inventario"))
