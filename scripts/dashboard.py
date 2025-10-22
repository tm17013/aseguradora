import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Configuración de la página con tema personalizado
st.set_page_config(
    page_title="🏢 Aseguradora SV Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilos CSS personalizados
st.markdown("""
<style>
    /* Estilos generales */
    .main {
        background-color: #f8fafc;
    }
    
    /* Títulos principales */
    .main-title {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        margin-bottom: 0.5rem !important;
    }
    
    .subtitle {
        font-size: 1.1rem !important;
        color: #64748b !important;
        margin-bottom: 2rem !important;
    }
    
    /* Tarjetas de métricas */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 4px solid #3b82f6;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .metric-value {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        margin-bottom: 0.25rem !important;
    }
    
    .metric-label {
        font-size: 0.9rem !important;
        color: #64748b !important;
        font-weight: 500 !important;
    }
    
    .metric-change {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        display: inline-block;
    }
    
    .positive {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .negative {
        background-color: #fee2e2;
        color: #dc2626;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
    }
    
    .sidebar-title {
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
    }
    
    /* Filtros */
    .filter-section {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .filter-label {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Gráficos */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        margin-bottom: 1rem !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f5f9;
        border-radius: 8px 8px 0px 0px;
        gap: 1rem;
        padding: 1rem 2rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Función para generar datos de ejemplo (manteniendo tu función original)
@st.cache_data
def generar_datos_completos():
    """Genera datos completos de ejemplo para el dashboard"""
    
    # Configuración para El Salvador
    DEPARTAMENTOS = ['San Salvador', 'Santa Ana', 'San Miguel', 'La Libertad', 'Usulután', 'Sonsonate']
    TIPOS_SEGURO = ['Automóvil', 'Vida', 'Salud', 'Hogar', 'Empresarial']
    
    np.random.seed(42)
    
    # 1. GENERAR CLIENTES (200 clientes)
    clientes = pd.DataFrame({
        'ID_Cliente': range(1, 201),
        'Nombre': [f'Cliente {i}' for i in range(1, 201)],
        'Edad': np.random.randint(25, 65, 200),
        'Genero': np.random.choice(['M', 'F'], 200),
        'Departamento': np.random.choice(DEPARTAMENTOS, 200),
        'Email': [f'cliente{i}@email.com' for i in range(1, 201)],
        'Telefono': [f'7{np.random.randint(1000000, 9999999)}' for _ in range(200)],
        'Fecha_Registro': pd.date_range('2020-01-01', periods=200, freq='D'),
        'Segmento': np.random.choice(['Individual', 'Empresarial', 'Premium'], 200, p=[0.6, 0.3, 0.1])
    })
    
    # 2. GENERAR PÓLIZAS (300 pólizas)
    polizas = pd.DataFrame({
        'ID_Poliza': [f'POL-{i:03d}' for i in range(1, 301)],
        'ID_Cliente': np.random.randint(1, 201, 300),
        'Tipo_Seguro': np.random.choice(TIPOS_SEGURO, 300),
        'Monto_Asegurado': np.random.uniform(5000, 100000, 300).round(2),
        'Prima_Mensual': np.random.uniform(50, 500, 300).round(2),
        'Fecha_Inicio': pd.date_range('2022-01-01', periods=300, freq='D'),
        'Fecha_Vencimiento': pd.date_range('2023-01-01', periods=300, freq='D'),
        'Estado': np.random.choice(['Activa', 'Vencida', 'Cancelada'], 300, p=[0.7, 0.2, 0.1]),
        'Vendedor': [f'Vendedor {np.random.randint(1, 11)}' for _ in range(300)]
    })
    
    # 3. GENERAR SINIESTROS (100 siniestros)
    siniestros = pd.DataFrame({
        'ID_Siniestro': [f'SIN-{i:03d}' for i in range(1, 101)],
        'ID_Poliza': np.random.choice(polizas['ID_Poliza'], 100),
        'Fecha_Siniestro': pd.date_range('2022-06-01', periods=100, freq='D'),
        'Tipo_Siniestro': np.random.choice(['Colisión', 'Robo', 'Incendio', 'Hospitalización', 'Muerte'], 100),
        'Monto_Reclamado': np.random.uniform(1000, 20000, 100).round(2),
        'Monto_Pagado': np.random.uniform(500, 15000, 100).round(2),
        'Estado_Siniestro': np.random.choice(['Pagado', 'Rechazado', 'En Proceso'], 100, p=[0.7, 0.2, 0.1]),
        'Departamento_Siniestro': np.random.choice(DEPARTAMENTOS, 100)
    })
    
    # 4. GENERAR PAGOS
    pagos = []
    pago_id = 1
    
    for _, poliza in polizas.iterrows():
        if poliza['Estado'] == 'Activa':
            # Generar 6-12 pagos por póliza
            num_pagos = np.random.randint(6, 13)
            for mes in range(num_pagos):
                fecha_pago = poliza['Fecha_Inicio'] + timedelta(days=30 * mes)
                if fecha_pago < datetime.now():
                    pagos.append({
                        'ID_Pago': f'PAG-{pago_id:04d}',
                        'ID_Poliza': poliza['ID_Poliza'],
                        'Fecha_Pago': fecha_pago,
                        'Monto_Pago': poliza['Prima_Mensual'],
                        'Estado_Pago': np.random.choice(['Completado', 'Pendiente'], p=[0.9, 0.1]),
                        'Metodo_Pago': np.random.choice(['Transferencia', 'Tarjeta', 'Efectivo'])
                    })
                    pago_id += 1
    
    pagos_df = pd.DataFrame(pagos)
    
    return clientes, polizas, siniestros, pagos_df

# Cargar datos
@st.cache_data
def cargar_datos():
    """Carga datos - CORREGIDO para Streamlit Cloud"""
    
    try:
        # Intentar rutas ABSOLUTAS para Streamlit Cloud
        rutas_a_intentar = [
            '/mount/src/aseguradora/datos/clientes.csv',
            '../datos/clientes.csv',
            './datos/clientes.csv',
            'datos/clientes.csv',
            'clientes.csv'
        ]
        
        archivos_encontrados = False
        
        for ruta in rutas_a_intentar:
            if os.path.exists(ruta):
                st.success(f"Datos cargados desde: {ruta}")
                clientes = pd.read_csv(ruta)
                polizas = pd.read_csv(ruta.replace('clientes', 'polizas'))
                siniestros = pd.read_csv(ruta.replace('clientes', 'siniestros'))
                
                try:
                    pagos = pd.read_csv(ruta.replace('clientes', 'pagos'))
                except:
                    pagos = pd.DataFrame()
                
                archivos_encontrados = True
                break
        
        if not archivos_encontrados:
            st.info("No se encontraron archivos CSV. Generando datos de ejemplo...")
            clientes, polizas, siniestros, pagos = generar_datos_completos()
            
        return clientes, polizas, siniestros, pagos
        
    except Exception as e:
        st.warning(f"Error cargando archivos: {e}")
        st.info("Generando datos de ejemplo como respaldo...")
        return generar_datos_completos()

# Cargar los datos
clientes, polizas, siniestros, pagos = cargar_datos()

# Si no hay pagos, crear dataframe vacío
if pagos.empty:
    pagos = pd.DataFrame(columns=['ID_Pago', 'ID_Poliza', 'Fecha_Pago', 'Monto_Pago', 'Estado_Pago', 'Metodo_Pago'])

# ========== SIDEBAR CON FILTROS ==========
with st.sidebar:
    st.markdown('<h1 class="sidebar-title">🏢 Aseguradora SV</h1>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtros en secciones organizadas
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<p class="filter-label">📅 Rango de Fechas</p>', unsafe_allow_html=True)
    
    if not pagos.empty and 'Fecha_Pago' in pagos.columns:
        try:
            fecha_min = pd.to_datetime(pagos['Fecha_Pago']).min()
            fecha_max = pd.to_datetime(pagos['Fecha_Pago']).max()
            
            rango_fechas = st.date_input(
                "",
                value=[fecha_min.date(), fecha_max.date()],
                min_value=fecha_min.date(),
                max_value=fecha_max.date(),
                label_visibility="collapsed"
            )
        except:
            st.info("Fechas no disponibles")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<p class="filter-label">🛡️ Tipo de Seguro</p>', unsafe_allow_html=True)
    tipo_seguro = st.multiselect(
        "",
        options=polizas['Tipo_Seguro'].unique(),
        default=polizas['Tipo_Seguro'].unique(),
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<p class="filter-label">📍 Departamento</p>', unsafe_allow_html=True)
    departamento = st.multiselect(
        "",
        options=clientes['Departamento'].unique(),
        default=clientes['Departamento'].unique(),
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<p class="filter-label">📊 Estado Póliza</p>', unsafe_allow_html=True)
    estado_poliza = st.multiselect(
        "",
        options=polizas['Estado'].unique(),
        default=['Activa'],
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**🔧 Configuración**")
    st.info("Dashboard Aseguradora El Salvador")

# Aplicar filtros
polizas_filtradas = polizas[
    (polizas['Tipo_Seguro'].isin(tipo_seguro)) & 
    (polizas['Estado'].isin(estado_poliza))
]

clientes_filtrados = clientes[clientes['Departamento'].isin(departamento)]

# Filtrar siniestros y pagos basados en pólizas filtradas
siniestros_filtrados = siniestros[siniestros['ID_Poliza'].isin(polizas_filtradas['ID_Poliza'])]
pagos_filtrados = pagos[pagos['ID_Poliza'].isin(polizas_filtradas['ID_Poliza'])]

# ========== HEADER PRINCIPAL ==========
st.markdown('<h1 class="main-title">Dashboard Aseguradora</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análisis integral del portafolio de seguros en El Salvador</p>', unsafe_allow_html=True)

# ========== MÉTRICAS PRINCIPALES ==========
st.subheader("📈 Métricas Clave del Negocio")

# Calcular KPIs
if not pagos_filtrados.empty:
    total_primas = pagos_filtrados[pagos_filtrados['Estado_Pago'] == 'Completado']['Monto_Pago'].sum()
else:
    total_primas = polizas_filtradas['Prima_Mensual'].sum() * 12  # Estimación

total_siniestros = siniestros_filtrados[siniestros_filtrados['Estado_Siniestro'] == 'Pagado']['Monto_Pagado'].sum()
polizas_activas = len(polizas_filtradas[polizas_filtradas['Estado'] == 'Activa'])
clientes_activos = len(clientes_filtrados)

# Calcular ratio de siniestralidad (evitar división por cero)
ratio_siniestralidad = (total_siniestros / total_primas * 100) if total_primas > 0 else 0

# Mostrar KPIs en columnas con diseño mejorado
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💰 Total Primas</div>
        <div class="metric-value">${total_primas:,.0f}</div>
        <div class="metric-change positive">+12% vs mes anterior</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📊 Ratio Siniestral</div>
        <div class="metric-value">{ratio_siniestralidad:.1f}%</div>
        <div class="metric-change {'negative' if ratio_siniestralidad > 50 else 'positive'}">
            {'↑' if ratio_siniestralidad > 50 else '↓'} vs objetivo
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🛡️ Pólizas Activas</div>
        <div class="metric-value">{polizas_activas:,}</div>
        <div class="metric-change positive">+5% crecimiento</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">👥 Clientes Activos</div>
        <div class="metric-value">{clientes_activos:,}</div>
        <div class="metric-change positive">+8% este trimestre</div>
    </div>
    """, unsafe_allow_html=True)

# ========== GRÁFICOS INTERACTIVOS ==========
st.markdown("---")
st.subheader("📊 Análisis Visual del Portafolio")

# Primera fila de gráficos
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">🛡️ Distribución por Tipo de Seguro</h3>', unsafe_allow_html=True)
    
    tipo_counts = polizas_filtradas['Tipo_Seguro'].value_counts()
    fig = px.pie(
        values=tipo_counts.values,
        names=tipo_counts.index,
        color=tipo_counts.index,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">💰 Primas por Tipo de Seguro</h3>', unsafe_allow_html=True)
    
    primas_por_tipo = polizas_filtradas.groupby('Tipo_Seguro')['Prima_Mensual'].sum().sort_values(ascending=False)
    fig = px.bar(
        x=primas_por_tipo.index,
        y=primas_por_tipo.values,
        labels={'x': 'Tipo de Seguro', 'y': 'Prima Mensual (USD)'},
        color=primas_por_tipo.values,
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Segunda fila de gráficos
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">📍 Distribución Geográfica</h3>', unsafe_allow_html=True)
    
    clientes_por_depto = clientes_filtrados['Departamento'].value_counts()
    fig = px.bar(
        x=clientes_por_depto.index,
        y=clientes_por_depto.values,
        labels={'x': 'Departamento', 'y': 'Número de Clientes'},
        color=clientes_por_depto.values,
        color_continuous_scale='Blues'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">📈 Evolución de Siniestros</h3>', unsafe_allow_html=True)
    
    # Agrupar siniestros por mes
    if not siniestros_filtrados.empty:
        siniestros_filtrados['Fecha_Siniestro'] = pd.to_datetime(siniestros_filtrados['Fecha_Siniestro'])
        siniestros_por_mes = siniestros_filtrados.groupby(siniestros_filtrados['Fecha_Siniestro'].dt.to_period('M')).size()
        siniestros_por_mes.index = siniestros_por_mes.index.astype(str)
        
        fig = px.line(
            x=siniestros_por_mes.index,
            y=siniestros_por_mes.values,
            labels={'x': 'Mes', 'y': 'Número de Siniestros'},
            markers=True
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de siniestros para mostrar")
    st.markdown('</div>', unsafe_allow_html=True)

# ========== DATOS DETALLADOS ==========
st.markdown("---")
st.subheader("📋 Datos Detallados")

tab1, tab2, tab3, tab4 = st.tabs(["👥 Clientes", "🛡️ Pólizas", "📋 Siniestros", "💰 Pagos"])

with tab1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">Base de Clientes</h3>', unsafe_allow_html=True)
    st.dataframe(clientes_filtrados, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">Portafolio de Pólizas</h3>', unsafe_allow_html=True)
    st.dataframe(polizas_filtradas, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">Registro de Siniestros</h3>', unsafe_allow_html=True)
    st.dataframe(siniestros_filtrados, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">Historial de Pagos</h3>', unsafe_allow_html=True)
    if not pagos_filtrados.empty:
        st.dataframe(pagos_filtrados, use_container_width=True)
    else:
        st.info("No hay datos de pagos disponibles")
    st.markdown('</div>', unsafe_allow_html=True)

# ========== PIE DE PÁGINA ==========
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #64748b; padding: 2rem 0;'>
        <strong>Dashboard Aseguradora El Salvador</strong> | 
        Desarrollado con Streamlit | 
        Optimizado para Streamlit Cloud
    </div>
    """, 
    unsafe_allow_html=True
)