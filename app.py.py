# APP COMBINADA PERSONAL + EMPRESA
# Personal conserva el diseño original
# Empresa usa registro empresarial mensual

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date

st.set_page_config(page_title="Registro Financiero", page_icon="💖", layout="wide")

CARPETA = Path("datos_usuarios")
CARPETA.mkdir(exist_ok=True)

# ---------------- FUNCIONES ----------------

def cargar_json(ruta, default):
    if ruta.exists():
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default


def guardar_json(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)


def cargar_clave(ruta):
    datos = cargar_json(ruta, {})
    return datos.get("clave")


def guardar_clave(ruta, clave):
    guardar_json(ruta, {"clave": clave})


# ---------------- ESTILO ----------------

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

[data-testid="stDataEditor"] {
    border-radius: 24px;
    border: 2px solid #ffcce5;
    overflow: hidden;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffeaf3, #fff7fb);
}
</style>
""", unsafe_allow_html=True)

# ---------------- PERFIL ----------------

st.sidebar.title("👤 Perfil")

perfil = st.sidebar.selectbox(
    "Selecciona usuario",
    ["Personal", "Empresa"]
)

if perfil == "Personal":
    ARCHIVO_DATOS = CARPETA / "datos_personal.json"
    ARCHIVO_CLAVE = CARPETA / "clave_personal.json"
else:
    ARCHIVO_DATOS = CARPETA / "datos_empresa.json"
    ARCHIVO_CLAVE = CARPETA / "clave_empresa.json"

# ---------------- LOGIN ----------------

st.sidebar.title("🔐 Acceso")

clave_guardada = cargar_clave(ARCHIVO_CLAVE)

if clave_guardada is None:
    st.info(f"Crea una contraseña para {perfil}")

    nueva = st.text_input("Crear contraseña", type="password")
    repetir = st.text_input("Repetir contraseña", type="password")

    if st.button("Guardar contraseña"):
        if nueva != repetir:
            st.error("Las contraseñas no coinciden")
        elif nueva == "":
            st.error("La contraseña no puede estar vacía")
        else:
            guardar_clave(ARCHIVO_CLAVE, nueva)
            st.success("Contraseña creada")
            st.rerun()

    st.stop()

clave = st.sidebar.text_input("Contraseña", type="password")

if clave != clave_guardada:
    st.warning("Ingresa tu contraseña")
    st.stop()

# =========================================================
# ====================== PERSONAL ==========================
# =========================================================

if perfil == "Personal":

    datos_guardados = cargar_json(ARCHIVO_DATOS, {})

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

    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre", value=datos_guardados.get("nombre", ""))

    with col2:
        mes = st.text_input("Mes y año", value=datos_guardados.get("mes", ""))

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

    total_ingresos = ingresos_df["Monto"].sum()
    total_fijos = gastos_fijos_df["Monto"].sum()
    total_variables = gastos_variables_df["Monto"].sum()

    total_gastos = total_fijos + total_variables
    saldo = total_ingresos - total_gastos

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric("💵 Ingresos", f"${total_ingresos:,.0f}")
    c2.metric("🧾 Gastos", f"${total_gastos:,.0f}")
    c3.metric("💖 Saldo", f"${saldo:,.0f}")

    with tab4:
        st.subheader("📊 Resumen del mes")

        resumen = pd.DataFrame({
            "Tipo": ["Ingresos", "Gastos fijos", "Gastos variables"],
            "Monto": [total_ingresos, total_fijos, total_variables]
        })

        st.bar_chart(resumen, x="Tipo", y="Monto")

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
        guardar_json(ARCHIVO_DATOS, datos)
        st.success("Datos guardados correctamente")

# =========================================================
# ======================= EMPRESA ==========================
# =========================================================

else:

    datos = cargar_json(ARCHIVO_DATOS, {})

    if "meses" not in datos:
        datos["meses"] = {}

    if "mes_actual" not in datos:
        hoy = date.today()
        datos["mes_actual"] = f"{hoy.year}-{hoy.month:02d}"

    if datos["mes_actual"] not in datos["meses"]:
        datos["meses"][datos["mes_actual"]] = {
            "ingresos": [],
            "gastos": [],
            "meta": 0
        }

    st.markdown(
        """
        <div class="hero-card">
            <h1 class="hero-title">
                Control Financiero <br>
                <span>Empresa</span>
            </h1>
            <p class="hero-subtitle">
                Control mensual del negocio
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🏢 Mes contable")

    meses = sorted(datos["meses"].keys(), reverse=True)

    mes_actual = st.selectbox(
        "Selecciona un mes",
        meses,
        index=meses.index(datos["mes_actual"])
    )

    nuevo_mes = st.text_input("Crear nuevo mes", placeholder="2026-06")

    if st.button("➕ Crear mes"):
        if nuevo_mes not in datos["meses"]:
            datos["meses"][nuevo_mes] = {
                "ingresos": [],
                "gastos": [],
                "meta": 0
            }
            datos["mes_actual"] = nuevo_mes
            guardar_json(ARCHIVO_DATOS, datos)
            st.rerun()

    datos["mes_actual"] = mes_actual

    datos_mes = datos["meses"][mes_actual]

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Inicio",
        "💵 Ingresos empresa",
        "🧾 Gastos empresa",
        "📊 Resumen negocio"
    ])

    with tab1:
        meta = st.number_input(
            "Meta de utilidad",
            min_value=0,
            step=1000,
            value=int(datos_mes.get("meta", 0))
        )

    with tab2:

        ingresos_df = st.data_editor(
            pd.DataFrame(
                datos_mes.get("ingresos", [
                    {
                        "Fecha": "",
                        "Categoría": "Impresiones",
                        "Descripción": "",
                        "Medio de pago": "Efectivo",
                        "Monto": 0
                    }
                ])
            ),
            num_rows="dynamic",
            use_container_width=True
        )

    with tab3:

        gastos_df = st.data_editor(
            pd.DataFrame(
                datos_mes.get("gastos", [
                    {
                        "Fecha": "",
                        "Categoría": "Insumos",
                        "Descripción": "",
                        "Medio de pago": "Transferencia",
                        "Monto": 0
                    }
                ])
            ),
            num_rows="dynamic",
            use_container_width=True
        )

    total_ingresos = ingresos_df["Monto"].sum()
    total_gastos = gastos_df["Monto"].sum()

    saldo = total_ingresos - total_gastos

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric("💵 Ingresos", f"${total_ingresos:,.0f}")
    c2.metric("🧾 Gastos", f"${total_gastos:,.0f}")
    c3.metric("💖 Utilidad", f"${saldo:,.0f}")

    with tab4:

        resumen = pd.DataFrame({
            "Tipo": ["Ingresos", "Gastos", "Meta"],
            "Monto": [total_ingresos, total_gastos, meta]
        })

        st.bar_chart(resumen, x="Tipo", y="Monto")

    datos["meses"][mes_actual] = {
        "ingresos": ingresos_df.to_dict("records"),
        "gastos": gastos_df.to_dict("records"),
        "meta": meta
    }

    if st.button("💾 Guardar negocio"):
        guardar_json(ARCHIVO_DATOS, datos)
        st.success("Datos empresa guardados")
