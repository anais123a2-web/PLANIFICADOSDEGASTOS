
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date

st.set_page_config(page_title="Registro Mensual", page_icon="💖", layout="wide")

CARPETA_DATOS = Path("datos_usuarios")
CARPETA_DATOS.mkdir(exist_ok=True)

USUARIOS = {
    "Personal": {
        "archivo": CARPETA_DATOS / "datos_personal.json",
        "clave": CARPETA_DATOS / "clave_personal.json",
        "categorias_ingresos": ["Sueldo", "Otros ingresos", "Venta ocasional", "Devolución", "Bono", "Otro"],
        "categorias_gastos": [
            "Arriendo", "Luz", "Agua", "Internet", "Mercadería", "Mascotas",
            "Gastos hormiga", "Gastos personales", "Transporte", "Comida fuera",
            "Salud", "Ropa", "Otro"
        ],
        "titulo": "Registro Financiero Personal",
        "meta_texto": "Meta de ahorro"
    },
    "Empresa": {
        "archivo": CARPETA_DATOS / "datos_empresa.json",
        "clave": CARPETA_DATOS / "clave_empresa.json",
        "categorias_ingresos": [
            "Impresiones", "Diseños", "Ventas productos", "Servicio gráfico",
            "Fotografías", "Plastificados", "Encuadernación", "Otros ingresos"
        ],
        "categorias_gastos": [
            "Insumos", "Papel fotográfico", "Tinta / tóner", "Arriendo local",
            "Luz local", "Internet", "Publicidad", "Mantención máquinas",
            "Sueldos", "Transporte", "Compras negocio", "Otros gastos"
        ],
        "titulo": "Control Financiero Empresa",
        "meta_texto": "Meta de utilidad"
    }
}

MEDIOS_PAGO = ["Efectivo", "Transferencia", "Débito", "Crédito", "Mercado Pago", "Otro"]


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


def mes_actual():
    hoy = date.today()
    return f"{hoy.year}-{hoy.month:02d}"


def tabla_ingresos_base(usuario):
    if usuario == "Empresa":
        return [
            {"Fecha": "", "Categoría": "Impresiones", "Descripción": "", "Medio de pago": "Efectivo", "Monto": 0, "Observación": ""},
            {"Fecha": "", "Categoría": "Diseños", "Descripción": "", "Medio de pago": "Transferencia", "Monto": 0, "Observación": ""},
        ]
    return [
        {"Fecha": "", "Categoría": "Sueldo", "Descripción": "", "Medio de pago": "Transferencia", "Monto": 0, "Observación": ""},
        {"Fecha": "", "Categoría": "Otros ingresos", "Descripción": "", "Medio de pago": "Efectivo", "Monto": 0, "Observación": ""},
    ]


def tabla_gastos_base(usuario):
    if usuario == "Empresa":
        return [
            {"Fecha": "", "Categoría": "Insumos", "Descripción": "", "Medio de pago": "Transferencia", "Monto": 0, "Observación": ""},
            {"Fecha": "", "Categoría": "Papel fotográfico", "Descripción": "", "Medio de pago": "Débito", "Monto": 0, "Observación": ""},
            {"Fecha": "", "Categoría": "Tinta / tóner", "Descripción": "", "Medio de pago": "Transferencia", "Monto": 0, "Observación": ""},
        ]
    return [
        {"Fecha": "", "Categoría": "Mercadería", "Descripción": "", "Medio de pago": "Débito", "Monto": 0, "Observación": ""},
        {"Fecha": "", "Categoría": "Luz", "Descripción": "", "Medio de pago": "Transferencia", "Monto": 0, "Observación": ""},
        {"Fecha": "", "Categoría": "Gastos hormiga", "Descripción": "", "Medio de pago": "Efectivo", "Monto": 0, "Observación": ""},
    ]


def crear_mes_vacio(usuario):
    return {
        "meta": 0,
        "notas": "",
        "ingresos": tabla_ingresos_base(usuario),
        "gastos": tabla_gastos_base(usuario)
    }


def asegurar_estructura(datos, usuario):
    if "mes_actual" not in datos:
        datos["mes_actual"] = mes_actual()

    if "meses" not in datos or not isinstance(datos["meses"], dict):
        datos["meses"] = {}

    if datos["mes_actual"] not in datos["meses"]:
        datos["meses"][datos["mes_actual"]] = crear_mes_vacio(usuario)

    for mes, contenido in list(datos["meses"].items()):
        if "movimientos" in contenido and ("ingresos" not in contenido or "gastos" not in contenido):
            mov = pd.DataFrame(contenido.get("movimientos", []))
            if len(mov) > 0 and "Tipo" in mov.columns:
                ingresos = mov[mov["Tipo"] == "Ingreso"].drop(columns=["Tipo"], errors="ignore").to_dict("records")
                gastos = mov[mov["Tipo"] == "Gasto"].drop(columns=["Tipo"], errors="ignore").to_dict("records")
            else:
                ingresos = tabla_ingresos_base(usuario)
                gastos = tabla_gastos_base(usuario)

            contenido["ingresos"] = ingresos if ingresos else tabla_ingresos_base(usuario)
            contenido["gastos"] = gastos if gastos else tabla_gastos_base(usuario)

        if "meta_ahorro" in contenido and "meta" not in contenido:
            contenido["meta"] = contenido.get("meta_ahorro", 0)

        if "ingresos" not in contenido:
            contenido["ingresos"] = tabla_ingresos_base(usuario)

        if "gastos" not in contenido:
            contenido["gastos"] = tabla_gastos_base(usuario)

        if "notas" not in contenido:
            contenido["notas"] = ""

        if "meta" not in contenido:
            contenido["meta"] = 0

    return datos


def preparar_tabla(registros):
    columnas = ["Fecha", "Categoría", "Descripción", "Medio de pago", "Monto", "Observación"]
    df = pd.DataFrame(registros)

    for col in columnas:
        if col not in df.columns:
            df[col] = 0 if col == "Monto" else ""

    df = df[columnas]
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)
    return df


def total_tabla(df):
    if "Monto" not in df.columns:
        return 0
    return pd.to_numeric(df["Monto"], errors="coerce").fillna(0).sum()


def cargar_clave(ruta_clave):
    datos = cargar_json(ruta_clave, {})
    return datos.get("clave")


def guardar_clave(ruta_clave, clave):
    guardar_json(ruta_clave, {"clave": clave})


st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #fff6fb 0%, #ffeaf4 45%, #fff8fc 100%);
    color: #321c3b;
}

.block-container {
    padding: 1rem;
    max-width: 1080px;
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


st.sidebar.title("👤 Perfil")
usuario = st.sidebar.selectbox("Selecciona usuario", ["Personal", "Empresa"])
config = USUARIOS[usuario]

ruta_datos = config["archivo"]
ruta_clave = config["clave"]

st.sidebar.title("🔐 Acceso")
clave_guardada = cargar_clave(ruta_clave)

if clave_guardada is None:
    st.info(f"Crea una contraseña para el perfil {usuario}")
    nueva_clave = st.text_input("Crea tu contraseña", type="password")
    repetir_clave = st.text_input("Repite tu contraseña", type="password")

    if st.button("Crear contraseña"):
        if not nueva_clave:
            st.error("La contraseña no puede estar vacía.")
        elif nueva_clave != repetir_clave:
            st.error("Las contraseñas no coinciden.")
        else:
            guardar_clave(ruta_clave, nueva_clave)
            st.success("Contraseña creada correctamente")
            st.rerun()
    st.stop()

clave_ingresada = st.sidebar.text_input(f"Contraseña de {usuario}", type="password")

if clave_ingresada != clave_guardada:
    st.warning(f"Ingresa la contraseña del perfil {usuario}")
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
            guardar_clave(ruta_clave, nueva_clave)
            st.success("Contraseña actualizada correctamente")
            st.rerun()


datos = asegurar_estructura(cargar_json(ruta_datos, {}), usuario)


st.markdown(
    f"""
    <div class="hero-card">
        <h1 class="hero-title">
            {config["titulo"]}<br>
            <span>{usuario}</span>
        </h1>
        <p class="hero-subtitle">
            Ingresos y gastos separados, con resumen mensual y comparación por meses
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


if usuario == "Empresa":
    st.subheader("🏢 Mes contable")
else:
    st.subheader("📅 Mes personal")

meses_ordenados = sorted(datos["meses"].keys(), reverse=True)
mes_seleccionado = st.selectbox(
    "Selecciona un mes guardado",
    meses_ordenados,
    index=meses_ordenados.index(datos["mes_actual"]) if datos["mes_actual"] in meses_ordenados else 0
)

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
            datos["meses"][nuevo_mes] = crear_mes_vacio(usuario)
            datos["mes_actual"] = nuevo_mes
            guardar_json(ruta_datos, datos)
            st.success(f"Mes {nuevo_mes} creado.")
            st.rerun()

if mes_seleccionado != datos["mes_actual"]:
    datos["mes_actual"] = mes_seleccionado
    guardar_json(ruta_datos, datos)

mes_data = datos["meses"][datos["mes_actual"]]


tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Inicio",
    "💵 Ingresos",
    "🧾 Gastos",
    "📊 Resumen",
    "📈 Comparar meses"
])

with tab1:
    if usuario == "Empresa":
        st.subheader("💼 Objetivos y notas del negocio")
    else:
        st.subheader("⭐ Meta y notas personales")

    meta = st.number_input(
        config["meta_texto"],
        min_value=0,
        step=1000,
        value=int(mes_data.get("meta", 0))
    )

    notas = st.text_area(
        "Notas o prioridades del mes",
        value=mes_data.get("notas", "")
    )

with tab2:
    st.subheader("💵 Ingresos del mes")

    if usuario == "Personal":
        st.caption("Por defecto aparecen Sueldo y Otros ingresos. Puedes editar la descripción, cambiar montos y agregar más filas abajo.")
    else:
        st.caption("Registra aquí todos los ingresos de la empresa. Puedes agregar más filas abajo.")

    ingresos_base = preparar_tabla(mes_data.get("ingresos", tabla_ingresos_base(usuario)))

    ingresos_df = st.data_editor(
        ingresos_base,
        num_rows="dynamic",
        use_container_width=True,
        key=f"ingresos_{usuario}_{datos['mes_actual']}",
        column_config={
            "Fecha": st.column_config.TextColumn("Fecha", help="Ej: 10/05/2026"),
            "Categoría": st.column_config.SelectboxColumn("Categoría", options=config["categorias_ingresos"]),
            "Descripción": st.column_config.TextColumn("Descripción", help="Ej: sueldo mayo, venta extra, abono, etc."),
            "Medio de pago": st.column_config.SelectboxColumn("Medio de pago", options=MEDIOS_PAGO),
            "Monto": st.column_config.NumberColumn("Monto", min_value=0, step=1000),
            "Observación": st.column_config.TextColumn("Observación"),
        }
    )

with tab3:
    st.subheader("🧾 Gastos del mes")

    if usuario == "Personal":
        st.caption("Edita la descripción de cada gasto y agrega más filas hacia abajo. Los gráficos se ven solo en la pestaña Resumen.")
    else:
        st.caption("Registra aquí los gastos de la empresa. Los gráficos se ven solo en la pestaña Resumen.")

    gastos_base = preparar_tabla(mes_data.get("gastos", tabla_gastos_base(usuario)))

    gastos_df = st.data_editor(
        gastos_base,
        num_rows="dynamic",
        use_container_width=True,
        key=f"gastos_{usuario}_{datos['mes_actual']}",
        column_config={
            "Fecha": st.column_config.TextColumn("Fecha", help="Ej: 10/05/2026"),
            "Categoría": st.column_config.SelectboxColumn("Categoría", options=config["categorias_gastos"]),
            "Descripción": st.column_config.TextColumn("Descripción", help="Ej: luz, agua, mercadería, alimento mascotas, etc."),
            "Medio de pago": st.column_config.SelectboxColumn("Medio de pago", options=MEDIOS_PAGO),
            "Monto": st.column_config.NumberColumn("Monto", min_value=0, step=1000),
            "Observación": st.column_config.TextColumn("Observación"),
        }
    )


ingresos_df = preparar_tabla(ingresos_df)
gastos_df = preparar_tabla(gastos_df)

total_ingresos = total_tabla(ingresos_df)
total_gastos = total_tabla(gastos_df)
saldo = total_ingresos - total_gastos
saldo_despues_meta = saldo - meta

porcentaje_gastado = 0
if total_ingresos > 0:
    porcentaje_gastado = min((total_gastos / total_ingresos) * 100, 100)


st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("💵 Ingresos", f"${total_ingresos:,.0f}")
col2.metric("🧾 Gastos", f"${total_gastos:,.0f}")
col3.metric("💖 Saldo / utilidad", f"${saldo:,.0f}")

st.progress(int(porcentaje_gastado))
st.caption(f"Has usado aproximadamente el {porcentaje_gastado:.1f}% de tus ingresos en {datos['mes_actual']}.")


st.subheader("🧠 Consejos automáticos")

if total_ingresos > 0:
    porcentaje_gastos = (total_gastos / total_ingresos) * 100

    if saldo < 0:
        st.error("🚨 Tus gastos superan tus ingresos este mes.")
    elif porcentaje_gastos >= 90:
        st.warning("⚠️ Estás usando casi todos tus ingresos. Revisa los gastos más altos.")
    elif porcentaje_gastos >= 70:
        st.info("💡 Tus gastos están algo altos. Revisa las categorías con mayor monto.")
    else:
        st.success("💖 El mes se ve equilibrado. Vas bien.")

    if total_gastos > 0:
        top_gastos = gastos_df.groupby("Categoría")["Monto"].sum().sort_values(ascending=False)
        if len(top_gastos) > 0:
            categoria_top = top_gastos.index[0]
            monto_top = top_gastos.iloc[0]
            st.caption(f"📌 La categoría con más gasto es {categoria_top}: ${monto_top:,.0f}.")

    if meta > 0:
        if saldo_despues_meta >= 0:
            st.info(f"✨ Puedes cumplir tu meta y aún quedar con ${saldo_despues_meta:,.0f}.")
        else:
            st.warning(f"Para cumplir tu meta te faltarían ${abs(saldo_despues_meta):,.0f}.")
else:
    st.info("💡 Ingresa ingresos para recibir consejos.")


with tab4:
    st.subheader(f"📊 Resumen de {datos['mes_actual']}")

    resumen = pd.DataFrame({
        "Tipo": ["Ingresos", "Gastos", config["meta_texto"], "Saldo"],
        "Monto": [total_ingresos, total_gastos, meta, saldo]
    })

    st.bar_chart(resumen, x="Tipo", y="Monto")

    st.subheader("Ingresos por categoría")
    ingresos_categoria = ingresos_df.groupby("Categoría", as_index=False)["Monto"].sum()
    st.dataframe(ingresos_categoria, use_container_width=True)

    st.subheader("Gastos por categoría")
    gastos_categoria = gastos_df.groupby("Categoría", as_index=False)["Monto"].sum()
    st.dataframe(gastos_categoria, use_container_width=True)

    st.subheader("Gastos por medio de pago")
    gastos_pago = gastos_df.groupby("Medio de pago", as_index=False)["Monto"].sum()
    st.dataframe(gastos_pago, use_container_width=True)


with tab5:
    st.subheader("📈 Comparación mensual")

    filas = []

    for mes, contenido in sorted(datos["meses"].items()):
        df_ing = preparar_tabla(contenido.get("ingresos", []))
        df_gas = preparar_tabla(contenido.get("gastos", []))
        meta_mes = float(contenido.get("meta", 0) or 0)

        ingresos_mes = total_tabla(df_ing)
        gastos_mes = total_tabla(df_gas)
        saldo_mes = ingresos_mes - gastos_mes

        filas.append({
            "Mes": mes,
            "Ingresos": ingresos_mes,
            "Gastos": gastos_mes,
            "Saldo": saldo_mes,
            config["meta_texto"]: meta_mes,
            "Después meta": saldo_mes - meta_mes,
        })

    comparacion = pd.DataFrame(filas)

    if len(comparacion) > 0:
        st.dataframe(comparacion, use_container_width=True)
        st.line_chart(comparacion, x="Mes", y=["Ingresos", "Gastos", "Saldo"])
    else:
        st.info("Aún no hay meses para comparar.")


datos["meses"][datos["mes_actual"]] = {
    "meta": meta,
    "notas": notas,
    "ingresos": ingresos_df.to_dict("records"),
    "gastos": gastos_df.to_dict("records"),
}

if st.button("💾 Guardar cambios"):
    guardar_json(ruta_datos, datos)
    st.success(f"Datos de {usuario} - {datos['mes_actual']} guardados correctamente")


st.download_button(
    label=f"📥 Descargar respaldo de {usuario}",
    data=json.dumps(datos, ensure_ascii=False, indent=4),
    file_name=f"respaldo_{usuario.lower()}_mensual.json",
    mime="application/json"
)
