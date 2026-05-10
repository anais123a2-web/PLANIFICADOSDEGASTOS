import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date

st.set_page_config(page_title="Planificador de Gastos", page_icon="💖", layout="wide")

ARCHIVO_DATOS = Path("datos_presupuesto.json")
CLAVE_ARCHIVO = Path("clave_usuario.json")


def cargar_json(ruta, default):
    if ruta.exists():
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def guardar_json(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)


def cargar_clave():
    return cargar_json(CLAVE_ARCHIVO, {}).get("clave")


def guardar_clave(nueva_clave):
    guardar_json(CLAVE_ARCHIVO, {"clave": nueva_clave})


def mes_actual():
    hoy = date.today()
    return f"{hoy.year}-{hoy.month:02d}"


def crear_mes_vacio():
    return {
        "nombre": "",
        "meta_ahorro": 0,
        "notas": "",
        "ingresos": [
            {"Descripción": "Sueldo", "Monto": 0},
            {"Descripción": "Otros ingresos", "Monto": 0},
        ],
        "gastos_fijos": [
            {"Categoría": "Arriendo", "Descripción": "", "Monto": 0},
            {"Categoría": "Luz", "Descripción": "", "Monto": 0},
            {"Categoría": "Agua", "Descripción": "", "Monto": 0},
            {"Categoría": "Internet / Teléfono", "Descripción": "", "Monto": 0},
            {"Categoría": "Mercadería", "Descripción": "", "Monto": 0},
            {"Categoría": "Alimento mascotas", "Descripción": "", "Monto": 0},
        ],
        "gastos_variables": [
            {"Categoría": "Gastos hormiga", "Descripción": "", "Monto": 0},
            {"Categoría": "Gastos personales", "Descripción": "", "Monto": 0},
            {"Categoría": "Comida fuera de casa", "Descripción": "", "Monto": 0},
            {"Categoría": "Transporte", "Descripción": "", "Monto": 0},
        ],
    }


def asegurar_estructura(datos):
    if "meses" not in datos:
        mes = datos.get("mes", mes_actual())
        datos = {
            "mes_actual": mes,
            "meses": {
                mes: {
                    "nombre": datos.get("nombre", ""),
                    "meta_ahorro": datos.get("meta_ahorro", 0),
                    "notas": datos.get("notas", ""),
                    "ingresos": datos.get("ingresos", crear_mes_vacio()["ingresos"]),
                    "gastos_fijos": datos.get("gastos_fijos", crear_mes_vacio()["gastos_fijos"]),
                    "gastos_variables": datos.get("gastos_variables", crear_mes_vacio()["gastos_variables"]),
                }
            },
        }

    if "mes_actual" not in datos:
        datos["mes_actual"] = mes_actual()

    if "meses" not in datos or not isinstance(datos["meses"], dict):
        datos["meses"] = {}

    if datos["mes_actual"] not in datos["meses"]:
        datos["meses"][datos["mes_actual"]] = crear_mes_vacio()

    return datos


def asegurar_columnas(df, columnas):
    for columna in columnas:
        if columna not in df.columns:
            df[columna] = 0 if columna == "Monto" else ""
    return df[columnas]


def limpiar_montos(df):
    if "Monto" in df.columns:
        df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)
    return df


def calcular_mes(datos_mes):
    ingresos = limpiar_montos(asegurar_columnas(pd.DataFrame(datos_mes.get("ingresos", [])), ["Descripción", "Monto"]))
    fijos = limpiar_montos(asegurar_columnas(pd.DataFrame(datos_mes.get("gastos_fijos", [])), ["Categoría", "Descripción", "Monto"]))
    variables = limpiar_montos(asegurar_columnas(pd.DataFrame(datos_mes.get("gastos_variables", [])), ["Categoría", "Descripción", "Monto"]))
    total_ingresos = ingresos["Monto"].sum()
    total_fijos = fijos["Monto"].sum()
    total_variables = variables["Monto"].sum()
    total_gastos = total_fijos + total_variables
    meta = float(datos_mes.get("meta_ahorro", 0) or 0)
    saldo = total_ingresos - total_gastos
    return {
        "Ingresos": total_ingresos,
        "Gastos fijos": total_fijos,
        "Gastos variables": total_variables,
        "Total gastos": total_gastos,
        "Meta ahorro": meta,
        "Saldo": saldo,
    }


datos = asegurar_estructura(cargar_json(ARCHIVO_DATOS, {}))

st.sidebar.title("🔐 Acceso")
clave_guardada = cargar_clave()

if clave_guardada is None:
    st.info("Primero crea una contraseña para proteger tu planificador 💖")
    nueva_clave = st.text_input("Crea tu contraseña", type="password")
    repetir_clave = st.text_input("Repite tu contraseña", type="password")
    if st.button("Crear contraseña"):
        if not nueva_clave:
            st.error("La contraseña no puede estar vacía.")
        elif nueva_clave != repetir_clave:
            st.error("Las contraseñas no coinciden.")
        else:
            guardar_clave(nueva_clave)
            st.success("Contraseña creada correctamente 💖")
            st.rerun()
    st.stop()

clave_ingresada = st.sidebar.text_input("Contraseña", type="password")
if clave_ingresada != clave_guardada:
    st.warning("Ingresa tu contraseña para entrar 💖")
    st.stop()

with st.sidebar.expander("⚙️ Cambiar contraseña"):
    clave_actual = st.text_input("Contraseña actual", type="password")
    nueva_clave = st.text_input("Nueva contraseña", type="password")
    repetir_nueva = st.text_input("Repetir nueva contraseña", type="password")
    if st.button("Actualizar contraseña"):
        if clave_actual != clave_guardada:
            st.error("La contraseña actual no es correcta.")
        elif not nueva_clave:
            st.error("La nueva contraseña no puede estar vacía.")
        elif nueva_clave != repetir_nueva:
            st.error("Las nuevas contraseñas no coinciden.")
        else:
            guardar_clave(nueva_clave)
            st.success("Contraseña actualizada correctamente 💖")
            st.rerun()

st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #fff6fb 0%, #ffeaf4 45%, #fff8fc 100%); color: #321c3b; }
.block-container { padding: 1rem; max-width: 980px; }
h1, h2, h3, label, p { color: #321c3b !important; }
.hero-card { background: linear-gradient(135deg, #fff7fb, #ffd6eb); border: 2px solid #ffc2df; border-radius: 32px; padding: 28px 18px; text-align: center; box-shadow: 0 12px 30px rgba(255, 105, 180, 0.22); margin-bottom: 20px; }
.hero-title { font-size: 46px; line-height: 1.05; font-weight: 900; color: #7b1e5c !important; margin: 0; }
.hero-title span { color: #ff4da6; font-family: Georgia, serif; font-style: italic; }
.hero-subtitle { margin-top: 10px; font-size: 16px; color: #8a4a73 !important; }
[data-testid="stMetric"] { background: linear-gradient(135deg, #ffffff, #fff0f7); border: 2px solid #ffcce5; border-radius: 26px; padding: 18px; box-shadow: 0px 8px 22px rgba(255, 105, 180, 0.18); }
[data-testid="stMetricValue"] { color: #ff4da6; }
[data-testid="stDataEditor"] { border-radius: 24px; border: 2px solid #ffcce5; overflow: hidden; }
.stTabs [data-baseweb="tab"] { background-color: #fff7fb; border: 2px solid #ffcce5; border-radius: 999px; padding: 8px 14px; color: #7b1e5c; font-weight: 800; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #ff8ac7, #ff4da6); color: white !important; }
.stButton>button { background: linear-gradient(135deg, #ff7ac8, #ff4da6); color: white; border-radius: 999px; border: none; padding: 14px 25px; font-weight: 900; width: 100%; }
div[data-baseweb="input"] > div, textarea { border-radius: 20px !important; border: 2px solid #ffcce5 !important; background-color: #fffafd !important; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #ffeaf3, #fff7fb); border-right: 2px solid #ffcce5; }
section[data-testid="stSidebar"] * { color: #7b1e5c !important; }
section[data-testid="stSidebar"] button { background: linear-gradient(135deg, #ff8ac7, #ff4da6); color: white !important; }
@media (max-width: 768px) { .hero-title { font-size: 34px; } .hero-card { padding: 24px 14px; } }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <h1 class="hero-title">Mi Presupuesto <br><span>Bonito</span></h1>
    <p class="hero-subtitle">Organiza tu dinero por mes y compara tus avances</p>
</div>
""", unsafe_allow_html=True)

st.subheader("📅 Mes de trabajo")
meses_ordenados = sorted(datos["meses"].keys(), reverse=True)
mes_seleccionado = st.selectbox("Selecciona un mes guardado", meses_ordenados, index=meses_ordenados.index(datos["mes_actual"]) if datos["mes_actual"] in meses_ordenados else 0)

col_a, col_b = st.columns(2)
with col_a:
    nuevo_mes = st.text_input("Crear nuevo mes", placeholder="Ej: 2026-06")
with col_b:
    st.write("")
    st.write("")
    if st.button("➕ Crear mes"):
        if not nuevo_mes.strip():
            st.error("Escribe un mes, por ejemplo 2026-06.")
        elif nuevo_mes in datos["meses"]:
            st.warning("Ese mes ya existe.")
        else:
            datos["meses"][nuevo_mes] = crear_mes_vacio()
            datos["mes_actual"] = nuevo_mes
            guardar_json(ARCHIVO_DATOS, datos)
            st.success(f"Mes {nuevo_mes} creado.")
            st.rerun()

if mes_seleccionado != datos["mes_actual"]:
    datos["mes_actual"] = mes_seleccionado
    guardar_json(ARCHIVO_DATOS, datos)

mes_data = datos["meses"][datos["mes_actual"]]

col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre", value=mes_data.get("nombre", ""))
with col2:
    st.text_input("Mes activo", value=datos["mes_actual"], disabled=True)

ingresos_df_base = asegurar_columnas(pd.DataFrame(mes_data.get("ingresos", [])), ["Descripción", "Monto"])
gastos_fijos_df_base = asegurar_columnas(pd.DataFrame(mes_data.get("gastos_fijos", [])), ["Categoría", "Descripción", "Monto"])
gastos_variables_df_base = asegurar_columnas(pd.DataFrame(mes_data.get("gastos_variables", [])), ["Categoría", "Descripción", "Monto"])

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Inicio", "💵 Ingresos", "🧾 Gastos", "📊 Resumen", "📈 Comparar meses"])

with tab1:
    st.subheader("⭐ Metas de ahorro")
    meta_ahorro = st.number_input("¿Cuánto quieres ahorrar este mes?", min_value=0, step=1000, value=int(mes_data.get("meta_ahorro", 0)))
    notas = st.text_area("Notas o prioridades del mes", value=mes_data.get("notas", ""))

with tab2:
    st.subheader("💵 Ingresos del mes")
    ingresos_df = st.data_editor(ingresos_df_base, num_rows="dynamic", use_container_width=True, key=f"ingresos_editor_{datos['mes_actual']}")

with tab3:
    st.subheader("🏠 Gastos fijos mensuales")
    gastos_fijos_df = st.data_editor(gastos_fijos_df_base, num_rows="dynamic", use_container_width=True, key=f"gastos_fijos_editor_{datos['mes_actual']}")
    st.subheader("🛍️ Gastos variables / personales")
    gastos_variables_df = st.data_editor(gastos_variables_df_base, num_rows="dynamic", use_container_width=True, key=f"gastos_variables_editor_{datos['mes_actual']}")

ingresos_df = limpiar_montos(ingresos_df)
gastos_fijos_df = limpiar_montos(gastos_fijos_df)
gastos_variables_df = limpiar_montos(gastos_variables_df)

total_ingresos = ingresos_df["Monto"].sum()
total_fijos = gastos_fijos_df["Monto"].sum()
total_variables = gastos_variables_df["Monto"].sum()
total_gastos = total_fijos + total_variables
saldo = total_ingresos - total_gastos
saldo_despues_ahorro = saldo - meta_ahorro
porcentaje_gastado = min((total_gastos / total_ingresos) * 100, 100) if total_ingresos > 0 else 0

st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("💵 Ingresos", f"${total_ingresos:,.0f}")
col2.metric("🧾 Gastos", f"${total_gastos:,.0f}")
col3.metric("💖 Saldo", f"${saldo:,.0f}")
st.progress(int(porcentaje_gastado))
st.caption(f"Has usado aproximadamente el {porcentaje_gastado:.1f}% de tus ingresos en {datos['mes_actual']}.")

st.subheader("🧠 Consejos financieros")
if total_ingresos > 0:
    porcentaje_gastos = (total_gastos / total_ingresos) * 100
    if porcentaje_gastos >= 90:
        st.error("🚨 Estás utilizando casi todos tus ingresos este mes. Intenta reducir gastos variables.")
    elif porcentaje_gastos >= 70:
        st.warning("⚠️ Tus gastos están algo elevados. Revisa gastos hormiga o compras impulsivas.")
    else:
        st.success("💖 Tus gastos están bastante equilibrados este mes.")

    hormiga = gastos_variables_df[gastos_variables_df["Categoría"].astype(str).str.contains("hormiga", case=False, na=False)]["Monto"].sum()
    if total_gastos > 0 and hormiga > 0:
        porcentaje_hormiga = (hormiga / total_gastos) * 100
        if porcentaje_hormiga >= 15:
            st.warning(f"🛍️ Tus gastos hormiga representan {porcentaje_hormiga:.1f}% de tus gastos.")

    if meta_ahorro > 0:
        if saldo_despues_ahorro >= 0:
            st.info("✨ Puedes cumplir tu meta de ahorro este mes.")
        else:
            st.error("⚠️ Con los gastos actuales será difícil cumplir tu meta de ahorro.")
else:
    st.info("💡 Ingresa tus ingresos para recibir consejos automáticos.")

with tab4:
    st.subheader(f"📊 Resumen de {datos['mes_actual']}")
    resumen = pd.DataFrame({"Tipo": ["Ingresos", "Gastos fijos", "Gastos variables", "Meta ahorro"], "Monto": [total_ingresos, total_fijos, total_variables, meta_ahorro]})
    st.bar_chart(resumen, x="Tipo", y="Monto")
    st.subheader("Detalle por categoría")
    detalle = pd.concat([gastos_fijos_df[["Categoría", "Monto"]], gastos_variables_df[["Categoría", "Monto"]]])
    detalle = detalle.groupby("Categoría", as_index=False)["Monto"].sum()
    st.dataframe(detalle, use_container_width=True)

with tab5:
    st.subheader("📈 Comparación entre meses")
    filas = []
    for mes, contenido in sorted(datos["meses"].items()):
        calculo = calcular_mes(contenido)
        filas.append({"Mes": mes, **calculo})
    comparacion = pd.DataFrame(filas)
    if len(comparacion) > 0:
        st.dataframe(comparacion, use_container_width=True)
        st.line_chart(comparacion, x="Mes", y=["Ingresos", "Total gastos", "Saldo"])
    else:
        st.info("Aún no hay meses para comparar.")

datos["meses"][datos["mes_actual"]] = {
    "nombre": nombre,
    "meta_ahorro": meta_ahorro,
    "notas": notas,
    "ingresos": ingresos_df.to_dict("records"),
    "gastos_fijos": gastos_fijos_df.to_dict("records"),
    "gastos_variables": gastos_variables_df.to_dict("records"),
}

if st.button("💾 Guardar cambios del mes"):
    guardar_json(ARCHIVO_DATOS, datos)
    st.success(f"Datos de {datos['mes_actual']} guardados correctamente 💖")

st.download_button(label="📥 Descargar respaldo completo", data=json.dumps(datos, ensure_ascii=False, indent=4), file_name="respaldo_presupuesto_todos_los_meses.json", mime="application/json")
