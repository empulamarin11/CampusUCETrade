import os
import json
import uuid
import requests
from behave import given, when, then

@given("tengo la URL base")
def step_base_url(context):
    context.base_url = os.getenv("BASE_URL", "").rstrip("/")
    assert context.base_url, "BASE_URL no está definido (revisa students/campusucetrade/config.env)"

@when('hago un GET a "{path}"')
def step_get(context, path):
    # Reemplazo de variables en URL
    if hasattr(context, "item_title"):
        path = path.replace("{{item_title}}", context.item_title)

    url = context.base_url + path
    context.response = requests.get(url, timeout=20)

@when('hago un POST a "{path}" con JSON')
@when('hago un POST a "{path}" con JSON:')
def step_post_json(context, path):
    raw = context.text  # docstring del feature

    # Reemplazo de variables en JSON
    if hasattr(context, "email"):
        raw = raw.replace("{{email}}", context.email)
    if hasattr(context, "item_title"):
        raw = raw.replace("{{item_title}}", context.item_title)

    data = json.loads(raw)
    url = context.base_url + path
    context.response = requests.post(url, json=data, timeout=20)

@then("la respuesta debe ser {status:d}")
def step_status(context, status):
    r = context.response
    assert r is not None, "No hay respuesta guardada"
    assert r.status_code == status, f"Esperado {status}, llegó {r.status_code}. Body: {r.text}"

@then("la respuesta debe ser uno de {codes}")
def step_status_one_of(context, codes):
    allowed = [int(x.strip()) for x in codes.split(",")]
    r = context.response
    assert r.status_code in allowed, (
        f"Esperado uno de {allowed}, llegó {r.status_code}. Body: {r.text}"
    )

@given("genero un usuario de prueba")
def step_gen_user(context):
    context.email = f"bdd_{uuid.uuid4().hex[:8]}@uce.edu.ec"

@given("registro el usuario de prueba")
def step_register_user(context):
    url = context.base_url + "/users/register"
    payload = {
        "email": context.email,
        "password": "Test1234*",
        "full_name": "Usuario BDD"
    }
    context.response = requests.post(url, json=payload, timeout=20)

@given("genero un nombre de item de prueba")
def step_gen_item_title(context):
    context.item_title = f"bdd-item-{uuid.uuid4().hex[:6]}"

@given("inicio sesión y guardo el token")
def step_login_and_save_token(context):
    url = context.base_url + "/auth/login"
    payload = {"email": context.email, "password": "Test1234*"}
    r = requests.post(url, json=payload, timeout=20)
    context.response = r

    assert r.status_code == 200, f"Login falló: {r.status_code} Body: {r.text}"

    data = r.json()
    # Tolerante: busca el token en varias claves posibles
    context.token = (
        data.get("access_token")
        or data.get("token")
        or data.get("jwt")
        or data.get("accessToken")
    )
    assert context.token, f"No se encontró token en respuesta: {data}"

@given("tengo el header Authorization listo")
def step_set_auth_header(context):
    assert hasattr(context, "token"), "Primero debes iniciar sesión y guardar el token"
    context.headers = {"Authorization": f"Bearer {context.token}"}

@when('hago un POST autenticado a "{path}" con JSON')
@when('hago un POST autenticado a "{path}" con JSON:')
def step_post_json_auth(context, path):
    raw = context.text
    if hasattr(context, "email"):
        raw = raw.replace("{{email}}", context.email)
    if hasattr(context, "item_title"):
        raw = raw.replace("{{item_title}}", context.item_title)

    data = json.loads(raw)
    url = context.base_url + path
    headers = getattr(context, "headers", {})
    context.response = requests.post(url, json=data, headers=headers, timeout=20)