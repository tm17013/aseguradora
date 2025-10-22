# scripts/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Aseguradora SV",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("Dashboard Aseguradora - El Salvador")
st.markdown("---")

# Cargar datos
@st.cache_data
def cargar_datos():
    try:
        clientes = pd.read_csv('../datos/clientes.csv', parse_dates=['Fecha_Registro'])
        polizas = pd.read_csv('../datos/polizas.csv', parse_dates=['Fecha_Inicio', 'Fecha_Vencimiento'])
        siniestros = pd.read_csv('../datos/siniestros.csv', parse_dates=['Fecha_Siniestro'])
        pagos = pd.read_csv('../datos/pagos.csv', parse_dates=['Fecha_Pago'])
        return clientes, polizas, siniestros, pagos
    except FileNotFoundError as e:
        st.error(f"Error cargando datos: {e}")
        st.info("Ejecuta primero: python scripts/generar_datos.py")
        return None, None, None, None

# Cargar datos
clientes, polizas, siniestros, pagos = cargar_datos()

if clientes is None:
    st.stop()

# ========== SIDEBAR CON FILTROS ==========
st.sidebar.title("🔍 Filtros")

# Filtro por fecha
fecha_min = pagos['Fecha_Pago'].min() if not pagos.empty else datetime.now()
fecha_max = pagos['Fecha_Pago'].max() if not pagos.empty else datetime.now()

rango_fechas = st.sidebar.date_input(
    "Rango de Fechas",
    value=[fecha_min.date(), fecha_max.date()],
    min_value=fecha_min.date(),
    max_value=fecha_max.date()
)

# Filtros múltiples
tipo_seguro = st.sidebar.multiselect(
    "Tipo de Seguro",
    options=polizas['Tipo_Seguro'].unique(),
    default=polizas['Tipo_Seguro'].unique()
)

departamento = st.sidebar.multiselect(
    "Departamento",
    options=clientes['Departamento'].unique(),
    default=clientes['Departamento'].unique()
)

estado_poliza = st.sidebar.multiselect(
    "Estado Póliza",
    options=polizas['Estado'].unique(),
    default=['Activa']
)

# ========== APLICAR FILTROS ==========
if len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas
    pagos_filtrados = pagos[
        (pagos['Fecha_Pago'].dt.date >= fecha_inicio) & 
        (pagos['Fecha_Pago'].dt.date <= fecha_fin)
    ]
    siniestros_filtrados = siniestros[
        (siniestros['Fecha_Siniestro'].dt.date >= fecha_inicio) & 
        (siniestros['Fecha_Siniestro'].dt.date <= fecha_fin)
    ]
else:
    pagos_filtrados = pagos
    siniestros_filtrados = siniestros

polizas_filtradas = polizas[
    (polizas['Tipo_Seguro'].isin(tipo_seguro)) & 
    (polizas['Estado'].isin(estado_poliza))
]

clientes_filtrados = clientes[clientes['Departamento'].isin(departamento)]

# ========== SECCIÓN 1: MÉTRICAS PRINCIPALES ==========
st.header("Métricas Principales")

# Calcular KPIs
total_primas = pagos_filtrados[pagos_filtrados['Estado_Pago'] == 'Completado']['Monto_Pago'].sum()
total_siniestros = siniestros_filtrados[siniestros_filtrados['Estado_Siniestro'] == 'Pagado']['Monto_Pagado'].sum()
polizas_activas = len(polizas_filtradas[polizas_filtradas['Estado'] == 'Activa'])
clientes_activos = len(clientes_filtrados)

# Calcular ratio de siniestralidad (evitar división por cero)
ratio_siniestralidad = (total_siniestros / total_primas * 100) if total_primas > 0 else 0

# Mostrar KPIs en columnas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Primas Cobradas", 
        f"${total_primas:,.2f}"
    )

with col2:
    st.metric(
        "Ratio de Siniestralidad", 
        f"{ratio_siniestralidad:.1f}%"
    )

with col3:
    st.metric(
        "Pólizas Activas", 
        f"{polizas_activas:,}"
    )

with col4:
    st.metric(
        "Clientes Activos", 
        f"{clientes_activos:,}"
    )

# ========== SECCIÓN 2: ANÁLISIS DE CARTERA ==========
st.header("Análisis de Cartera")

col1, col2 = st.columns(2)

with col1:
    # Distribución por tipo de seguro
    st.subheader("Distribución por Tipo de Seguro")
    tipo_counts = polizas_filtradas['Tipo_Seguro'].value_counts()
    fig = px.pie(
        values=tipo_counts.values,
        names=tipo_counts.index,
        title=""
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Primas por tipo de seguro
    st.subheader("Primas por Tipo de Seguro")
    
    # Unir pólizas con pagos para obtener primas reales
    primas_por_tipo = polizas_filtradas.merge(
        pagos_filtrados[pagos_filtrados['Estado_Pago'] == 'Completado'],
        left_on='ID_Poliza',
        right_on='ID_Poliza'
    ).groupby('Tipo_Seguro')['Monto_Pago'].sum().sort_values(ascending=False)
    
    fig = px.bar(
        x=primas_por_tipo.index,
        y=primas_por_tipo.values,
        labels={'x': 'Tipo de Seguro', 'y': 'Primas (USD)'}
    )
    st.plotly_chart(fig, use_container_width=True)

# ========== SECCIÓN 3: ANÁLISIS GEOGRÁFICO ==========
st.header("Análisis Geográfico")

col1, col2 = st.columns(2)

with col1:
    # Clientes por departamento
    st.subheader("Clientes por Departamento")
    clientes_por_depto = clientes_filtrados['Departamento'].value_counts()
    fig = px.bar(
        x=clientes_por_depto.index,
        y=clientes_por_depto.values,
        labels={'x': 'Departamento', 'y': 'Número de Clientes'}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Siniestros por departamento
    st.subheader("Siniestros por Departamento")
    siniestros_por_depto = siniestros_filtrados.groupby('Departamento_Siniestro')['Monto_Pagado'].sum()
    
    if not siniestros_por_depto.empty:
        fig = px.bar(
            x=siniestros_por_depto.index,
            y=siniestros_por_depto.values,
            labels={'x': 'Departamento', 'y': 'Monto Pagado (USD)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de siniestros para los filtros seleccionados")

# ========== SECCIÓN 4: ANÁLISIS TEMPORAL ==========
st.header("Análisis Temporal")

# Primas mensuales
st.subheader("Evolución de Primas Mensuales")
if not pagos_filtrados.empty:
    pagos_mensuales = pagos_filtrados[pagos_filtrados['Estado_Pago'] == 'Completado'].copy()
    pagos_mensuales['Mes_Año'] = pagos_mensuales['Fecha_Pago'].dt.to_period('M')
    primas_mensuales = pagos_mensuales.groupby('Mes_Año')['Monto_Pago'].sum().reset_index()
    primas_mensuales['Mes_Año'] = primas_mensuales['Mes_Año'].astype(str)

    fig = px.line(
        primas_mensuales,
        x='Mes_Año',
        y='Monto_Pago',
        labels={'Mes_Año': 'Mes', 'Monto_Pago': 'Primas (USD)'}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hay datos de pagos para los filtros seleccionados")

# ========== SECCIÓN 5: ANÁLISIS DE SINIESTROS ==========
st.header("Análisis de Siniestros")

col1, col2 = st.columns(2)

with col1:
    # Siniestros por tipo
    st.subheader("Siniestros por Tipo")
    if not siniestros_filtrados.empty:
        siniestros_por_tipo = siniestros_filtrados.groupby('Tipo_Siniestro')['Monto_Pagado'].sum()
        fig = px.bar(
            x=siniestros_por_tipo.index,
            y=siniestros_por_tipo.values,
            labels={'x': 'Tipo de Siniestro', 'y': 'Monto Pagado (USD)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de siniestros")

with col2:
    # Estado de siniestros
    st.subheader("Estado de Siniestros")
    if not siniestros_filtrados.empty:
        estado_counts = siniestros_filtrados['Estado_Siniestro'].value_counts()
        fig = px.pie(
            values=estado_counts.values,
            names=estado_counts.index
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de siniestros")

# ========== SECCIÓN 6: DETALLE DE DATOS ==========
st.header("Detalle de Datos")

tab1, tab2, tab3, tab4 = st.tabs(["Clientes", "Pólizas", "Siniestros", "Pagos"])

with tab1:
    st.subheader("Base de Clientes")
    st.dataframe(clientes_filtrados, use_container_width=True)

with tab2:
    st.subheader("Portafolio de Pólizas")
    st.dataframe(polizas_filtradas, use_container_width=True)

with tab3:
    st.subheader("Registro de Siniestros")
    st.dataframe(siniestros_filtrados, use_container_width=True)

with tab4:
    st.subheader("Historial de Pagos")
    st.dataframe(pagos_filtrados, use_container_width=True)

# ========== PIE DE PÁGINA ==========
st.markdown("---")
st.markdown(
    "**Dashboard Aseguradora El Salvador** | "
    "Desarrollado con Streamlit | "
    "Datos de ejemplo generados para fines demostrativos"
)