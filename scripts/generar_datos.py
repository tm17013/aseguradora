# scripts/generar_datos.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
Faker = Faker('es_ES')
import random
import os

def generar_datos_aseguradora():
    print("Generando base de datos de la aseguradora...")
    
    # Configuración para El Salvador
    DEPARTAMENTOS = [
        'San Salvador', 'Santa Ana', 'San Miguel', 'La Libertad', 'Usulután',
        'Sonsonate', 'La Paz', 'Chalatenango', 'Cuscatlán', 'Ahuachapán',
        'Morazán', 'La Unión', 'Cabañas', 'San Vicente'
    ]
    
    MUNICIPIOS_POR_DEPTO = {
        'San Salvador': ['San Salvador', 'Soyapango', 'Apopa', 'Mejicanos', 'Delgado'],
        'Santa Ana': ['Santa Ana', 'Chalchuapa', 'Metapán'],
        'San Miguel': ['San Miguel', 'Chinameca', 'Nueva Guadalupe'],
        'La Libertad': ['Santa Tecla', 'Antiguo Cuscatlán', 'Zaragoza']
    }
    
    TIPOS_SEGURO = ['Automóvil', 'Vida', 'Salud', 'Hogar', 'Empresarial', 'Agrícola']
    
    # 1. GENERAR CLIENTES (500 clientes)
    print("Generando clientes...")
    clientes = []
    for i in range(1, 501):
        depto = random.choice(DEPARTAMENTOS)
        municipio = random.choice(MUNICIPIOS_POR_DEPTO.get(depto, ['Municipio Principal']))
        
        clientes.append({
            'ID_Cliente': i,
            'Nombre': Faker.name(),
            'Edad': random.randint(18, 80),
            'Genero': random.choice(['M', 'F']),
            'Departamento': depto,
            'Municipio': municipio,
            'Email': Faker.email(),
            'Telefono': f"7{random.randint(1000000, 9999999)}",
            'Fecha_Registro': Faker.date_between(start_date='-3y', end_date='today'),
            'Segmento': random.choice(['Individual', 'Empresarial', 'Premium'])
        })
    
    # 2. GENERAR PÓLIZAS (800 pólizas)
    print("Generando pólizas...")
    polizas = []
    for i in range(1, 801):
        fecha_inicio = Faker.date_between(start_date='-2y', end_date='today')
        fecha_vencimiento = fecha_inicio + timedelta(days=365)
        
        polizas.append({
            'ID_Poliza': f'POL-{i:04d}',
            'ID_Cliente': random.randint(1, 500),
            'Tipo_Seguro': random.choice(TIPOS_SEGURO),
            'Monto_Asegurado': round(random.uniform(5000, 100000), 2),
            'Prima_Mensual': round(random.uniform(25, 300), 2),
            'Fecha_Inicio': fecha_inicio,
            'Fecha_Vencimiento': fecha_vencimiento,
            'Estado': random.choices(['Activa', 'Vencida', 'Cancelada'], weights=[0.8, 0.15, 0.05])[0],
            'Vendedor': Faker.name()
        })
    
    # 3. GENERAR SINIESTROS (250 siniestros)
    print("Generando siniestros...")
    siniestros = []
    for i in range(1, 251):
        poliza_valida = random.choice([p for p in polizas if p['Estado'] == 'Activa'])
        fecha_siniestro = Faker.date_between(
            start_date=poliza_valida['Fecha_Inicio'], 
            end_date=min(poliza_valida['Fecha_Vencimiento'], datetime.now().date())
        )
        
        monto_reclamado = round(random.uniform(100, 15000), 2)
        
        siniestros.append({
            'ID_Siniestro': f'SIN-{i:04d}',
            'ID_Poliza': poliza_valida['ID_Poliza'],
            'Fecha_Siniestro': fecha_siniestro,
            'Tipo_Siniestro': random.choice(['Colisión', 'Robo', 'Incendio', 'Hospitalización', 'Muerte']),
            'Monto_Reclamado': monto_reclamado,
            'Monto_Pagado': round(monto_reclamado * random.uniform(0.7, 1.0), 2),
            'Estado_Siniestro': random.choices(['Pagado', 'Rechazado', 'En Proceso'], weights=[0.7, 0.2, 0.1])[0],
            'Departamento_Siniestro': random.choice(DEPARTAMENTOS)
        })
    
    # 4. GENERAR PAGOS
    print("Generando pagos...")
    pagos = []
    pago_id = 1
    
    for poliza in polizas:
        if poliza['Estado'] == 'Activa':
            # Generar pagos mensuales desde inicio hasta hoy
            fecha_actual = poliza['Fecha_Inicio']
            while fecha_actual <= datetime.now().date() and fecha_actual <= poliza['Fecha_Vencimiento']:
                pagos.append({
                    'ID_Pago': f'PAG-{pago_id:05d}',
                    'ID_Poliza': poliza['ID_Poliza'],
                    'Fecha_Pago': fecha_actual,
                    'Monto_Pago': poliza['Prima_Mensual'],
                    'Estado_Pago': random.choices(['Completado', 'Pendiente'], weights=[0.9, 0.1])[0],
                    'Metodo_Pago': random.choice(['Transferencia', 'Tarjeta', 'Efectivo'])
                })
                pago_id += 1
                fecha_actual += timedelta(days=30)  # Aprox 1 mes
    
    # Convertir a DataFrames
    df_clientes = pd.DataFrame(clientes)
    df_polizas = pd.DataFrame(polizas)
    df_siniestros = pd.DataFrame(siniestros)
    df_pagos = pd.DataFrame(pagos)
    
    return df_clientes, df_polizas, df_siniestros, df_pagos

def guardar_datos(df_clientes, df_polizas, df_siniestros, df_pagos):
    """Guarda los DataFrames como archivos CSV"""
    print("Guardando datos...")
    
    # Asegurar que la carpeta datos existe
    os.makedirs('../datos', exist_ok=True)
    
    # Guardar archivos
    df_clientes.to_csv('../datos/clientes.csv', index=False, encoding='utf-8-sig')
    df_polizas.to_csv('../datos/polizas.csv', index=False, encoding='utf-8-sig')
    df_siniestros.to_csv('../datos/siniestros.csv', index=False, encoding='utf-8-sig')
    df_pagos.to_csv('../datos/pagos.csv', index=False, encoding='utf-8-sig')
    
    print("Datos guardados en la carpeta 'datos/'")

def mostrar_estadisticas(df_clientes, df_polizas, df_siniestros, df_pagos):
    """Muestra estadísticas básicas de los datos generados"""
    print("\nESTADÍSTICAS DE LOS DATOS GENERADOS:")
    print("=" * 40)
    print(f"Clientes: {len(df_clientes)}")
    print(f"Pólizas: {len(df_polizas)}")
    print(f"Siniestros: {len(df_siniestros)}")
    print(f"Pagos: {len(df_pagos)}")
    
    print(f"\nPrimas mensuales totales: ${df_polizas['Prima_Mensual'].sum():,.2f}")
    print(f"Monto total siniestros: ${df_siniestros['Monto_Pagado'].sum():,.2f}")
    
    print(f"\nDistribución por departamento:")
    print(df_clientes['Departamento'].value_counts().head())

if __name__ == "__main__":
    print("GENERADOR DE DATOS - ASEGURADORA EL SALVADOR")
    print("=" * 50)
    
    # Generar datos
    df_clientes, df_polizas, df_siniestros, df_pagos = generar_datos_aseguradora()
    
    # Guardar datos
    guardar_datos(df_clientes, df_polizas, df_siniestros, df_pagos)
    
    # Mostrar estadísticas
    mostrar_estadisticas(df_clientes, df_polizas, df_siniestros, df_pagos)
    
    print("\n¡Base de datos generada exitosamente!")
    print("Archivos guardados en: datos/")