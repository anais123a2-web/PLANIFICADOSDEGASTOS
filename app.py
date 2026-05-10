import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Planificador de Gastos", page_icon="💖", layout="wide")

ARCHIVO_DATOS = Path("datos_presupuesto.json")
CLAVE_ARCHIVO = Path("clave_usuario.json")


def cargar_datos():
    if ARCHIVO_DATOS.exists():
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_datos(datos):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)


def cargar_clave():
    if CLAVE_ARCHIVO.exists():
        with open(CLAVE_ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f).get("clave")
    return None


def guardar_clave(nueva_clave):
    with open(CLAVE_ARCHIVO, "w", encoding="utf-8") as f:
        json.dump({"clave": nueva_clave}, f, ensure_ascii=False, indent=4)


datos_guardados = cargar_datos()

# ---------- LOGIN ----------
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

# ---------- MODO ----------

fondo = "#fff6fb"
texto = "#321c3b"

# ---------- ESTILO ----------
st.markdown("""

<style>
.stApp {
    background: linear-gradient(180deg, #fff6fb 0%, #ffeaf4 45%, #fff8fc 100%);
    color: #321c3b;
}

.block-container {
    padding: 1rem;
    max-width: 980px;
}

h1, h2, h3, label, p {
    color: #321c3b !important;
}

.hero-card {
    background: linear-gradient(135deg, #fff7fb, #ffd6eb);
    border: 2px solid #ffc2df;
    border-radius: 32px;
    padding: 28px 18px;
    text-align: center;
    box-shadow: 0 12px 30px rgba(255, 105, 180, 0.22);
    margin-bottom: 20px;
}

.hero-title {
    font-size: 46px;
    line-height: 1.05;
    font-weight: 900;
    color: #7b1e5c !important;
    margin: 0;
}

.hero-title span {
    color: #ff4da6;
    font-family: Georgia, serif;
    font-style: italic;
}

.hero-subtitle {
    margin-top: 10px;
    font-size: 16px;
    color: #8a4a73 !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #fff0f7);
    border: 2px solid #ffcce5;
    border-radius: 26px;
    padding: 18px;
    box-shadow: 0px 8px 22px rgba(255, 105, 180, 0.18);
}

[data-testid="stMetricValue"] {
    color: #ff4da6;
}

[data-testid="stDataEditor"] {
    border-radius: 24px;
    border: 2px solid #ffcce5;
    overflow: hidden;
}

.stTabs [data-baseweb="tab"] {
    background-color: #fff7fb;
    border: 2px solid #ffcce5;
    border-radius: 999px;
    padding: 8px 14px;
    color: #7b1e5c;
    font-weight: 800;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #ff8ac7, #ff4da6);
    color: white !important;
}

.stButton>button {
    background: linear-gradient(135deg, #ff7ac8, #ff4da6);
    color: white;
    border-radius: 999px;
    border: none;
    padding: 14px 25px;
    font-weight: 900;
    width: 100%;
}

div[data-baseweb="input"] > div,
textarea {
    border-radius: 20px !important;
    border: 2px solid #ffcce5 !important;
    background-color: #fffafd !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffeaf3, #fff7fb);
    border-right: 2px solid #ffcce5;
}

section[data-testid="stSidebar"] * {
    color: #7b1e5c !important;
}

section[data-testid="stSidebar"] button {
    background: linear-gradient(135deg, #ff8ac7, #ff4da6);
    color: white !important;
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 34px;
    }

    .hero-card {
        padding: 24px 14px;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------- TÍTULO ----------
st.markdown(
    """
    <div class="hero-card">
        <h1 class="hero-title">
            Mi Presupuesto <br>
            <span>Bonito</span>
        </h1>
        <p class="hero-subtitle">
            Organiza tu mes con calma, claridad y estilo
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- DATOS PRINCIPALES ----------
col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input("Nombre", value=datos_guardados.get("nombre", ""))

with col2:
    mes = st.text_input("Mes y año", value=datos_guardados.get("mes", ""))

# ---------- DATOS BASE ----------
ingresos_base = datos_guardados.get("ingresos", [
    {"Descripción": "Sueldo", "Monto": 0},
    {"Descripción": "Otros ingresos", "Monto": 0},
])

gastos_fijos_base = datos_guardados.get("gastos_fijos", [
    {"Categoría": "Arriendo", "Descripción": "", "Monto": 0},
    {"Categoría": "Luz", "Descripción": "", "Monto": 0},
    {"Categoría": "Agua", "Descripción": "", "Monto": 0},
    {"Categoría": "Internet / Teléfono", "Descripción": "", "Monto": 0},
    {"Categoría": "Mercadería", "Descripción": "", "Monto": 0},
    {"Categoría": "Alimento mascotas", "Descripción": "", "Monto": 0},
])

gastos_variables_base = datos_guardados.get("gastos_variables", [
    {"Categoría": "Gastos hormiga", "Descripción": "", "Monto": 0},
    {"Categoría": "Gastos personales", "Descripción": "", "Monto": 0},
    {"Categoría": "Comida fuera de casa", "Descripción": "", "Monto": 0},
    {"Categoría": "Transporte", "Descripción": "", "Monto": 0},
])

# ---------- PESTAÑAS ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Inicio",
    "💵 Ingresos",
    "🧾 Gastos",
    "📊 Resumen"
])

with tab1:
    st.subheader("⭐ Metas de ahorro")

    meta_ahorro = st.number_input(
        "¿Cuánto quieres ahorrar este mes?",
        min_value=0,
        step=1000,
        value=int(datos_guardados.get("meta_ahorro", 0))
    )

    notas = st.text_area(
        "Notas o prioridades del mes",
        value=datos_guardados.get("notas", "")
    )

with tab2:
    st.subheader("💵 Ingresos del mes")
    ingresos_df = st.data_editor(
        pd.DataFrame(ingresos_base),
        num_rows="dynamic",
        use_container_width=True,
        key="ingresos_editor"
    )

with tab3:
    st.subheader("🏠 Gastos fijos mensuales")
    gastos_fijos_df = st.data_editor(
        pd.DataFrame(gastos_fijos_base),
        num_rows="dynamic",
        use_container_width=True,
        key="gastos_fijos_editor"
    )

    st.subheader("🛍️ Gastos variables / personales")
    gastos_variables_df = st.data_editor(
        pd.DataFrame(gastos_variables_base),
        num_rows="dynamic",
        use_container_width=True,
        key="gastos_variables_editor"
    )

# ---------- CÁLCULOS ----------
total_ingresos = ingresos_df["Monto"].sum()
total_fijos = gastos_fijos_df["Monto"].sum()
total_variables = gastos_variables_df["Monto"].sum()
total_gastos = total_fijos + total_variables
saldo = total_ingresos - total_gastos
saldo_despues_ahorro = saldo - meta_ahorro

porcentaje_gastado = 0
if total_ingresos > 0:
    porcentaje_gastado = min((total_gastos / total_ingresos) * 100, 100)

# ---------- RESUMEN ARRIBA ----------
st.divider()

col1, col2, col3 = st.columns(3)

col1.metric("💵 Ingresos", f"${total_ingresos:,.0f}")
col2.metric("🧾 Gastos", f"${total_gastos:,.0f}")
col3.metric("💖 Saldo", f"${saldo:,.0f}")

st.progress(int(porcentaje_gastado))
st.caption(f"Has usado aproximadamente el {porcentaje_gastado:.1f}% de tus ingresos.")

# ---------- CONSEJOS ----------
st.subheader("🧠 Consejos financieros")

if total_ingresos > 0:
    porcentaje_gastos = (total_gastos / total_ingresos) * 100

    if porcentaje_gastos >= 90:
        st.error("🚨 Estás utilizando casi todos tus ingresos este mes. Intenta reducir gastos variables.")
    elif porcentaje_gastos >= 70:
        st.warning("⚠️ Tus gastos están algo elevados. Revisa gastos hormiga o compras impulsivas.")
    else:
        st.success("💖 Tus gastos están bastante equilibrados este mes.")

    hormiga = gastos_variables_df[
        gastos_variables_df["Categoría"].astype(str).str.contains("hormiga", case=False, na=False)
    ]["Monto"].sum()

    if total_gastos > 0 and hormiga > 0:
        porcentaje_hormiga = (hormiga / total_gastos) * 100
        if porcentaje_hormiga >= 15:
            st.warning(f"🛍️ Tus gastos hormiga representan {porcentaje_hormiga:.1f}% de tus gastos.")

    if meta_ahorro > 0:
        if saldo_despues_ahorro >= 0:
            st.info("✨ Puedes cumplir tu meta de ahorro este mes.")
        else:
            st.error("⚠️ Con los gastos actuales será difícil cumplir tu meta de ahorro.")

    mascotas = gastos_fijos_df[
        gastos_fijos_df["Categoría"].astype(str).str.contains("masc", case=False, na=False)
    ]["Monto"].sum()

    if mascotas > 0:
        st.caption("🐶 Recuerda considerar gastos veterinarios o emergencias para mascotas.")
else:
    st.info("💡 Ingresa tus ingresos para recibir consejos automáticos.")

# ---------- RESUMEN Y GRÁFICOS ----------
with tab4:
    st.subheader("📊 Resumen del mes")

    resumen = pd.DataFrame({
        "Tipo": ["Ingresos", "Gastos fijos", "Gastos variables", "Meta ahorro"],
        "Monto": [total_ingresos, total_fijos, total_variables, meta_ahorro]
    })

    st.bar_chart(resumen, x="Tipo", y="Monto")

    st.subheader("Detalle por categoría")

    detalle = pd.concat([
        gastos_fijos_df[["Categoría", "Monto"]],
        gastos_variables_df[["Categoría", "Monto"]]
    ])

    detalle = detalle.groupby("Categoría", as_index=False)["Monto"].sum()
    st.dataframe(detalle, use_container_width=True)

# ---------- GUARDAR ----------
datos = {
    "nombre": nombre,
    "mes": mes,
    "meta_ahorro": meta_ahorro,
    "notas": notas,
    "ingresos": ingresos_df.to_dict("records"),
    "gastos_fijos": gastos_fijos_df.to_dict("records"),
    "gastos_variables": gastos_variables_df.to_dict("records"),
}

if st.button("💾 Guardar cambios"):
    guardar_datos(datos)
    st.success("Datos guardados correctamente 💖")

st.download_button(
    label="📥 Descargar respaldo",
    data=json.dumps(datos, ensure_ascii=False, indent=4),
    file_name="respaldo_presupuesto.json",
    mime="application/json"
)