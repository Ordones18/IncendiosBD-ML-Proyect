# -*- coding: utf-8 -*-
# =========================================================================
# Proyecto de InvestigaciÃ³n Formativa: PredicciÃ³n de Incendios Forestales
# Fase 5: Carga de Datos a SQL Server
# Archivo: cargar_datos_sql.py
# =========================================================================

import os
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine, text
import time
import warnings
warnings.filterwarnings('ignore')

print("Iniciando el proceso de carga de datos a SQL Server...")

# Definir directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. ConfiguraciÃ³n de conexiÃ³n (usando la instancia LUIS)
CONN_STR = "mssql+pyodbc://LUIS/IncendiosForestalesEC?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
engine = create_engine(CONN_STR)

# 2. Cargar e Insertar Ciudades (Tabla de DimensiÃ³n)
cities_data = [
    {'id_ciudad': 1, 'nombre': 'Quito', 'region': 'Sierra', 'latitud': -0.1807, 'longitud': -78.4678, 'altitud_msnm': 2850.0},
    {'id_ciudad': 2, 'nombre': 'Guayaquil', 'region': 'Costa', 'latitud': -2.1894, 'longitud': -79.8890, 'altitud_msnm': 4.0},
    {'id_ciudad': 3, 'nombre': 'Riobamba', 'region': 'Sierra', 'latitud': -1.6731, 'longitud': -78.6530, 'altitud_msnm': 2754.0},
    {'id_ciudad': 4, 'nombre': 'Cuenca', 'region': 'Sierra', 'latitud': -2.9001, 'longitud': -79.0060, 'altitud_msnm': 2560.0}
]
df_cities = pd.DataFrame(cities_data)

try:
    print("Insertando ciudades...")
    # Limpiar las tablas antes por si acaso
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM Incendios;"))
        conn.execute(text("DELETE FROM Clima;"))
        conn.execute(text("DELETE FROM NDVI;"))
        conn.execute(text("DELETE FROM Ciudades;"))
        conn.commit()
    df_cities.to_sql('Ciudades', con=engine, if_exists='append', index=False)
    print("Ciudades insertadas con Ã©xito.")
except Exception as e:
    print(f"Error al insertar ciudades: {e}")
    raise e

# 3. Cargar y Preprocesar Clima Diario
clima_path = os.path.join(BASE_DIR, 'data', 'clima_diario_4ciudades.csv')
if os.path.exists(clima_path):
    print("\nProcesando clima diario...")
    df_clima = pd.read_csv(clima_path)
    
    # Imputar valores nulos (que corresponden a -999) agrupando por ciudad
    # Usamos ffill() y bfill() para rellenar los nulos con dÃ­as adyacentes
    print("- Imputando valores nulos en el clima...")
    df_clima = df_clima.groupby('ciudad').apply(lambda g: g.ffill().bfill()).reset_index(drop=True)
    
    # Mapear nombre de ciudad a id_ciudad
    city_map = {'Quito': 1, 'Guayaquil': 2, 'Riobamba': 3, 'Cuenca': 4}
    df_clima['id_ciudad'] = df_clima['ciudad'].map(city_map)
    
    # Renombrar columnas para que coincidan con la tabla Clima
    df_clima = df_clima.rename(columns={
        'temperatura_media': 'temperatura_media',
        'temperatura_max': 'temperatura_max',
        'temperatura_min': 'temperatura_min',
        'humedad_relativa': 'humedad_relativa',
        'precipitacion': 'precipitacion',
        'velocidad_viento': 'velocidad_viento',
        'direccion_viento': 'direccion_viento'
    })
    
    # Seleccionar columnas necesarias
    clima_cols = ['id_ciudad', 'fecha', 'velocidad_viento', 'direccion_viento', 
                  'temperatura_media', 'temperatura_max', 'temperatura_min', 
                  'humedad_relativa', 'precipitacion']
    df_clima_final = df_clima[clima_cols].drop_duplicates(subset=['id_ciudad', 'fecha'])
    
    print(f"- Insertando {len(df_clima_final)} registros en la tabla Clima...")
    t0 = time.time()
    df_clima_final.to_sql('Clima', con=engine, if_exists='append', index=False, chunksize=2000)
    print(f"Clima insertado con Ã©xito en {time.time() - t0:.2f} segundos.")
else:
    print("Error: clima_diario_4ciudades.csv no encontrado.")

# 4. Cargar y Preprocesar NDVI
ndvi_path = os.path.join(BASE_DIR, 'data', 'NDVI-Ecuador-Cities-MOD13Q1-061-results.csv')
if os.path.exists(ndvi_path):
    print("\nProcesando NDVI...")
    df_ndvi = pd.read_csv(ndvi_path)
    
    # Mapear nombre de ciudad a id_ciudad (columna ID es el nombre de la ciudad)
    city_map = {'Quito': 1, 'Guayaquil': 2, 'Riobamba': 3, 'Cuenca': 4}
    df_ndvi['id_ciudad'] = df_ndvi['ID'].map(city_map)
    
    # Renombrar columnas
    df_ndvi = df_ndvi.rename(columns={
        'Date': 'fecha',
        'MOD13Q1_061__250m_16_days_NDVI': 'ndvi',
        'MOD13Q1_061__250m_16_days_VI_Quality': 'vi_quality',
        'MOD13Q1_061__250m_16_days_pixel_reliability': 'pixel_reliability',
        'MODIS_Tile': 'modis_tile'
    })
    
    # Agregar columna 'evi' como NULL ya que no estÃ¡ en el dataset
    df_ndvi['evi'] = None
    
    # Filtrar filas donde la ciudad sea vÃ¡lida
    df_ndvi = df_ndvi[df_ndvi['id_ciudad'].notnull()]
    df_ndvi['id_ciudad'] = df_ndvi['id_ciudad'].astype(int)
    
    # Rellenar posibles nulos
    df_ndvi['ndvi'] = df_ndvi['ndvi'].ffill().bfill()
    df_ndvi['vi_quality'] = df_ndvi['vi_quality'].fillna(0).astype(int)
    df_ndvi['pixel_reliability'] = df_ndvi['pixel_reliability'].fillna(0).astype(int)
    df_ndvi['modis_tile'] = df_ndvi['modis_tile'].fillna('h10v09')
    
    # Seleccionar columnas necesarias
    ndvi_cols = ['id_ciudad', 'fecha', 'ndvi', 'evi', 'vi_quality', 'pixel_reliability', 'modis_tile']
    df_ndvi_final = df_ndvi[ndvi_cols].drop_duplicates(subset=['id_ciudad', 'fecha'])
    
    print(f"- Insertando {len(df_ndvi_final)} registros en la tabla NDVI...")
    df_ndvi_final.to_sql('NDVI', con=engine, if_exists='append', index=False)
    print("NDVI insertado con Ã©xito.")
else:
    print("Error: NDVI-Ecuador-Cities-MOD13Q1-061-results.csv no encontrado.")

# 5. Cargar y Asociar Historial de Incendios
incendios_path = os.path.join(BASE_DIR, 'data', 'fire_archive_M-C61_761089.csv')
if os.path.exists(incendios_path):
    print("\nProcesando historial de incendios (NASA FIRMS)...")
    df_incendios = pd.read_csv(incendios_path)
    
    # Coordenadas de las 4 ciudades para asignaciÃ³n por proximidad
    cities_coords = {
        1: (-0.1807, -78.4678),  # Quito
        2: (-2.1894, -79.8890),  # Guayaquil
        3: (-1.6731, -78.6530),  # Riobamba
        4: (-2.9001, -79.0060)   # Cuenca
    }
    
    lats = df_incendios['latitude'].values
    lons = df_incendios['longitude'].values
    
    # CÃ¡lculo vectorial de distancias a las 4 ciudades
    print("- Calculando ciudad mÃ¡s cercana geogrÃ¡ficamente para cada detecciÃ³n...")
    dists = []
    city_ids = sorted(cities_coords.keys())
    for cid in city_ids:
        clat, clon = cities_coords[cid]
        # Distancia euclidiana aproximada
        dist = np.sqrt((lats - clat)**2 + (lons - clon)**2)
        dists.append(dist)
        
    dists = np.column_stack(dists) # Matriz de distancias (N, 4)
    closest_indices = np.argmin(dists, axis=1)
    closest_city_ids = [city_ids[idx] for idx in closest_indices]
    
    df_incendios['id_ciudad'] = closest_city_ids
    
    # Renombrar columnas para que coincidan con la tabla Incendios
    df_incendios_final = df_incendios.rename(columns={
        'latitude': 'latitud',
        'longitude': 'longitud',
        'acq_date': 'fecha_deteccion',
        'acq_time': 'hora_deteccion',
        'satellite': 'satelite',
        'instrument': 'instrumento',
        'confidence': 'confianza',
        'daynight': 'dia_noche',
        'type': 'tipo'
    })
    
    # Asegurar que dia_noche sea char(1)
    df_incendios_final['dia_noche'] = df_incendios_final['dia_noche'].str.strip().str[0]
    
    # Columnas requeridas por la base de datos
    incendios_cols = ['id_ciudad', 'latitud', 'longitud', 'brightness', 'scan', 'track', 
                      'fecha_deteccion', 'hora_deteccion', 'satelite', 'instrumento', 
                      'confianza', 'version', 'bright_t31', 'frp', 'dia_noche', 'tipo']
    
    df_incendios_final = df_incendios_final[incendios_cols]
    
    print(f"- Insertando {len(df_incendios_final)} registros en la tabla Incendios...")
    t0 = time.time()
    df_incendios_final.to_sql('Incendios', con=engine, if_exists='append', index=False, chunksize=5000)
    print(f"Incendios insertados con exito en {time.time() - t0:.2f} segundos.")
else:
    print("Error: fire_archive_M-C61_761089.csv no encontrado.")

# 6. Comprobacion final y conteo de registros en la base de datos
print("\n=== VERIFICACION FINAL DE LA BASE DE DATOS ===")
try:
    with engine.connect() as conn:
        r_ciu = conn.execute(text("SELECT COUNT(*) FROM Ciudades;")).fetchone()[0]
        r_cli = conn.execute(text("SELECT COUNT(*) FROM Clima;")).fetchone()[0]
        r_ndv = conn.execute(text("SELECT COUNT(*) FROM NDVI;")).fetchone()[0]
        r_inc = conn.execute(text("SELECT COUNT(*) FROM Incendios;")).fetchone()[0]
        r_aud = conn.execute(text("SELECT COUNT(*) FROM Auditoria;")).fetchone()[0]
        
        print(f"Registros en Ciudades: {r_ciu}")
        print(f"Registros en Clima: {r_cli}")
        print(f"Registros en NDVI: {r_ndv}")
        print(f"Registros en Incendios: {r_inc}")
        print(f"Registros en Auditoria (Triggers ejecutados): {r_aud}")
        
        if r_inc >= 10000:
            print("\n¡EXITO! Se cumple con el requisito de mas de 10,000 registros para la investigacion.")
        else:
            print("\nADVERTENCIA: Menos de 10,000 registros insertados.")
            
except Exception as e:
    print(f"Error al verificar la base de datos: {e}")

print("\nProceso de carga finalizado.")
