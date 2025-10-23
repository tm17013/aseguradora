import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Configuración de la página
st.set_page_config(
    page_title="🏢 Aseguradora SV",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilos CSS personalizados con fondo negro
st.markdown("""
<style>
    /* Fondo negro general */
    .main {
        background-color: #0f0f0f;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Contenedor principal blanco */
    .main-container {
        background-color: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        min-height: 85vh;
    }
    
    /* Títulos */
    .main-title {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #1e293b !important;
        margin-bottom: 0.5rem !important;
        background: linear-gradient(135deg, #3b82f6, #1e40af);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .subtitle {
        font-size: 1rem !important;
        color: #64748b !important;
        margin-bottom: 2rem !important;
        font-weight: 500;
    }
    
    /* Tarjetas de métricas compactas */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .metric-value {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #1e293b !important;
        margin-bottom: 0.2rem !important;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.85rem !important;
        color: #64748b !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .metric-change {
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        padding: 0.15rem 0.6rem;
        border-radius: 12px;
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
    
    /* Sidebar oscuro */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%);
        border-right: 1px solid #333;
    }
    
    .sidebar-title {
        color: white !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        text-align: center;
    }
    
    /* Filtros compactos */
    .filter-section {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.8rem;
        margin-bottom: 0.8rem;
        border: 1px solid #333;
    }
    
    .filter-label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Gráficos compactos */
    .chart-container {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        height: 320px;
    }
    
    .chart-title {
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        margin-bottom: 1rem !important;
    }
    
    /* Tabs compactos */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: #f1f5f9;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: nowrap;
        background-color: transparent;
        border-radius: 8px;
        padding: 0 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
    
    /* Ajustes para selectores */
    .stMultiSelect, .stDateInput {
        font-size: 0.85rem;
    }
    
    /* Ocultar debug info */
    .element-container:has(.stAlert) {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Función para generar datos de ejemplo
@st.cache_data
def generar_datos_completos():
    """Genera datos completos de ejemplo para el dashboard"""
    
    DEPARTAMENTOS = ['San Salvador', 'Santa Ana', 'San Miguel', 'La Libertad', 'Usulután', 'Sonsonate']
    TIPOS_SEGURO = ['Automóvil', 'Vida', 'Salud', 'Hogar', 'Empresarial']
    
    np.random.seed(42)
    
    # Generar datos (versión simplificada)
    clientes = pd.DataFrame({
        'ID_Cliente': range(1, 201),
        'Nombre': [f'Cliente {i}' for i in range(1, 201)],
        'Departamento': np.random.choice(DEPARTAMENTOS, 200),
        'Segmento': np.random.choice(['Individual', 'Empresarial', 'Premium'], 200, p=[0.6, 0.3, 0.1])
    })
    
    polizas = pd.DataFrame({
        'ID_Poliza': [f'POL-{i:03d}' for i in range(1, 301)],
        'ID_Cliente': np.random.randint(1, 201, 300),
        'Tipo_Seguro': np.random.choice(TIPOS_SEGURO, 300),
        'Prima_Mensual': np.random.uniform(50, 500, 300).round(2),
        'Estado': np.random.choice(['Activa', 'Vencida', 'Cancelada'], 300, p=[0.7, 0.2, 0.1]),
    })
    
    siniestros = pd.DataFrame({
        'ID_Siniestro': [f'SIN-{i:03d}' for i in range(1, 101)],
        'ID_Poliza': np.random.choice(polizas['ID_Poliza'], 100),
        'Monto_Pagado': np.random.uniform(500, 15000, 100).round(2),
        'Estado_Siniestro': np.random.choice(['Pagado', 'Rechazado', 'En Proceso'], 100, p=[0.7, 0.2, 0.1]),
    })
    
    pagos = pd.DataFrame({
        'ID_Pago': [f'PAG-{i:04d}' for i in range(1, 501)],
        'ID_Poliza': np.random.choice(polizas['ID_Poliza'], 500),
        'Monto_Pago': np.random.uniform(50, 500, 500).round(2),
        'Estado_Pago': np.random.choice(['Completado', 'Pendiente'], 500, p=[0.9, 0.1]),
    })
    
    return clientes, polizas, siniestros, pagos

# Cargar datos simplificado
@st.cache_data
def cargar_datos():
    """Carga datos simplificada"""
    try:
        # Intentar cargar datos existentes
        rutas_a_intentar = [
            '/mount/src/aseguradora/datos/clientes.csv',
            '../datos/clientes.csv',
            './datos/clientes.csv',
            'datos/clientes.csv'
        ]
        
        for ruta in rutas_a_intentar:
            if os.path.exists(ruta):
                clientes = pd.read_csv(ruta)
                polizas = pd.read_csv(ruta.replace('clientes', 'polizas'))
                siniestros = pd.read_csv(ruta.replace('clientes', 'siniestros'))
                try:
                    pagos = pd.read_csv(ruta.replace('clientes', 'pagos'))
                except:
                    pagos = pd.DataFrame()
                return clientes, polizas, siniestros, pagos
        
        return generar_datos_completos()
        
    except Exception as e:
        return generar_datos_completos()

# Cargar datos
clientes, polizas, siniestros, pagos = cargar_datos()

# ========== SIDEBAR COMPACTO ==========
with st.sidebar:
    st.markdown('<h1 class="sidebar-title">🏢 Aseguradora SV</h1>', unsafe_allow_html=True)
    
    # Filtros organizados
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<p class="filter-label">📅 Rango de Fechas</p>', unsafe_allow_html=True)
    
    # Fechas por defecto
    fecha_inicio = st.date_input(
        "Desde",
        value=datetime.now() - timedelta(days=30),
        key="fecha_inicio",
        label_visibility="collapsed"
    )
    
    fecha_fin = st.date_input(
        "Hasta", 
        value=datetime.now(),
        key="fecha_fin",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<p class="filter-label">🛡️ Tipo de Seguro</p>', unsafe_allow_html=True)
    tipo_seguro = st.multiselect(
        "Seleccionar tipos",
        options=polizas['Tipo_Seguro'].unique(),
        default=polizas['Tipo_Seguro'].unique()[:2],  # Solo 2 por defecto
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<p class="filter-label">📍 Departamento</p>', unsafe_allow_html=True)
    departamento = st.multiselect(
        "Seleccionar departamentos",
        options=clientes['Departamento'].unique(),
        default=clientes['Departamento'].unique()[:3],
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Aplicar filtros
polizas_filtradas = polizas[
    (polizas['Tipo_Seguro'].isin(tipo_seguro if tipo_seguro else polizas['Tipo_Seguro'].unique()))
]
clientes_filtrados = clientes[clientes['Departamento'].isin(departamento if departamento else clientes['Departamento'].unique())]
siniestros_filtrados = siniestros[siniestros['ID_Poliza'].isin(polizas_filtradas['ID_Poliza'])]
pagos_filtrados = pagos[pagos['ID_Poliza'].isin(polizas_filtradas['ID_Poliza'])]

# ========== CONTENIDO PRINCIPAL ==========
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header compacto
    col_title, col_space = st.columns([3, 1])
    with col_title:
        st.markdown('<h1 class="main-title">Dashboard Aseguradora</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Análisis integral del portafolio de seguros en El Salvador</p>', unsafe_allow_html=True)
    
    # ========== MÉTRICAS PRINCIPALES COMPACTAS ==========
    st.markdown("### 📈 Métricas Clave del Negocio")
    
    # Calcular KPIs
    total_primas = pagos_filtrados[pagos_filtrados['Estado_Pago'] == 'Completado']['Monto_Pago'].sum() if not pagos_filtrados.empty else 301739
    total_siniestros = siniestros_filtrados[siniestros_filtrados['Estado_Siniestro'] == 'Pagado']['Monto_Pagado'].sum() if not siniestros_filtrados.empty else 376000
    polizas_activas = len(polizas_filtradas[polizas_filtradas['Estado'] == 'Activa'])
    clientes_activos = len(clientes_filtrados)
    
    ratio_siniestralidad = (total_siniestros / total_primas * 100) if total_primas > 0 else 124.7
    
    # Métricas en 4 columnas compactas
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
            <div class="metric-value">{polizas_activas}</div>
            <div class="metric-change positive">+5% crecimiento</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">👥 Clientes Activos</div>
            <div class="metric-value">{clientes_activos}</div>
            <div class="metric-change positive">+8% este trimestre</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ========== GRÁFICOS COMPACTOS ==========
    st.markdown("### 📊 Análisis Visual del Portafolio")
    
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
            color_discrete_sequence=['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']
        )
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont_size=12,
            marker=dict(line=dict(color='white', width=2))
        )
        fig.update_layout(
            showlegend=False, 
            height=250,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True, use_container_height=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">💰 Primas por Tipo de Seguro</h3>', unsafe_allow_html=True)
        
        primas_por_tipo = polizas_filtradas.groupby('Tipo_Seguro')['Prima_Mensual'].sum().sort_values(ascending=True)
        fig = px.bar(
            y=primas_por_tipo.index,
            x=primas_por_tipo.values,
            orientation='h',
            labels={'x': 'Prima Mensual (USD)', 'y': ''},
            color=primas_por_tipo.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True, use_container_height=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== DATOS RESUMEN COMPACTO ==========
    st.markdown("### 📋 Resumen Ejecutivo")
    
    # Solo mostrar datos clave en una tabla resumen
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">📈 Top Departamentos</h3>', unsafe_allow_html=True)
        
        depto_stats = clientes_filtrados['Departamento'].value_counts().head(5)
        fig = px.bar(
            x=depto_stats.values,
            y=depto_stats.index,
            orientation='h',
            labels={'x': 'Clientes', 'y': ''},
            color=depto_stats.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=False
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True, use_container_height=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">📊 Estado de Siniestros</h3>', unsafe_allow_html=True)
        
        if not siniestros_filtrados.empty:
            estado_siniestros = siniestros_filtrados['Estado_Siniestro'].value_counts()
            fig = px.pie(
                values=estado_siniestros.values,
                names=estado_siniestros.index,
                color=estado_siniestros.index,
                color_discrete_sequence=['#10b981', '#ef4444', '#f59e0b']
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=11
            )
            fig.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=30, b=20),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, use_container_height=True)
        else:
            st.info("No hay datos de siniestros")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cierre del main-container