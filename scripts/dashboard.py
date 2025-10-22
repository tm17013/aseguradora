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
    page_title="Dashboard Aseguradora SV",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏢 Dashboard Aseguradora - El Salvador")
st.markdown("---")

# DEBUG: Mostrar información del sistema
st.sidebar.info("🔧 Modo: Streamlit Cloud")

# Función para generar datos de ejemplo
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

# Cargar datos - VERSIÓN CORREGIDA PARA STREAMLIT CLOUD
@st.cache_data
def cargar_datos():
    """Carga datos - CORREGIDO para Streamlit Cloud"""
    
    # Mostrar información de debug
    current_dir = os.getcwd()
    st.sidebar.write(f"Directorio: {current_dir}")
    
    try:
        # EN STREAMLIT CLOUD, el dashboard.py está en /scripts/
        # pero los datos deberían estar en la raíz: /datos/
        
        # Intentar rutas ABSOLUTAS para Streamlit Cloud
        rutas_a_intentar = [
            '/mount/src/aseguradora/datos/clientes.csv',  # Ruta ABSOLUTA en Streamlit Cloud
            '../datos/clientes.csv',                      # Subir un nivel desde /scripts/
            './datos/clientes.csv',                       # Relativo al script
            'datos/clientes.csv',                         # Relativo al directorio de trabajo
            'clientes.csv'                                # En el mismo directorio
        ]
        
        archivos_encontrados = False
        
        for ruta in rutas_a_intentar:
            if os.path.exists(ruta):
                st.success(f"Datos cargados desde: {ruta}")
                clientes = pd.read_csv(ruta)
                polizas = pd.read_csv(ruta.replace('clientes', 'polizas'))
                siniestros = pd.read_csv(ruta.replace('clientes', 'siniestros'))
                
                # Intentar cargar pagos (puede no existir)
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
st.sidebar.title("🔍 Filtros")

# Filtro por fecha (si existen los datos de pagos)
if not pagos.empty and 'Fecha_Pago' in pagos.columns:
    try:
        fecha_min = pagos['Fecha_Pago'].min()
        fecha_max = pagos['Fecha_Pago'].max()
        
        rango_fechas = st.sidebar.date_input(
            "Rango de Fechas",
            value=[fecha_min.date(), fecha_max.date()],
            min_value=fecha_min.date(),
            max_value=fecha_max.date()
        )
    except:
        st.sidebar.info("Fechas no disponibles")

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

# Aplicar filtros
polizas_filtradas = polizas[
    (polizas['Tipo_Seguro'].isin(tipo_seguro)) & 
    (polizas['Estado'].isin(estado_poliza))
]

clientes_filtrados = clientes[clientes['Departamento'].isin(departamento)]

# Filtrar siniestros y pagos basados en pólizas filtradas
siniestros_filtrados = siniestros[siniestros['ID_Poliza'].isin(polizas_filtradas['ID_Poliza'])]
pagos_filtrados = pagos[pagos['ID_Poliza'].isin(polizas_filtradas['ID_Poliza'])]

# ========== MÉTRICAS PRINCIPALES ==========
st.header("📈 Métricas Principales")

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

# Mostrar KPIs en columnas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Primas", f"${total_primas:,.0f}")

with col2:
    st.metric("Ratio Siniestral", f"{ratio_siniestralidad:.1f}%")

with col3:
    st.metric("Pólizas Activas", f"{polizas_activas:,}")

with col4:
    st.metric("Clientes Activos", f"{clientes_activos:,}")

# ========== GRÁFICOS INTERACTIVOS ==========
st.header("Análisis Visual")

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
    primas_por_tipo = polizas_filtradas.groupby('Tipo_Seguro')['Prima_Mensual'].sum().sort_values(ascending=False)
    fig = px.bar(
        x=primas_por_tipo.index,
        y=primas_por_tipo.values,
        labels={'x': 'Tipo de Seguro', 'y': 'Prima Mensual (USD)'},
        color=primas_por_tipo.values,
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_container_width=True)

# Gráfico geográfico
st.subheader("Distribución Geográfica")
clientes_por_depto = clientes_filtrados['Departamento'].value_counts()
fig = px.bar(
    x=clientes_por_depto.index,
    y=clientes_por_depto.values,
    labels={'x': 'Departamento', 'y': 'Número de Clientes'},
    color=clientes_por_depto.values,
    color_continuous_scale='Viridis'
)
st.plotly_chart(fig, use_container_width=True)

# ========== DATOS DETALLADOS ==========
st.header("Datos Detallados")

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
    if not pagos_filtrados.empty:
        st.dataframe(pagos_filtrados, use_container_width=True)
    else:
        st.info("No hay datos de pagos disponibles")

# ========== PIE DE PÁGINA ==========
st.markdown("---")
st.markdown(
    "**Dashboard Aseguradora El Salvador** | "
    "Desarrollado con Streamlit | "
    "Optimizado para Streamlit Cloud"
)

# Información de debug expandible
with st.expander("Información de Sistema"):
    st.write(f"Directorio actual: {os.getcwd()}")
    st.write(f"Python version: {sys.version}")
    st.write(f"Total clientes: {len(clientes)}")
    st.write(f"Total pólizas: {len(polizas)}")
    st.write(f"Total siniestros: {len(siniestros)}")
    st.write(f"Total pagos: {len(pagos)}")
    
    # Listar archivos en directorio actual
    st.write("Archivos en directorio actual:")
    try:
        files = os.listdir('.')
        st.write(files)
    except Exception as e:
        st.write(f"Error listando archivos: {e}")