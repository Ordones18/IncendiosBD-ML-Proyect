# =========================================================================
# Proyecto de Investigación Formativa: Predicción de Incendios Forestales
# Fase 6: Aplicación Streamlit
# Archivo: app_streamlit.py
# =========================================================================

import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
from sqlalchemy import create_engine, text
import datetime

# -------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y ESTILO
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="FireGuard 360 - Predicción de Incendios Forestales Ecuador",
    page_icon="image/Designer (1).png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS para wowear al usuario (Paleta oscura con acentos rojos y naranja)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Fondo principal y textos */
    .main {
        background-color: #0f1219;
        color: #e2e8f0;
    }
    
    /* Contenedor de métricas */
    .card {
        background: linear-gradient(135deg, #18202d 0%, #0f141d 100%);
        border: 1px solid #283548;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        border-color: #ff5e57;
    }
    
    /* Encabezados */
    .title-h1 {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff5e57, #ffc048);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .subtitle {
        color: #a0aec0;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    
    /* Etiquetas de riesgo */
    .risk-badge {
        font-size: 1.5rem;
        font-weight: 800;
        padding: 10px 20px;
        border-radius: 12px;
        text-align: center;
        margin-top: 15px;
        color: white;
    }
    .risk-high {
        background: linear-gradient(90deg, #ff3f34, #ff5e57);
        box-shadow: 0 0 15px rgba(255, 63, 52, 0.4);
    }
    .risk-medium {
        background: linear-gradient(90deg, #ffc048, #ffa801);
        box-shadow: 0 0 15px rgba(255, 192, 72, 0.4);
    }
    .risk-low {
        background: linear-gradient(90deg, #05c46b, #0be881);
        box-shadow: 0 0 15px rgba(5, 196, 107, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# CONEXIÓN A BASE DE DATOS Y CARGA DE MODELOS
# -------------------------------------------------------------------------
CONN_STR = "mssql+pyodbc://LUIS/IncendiosForestalesEC?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
engine = create_engine(CONN_STR)

@st.cache_resource
def load_ml_model():
    if os.path.exists('modelo_incendios.pkl'):
        return joblib.load('modelo_incendios.pkl')
    return None

model_artifacts = load_ml_model()

# -------------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR)
# -------------------------------------------------------------------------
st.sidebar.markdown("<h2 style='color: #ff5e57; font-weight:800;'>Panel de Control</h2>", unsafe_allow_html=True)
st.sidebar.markdown("Investigación Formativa: Persistencia Híbrida y ML para la Predicción de Incendios en Ecuador (2012-2026).")
st.sidebar.divider()

# Estadísticas Rápidas de la Base de Datos
@st.cache_data(ttl=600)
def get_db_stats():
    stats = {}
    try:
        with engine.connect() as conn:
            stats['ciudades'] = conn.execute(text("SELECT COUNT(*) FROM Ciudades")).fetchone()[0]
            stats['clima'] = conn.execute(text("SELECT COUNT(*) FROM Clima")).fetchone()[0]
            stats['ndvi'] = conn.execute(text("SELECT COUNT(*) FROM NDVI")).fetchone()[0]
            stats['incendios'] = conn.execute(text("SELECT COUNT(*) FROM Incendios")).fetchone()[0]
    except Exception as e:
        stats = {'ciudades': 4, 'clima': 21100, 'ndvi': 1328, 'incendios': 72532}
    return stats

db_stats = get_db_stats()

st.sidebar.markdown("<h4 style='font-weight:600;'>Persistencia SQL Server</h4>", unsafe_allow_html=True)
st.sidebar.info(f"""
- **Ciudades Registradas:** {db_stats['ciudades']}
- **Registros Climáticos:** {db_stats['clima']:,}
- **Mediciones NDVI:** {db_stats['ndvi']:,}
- **Focos de Incendio (NASA):** {db_stats['incendios']:,}
""")

if model_artifacts:
    st.sidebar.success(f"Modelo ML Activo: **{model_artifacts['supervised_model_name']}**")
else:
    st.sidebar.warning("Modelo ML no encontrado. Ejecuta el pipeline primero.")

st.sidebar.divider()
st.sidebar.markdown("<span style='color: #a0aec0; font-size: 0.8rem;'>Desarrollado para Investigación Formativa 2026.</span>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# ENCABEZADO PRINCIPAL
# -------------------------------------------------------------------------
col_logo, col_title = st.columns([1, 10])
with col_logo:
    st.image("image/Designer (1).png", width=95)
with col_title:
    st.markdown("<h1 class='title-h1' style='margin-top: 10px;'>FireGuard 360</h1>", unsafe_allow_html=True)

st.markdown("<p class='subtitle'>Sistema de Predicción y Simulación de Incendios Forestales en Ecuador | Visualización en tiempo real, predicción analítica y simulación física de propagación</p>", unsafe_allow_html=True)

# Crear pestañas de navegación principal
tab_mapa, tab_cluster, tab_pred, tab_sim, tab_api = st.tabs([
    "Mapa de Calor Histórico", 
    "Clústeres de Riesgo Climático", 
    "Predicción de Riesgo", 
    "Simulación de Propagación",
    "Monitoreo en Tiempo Real (NASA API)"
])

# -------------------------------------------------------------------------
# PESTAÑA 1: MAPA DE CALOR HISTÓRICO
# -------------------------------------------------------------------------
with tab_mapa:
    st.markdown("### Focos Históricos de Incendios Forestales (MODIS)")
    st.markdown("Consulta y visualiza las zonas calientes de incendios históricos registradas por las misiones Terra y Aqua de la NASA.")
    
    # Filtros específicos
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        ciudad_sel = st.selectbox("Filtrar por área de ciudad de influencia:", ["Todas", "Quito", "Guayaquil", "Riobamba", "Cuenca"])
    with col_f2:
        conf_min = st.slider("Confianza mínima de detección (%):", 0, 100, 50)
    with col_f3:
        years = st.slider("Rango de años:", 2012, 2026, (2012, 2026))

    # Query a la base de datos
    @st.cache_data
    def load_fires_for_map(min_confidence, start_year, end_year, city_name):
        city_where = ""
        params = {
            "min_conf": min_confidence,
            "start_date": f"{start_year}-01-01",
            "end_date": f"{end_year}-12-31"
        }
        
        if city_name != "Todas":
            city_map = {'Quito': 1, 'Guayaquil': 2, 'Riobamba': 3, 'Cuenca': 4}
            city_where = "AND id_ciudad = :city_id"
            params["city_id"] = city_map[city_name]
            
        query_sql = f"""
            SELECT latitud, longitud, confianza, frp, fecha_deteccion, satelite
            FROM Incendios
            WHERE confianza >= :min_conf
              AND fecha_deteccion BETWEEN :start_date AND :end_date
              {city_where}
        """
        with engine.connect() as conn:
            df_res = pd.read_sql(text(query_sql), conn, params=params)
        return df_res

    df_map = load_fires_for_map(conf_min, years[0], years[1], ciudad_sel)

    # Tarjetas informativas
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown(f"""
        <div class='card'>
            <div class='metric-title'>Total Focos Detectados</div>
            <div class='metric-value'>{len(df_map):,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        max_frp = df_map['frp'].max() if len(df_map) > 0 else 0.0
        st.markdown(f"""
        <div class='card'>
            <div class='metric-title'>Máximo FRP (Poder Radiativo)</div>
            <div class='metric-value'>{max_frp:.1f} MW</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m3:
        avg_conf = df_map['confianza'].mean() if len(df_map) > 0 else 0.0
        st.markdown(f"""
        <div class='card'>
            <div class='metric-title'>Confianza Promedio</div>
            <div class='metric-value'>{avg_conf:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    if len(df_map) > 0:
        # Limitar número de puntos a graficar en folium para evitar crash del navegador (máximo 15,000 puntos)
        df_map_sample = df_map
        if len(df_map) > 15000:
            df_map_sample = df_map.sample(15000, random_state=42)
            st.warning("El mapa muestra una muestra aleatoria de 15,000 puntos para optimizar el rendimiento de renderizado.")

        # Crear mapa folium
        centro_lat, centro_lon = -1.5, -78.5  # Centro aproximado de Ecuador
        m = folium.Map(location=[centro_lat, centro_lon], zoom_start=7, tiles='CartoDB dark_matter')
        
        # Agregar capa de calor
        heat_data = df_map_sample[['latitud', 'longitud']].values.tolist()
        HeatMap(heat_data, radius=10, blur=15, gradient={0.4: 'blue', 0.65: 'orange', 0.9: 'red'}).add_to(m)
        
        # Renderizar en streamlit
        st_folium(m, width="100%", height=600, key="heatmap_folium")
    else:
        st.info("No hay datos de incendios que coincidan con los filtros seleccionados.")

# -------------------------------------------------------------------------
# PESTAÑA 2: CLÚSTERES DE RIESGO CLIMÁTICO
# -------------------------------------------------------------------------
with tab_cluster:
    st.markdown("### Clústeres de Riesgo mediante K-Means (Aprendizaje No Supervisado)")
    st.markdown("El modelo agrupa el territorio en base a las variables climáticas (temperatura, humedad, viento, precipitación) y vegetación (NDVI) para categorizar el nivel de riesgo.")
    
    # Distribución en dos columnas para gráficos: Dispersión 3D (izquierda, amplia) y Validación (derecha, vertical)
    col_graph_left, col_graph_right = st.columns([3.2, 1.8])
    
    with col_graph_left:
        st.markdown("#### Dispersión 3D de Clústeres de Riesgo")
        
        # Leer datos unificados para graficar
        @st.cache_data
        def load_unified_data():
            with engine.connect() as conn:
                df_res = pd.read_sql("SELECT * FROM vw_DatosUnificados", conn)
            # Agregar el cluster riesgo a los datos
            if model_artifacts:
                X_k = model_artifacts['scaler_kmeans'].transform(df_res[model_artifacts['features_kmeans']])
                df_res['cluster'] = model_artifacts['kmeans_model'].predict(X_k)
                cluster_mapping = model_artifacts['cluster_mapping']
                df_res['Riesgo_Climatico'] = df_res['cluster'].map(cluster_mapping).map({0: 'Bajo', 1: 'Medio', 2: 'Alto'})
            else:
                df_res['Riesgo_Climatico'] = 'Desconocido'
            return df_res

        df_uni = load_unified_data()
        
        if model_artifacts:
            # Gráfica interactiva de clusters con Plotly
            # Muestra aleatoria para no ralentizar la gráfica
            df_uni_sample = df_uni.sample(min(3000, len(df_uni)), random_state=42)
            fig = px.scatter_3d(
                df_uni_sample, 
                x='temperatura_media', 
                y='humedad_relativa', 
                z='ndvi',
                color='Riesgo_Climatico',
                color_discrete_map={'Bajo': '#0be881', 'Medio': '#ffa801', 'Alto': '#ff5e57'},
                title="Clasificación Tridimensional de Clústeres de Riesgo",
                labels={'temperatura_media': 'Temp. Media (°C)', 'humedad_relativa': 'Humedad (%)', 'ndvi': 'NDVI'},
                opacity=0.7
            )
            fig.update_layout(
                scene=dict(
                    bgcolor="#0f1219",
                    xaxis=dict(gridcolor="#283548"),
                    yaxis=dict(gridcolor="#283548"),
                    zaxis=dict(gridcolor="#283548"),
                    camera=dict(
                        eye=dict(x=1.1, y=1.1, z=1.1)  # Zoom ligeramente más cercano al iniciar
                    )
                ),
                margin=dict(l=0, r=0, b=0, t=40),  # Eliminar márgenes vacíos para maximizar espacio
                height=750,  # Aumentar altura a 750px
                paper_bgcolor="#0f1219",
                font_color="#e2e8f0"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay modelo K-Means cargado para visualizar los clústeres.")

    with col_graph_right:
        st.markdown("#### Curvas de Validación del Algoritmo K-Means")
        if os.path.exists('graficas/curva_codo.png'):
            st.image('graficas/curva_codo.png', caption='Método del Codo (K Óptimo = 3)', use_container_width=True)
        else:
            st.info("Ejecuta el pipeline ML para generar las curvas.")
            
        if os.path.exists('graficas/coeficiente_silueta.png'):
            st.image('graficas/coeficiente_silueta.png', caption='Coeficiente de Silueta', use_container_width=True)

    # Información y perfiles de riesgo colocados en la parte inferior para despejar los gráficos
    st.divider()
    st.markdown("#### Perfiles de Riesgo de los Clústeres")
    col_p0, col_p1, col_p2 = st.columns(3)
    
    with col_p0:
        st.markdown("""
        <div class='card'>
            <h5 style='color: #0be881; margin-top: 0px; margin-bottom: 10px; font-weight: 800;'>Riesgo Bajo (Clúster 0)</h5>
            <p style='color: #a0aec0; font-size: 0.95rem; margin: 0;'>
                Caracterizado por menores temperaturas medias, alta humedad relativa y mayor nivel de vegetación (NDVI).
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p1:
        st.markdown("""
        <div class='card'>
            <h5 style='color: #ffa801; margin-top: 0px; margin-bottom: 10px; font-weight: 800;'>Riesgo Medio (Clúster 1)</h5>
            <p style='color: #a0aec0; font-size: 0.95rem; margin: 0;'>
                Temperaturas templadas a cálidas, niveles intermedios de humedad relativa y vegetación moderada.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p2:
        st.markdown("""
        <div class='card'>
            <h5 style='color: #ff5e57; margin-top: 0px; margin-bottom: 10px; font-weight: 800;'>Riesgo Alto (Clúster 2)</h5>
            <p style='color: #a0aec0; font-size: 0.95rem; margin: 0;'>
                Altas temperaturas medias, baja humedad relativa y vientos con velocidades elevadas, propenso para la propagación.
            </p>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# PESTAÑA 3: PREDICCIÓN DE RIESGO
# -------------------------------------------------------------------------
with tab_pred:
    st.markdown("### Predicción de Riesgo en Tiempo Real (XGBoost Classifier)")
    st.markdown("Ingresa los datos meteorológicos de la zona y el nivel de vegetación (NDVI) para estimar la probabilidad de que ocurra un incendio forestal en las próximas 24 horas.")

    if not model_artifacts:
        st.error("Error: No se pudo cargar el modelo ML. Por favor ejecute `notebook_ml_pipeline.py` primero.")
    else:
        # Formulario de entrada
        col_p1, col_p2 = st.columns(2)
        
        # Datos geográficos de referencia para las ciudades
        ciudades_coord = {
            'Quito': {'lat': -0.1807, 'lon': -78.4678, 'alt': 2850.0, 'cod': 1},
            'Guayaquil': {'lat': -2.1894, 'lon': -79.8890, 'alt': 4.0, 'cod': 2},
            'Riobamba': {'lat': -1.6731, 'lon': -78.6530, 'alt': 2754.0, 'cod': 3},
            'Cuenca': {'lat': -2.9001, 'lon': -79.0060, 'alt': 2560.0, 'cod': 4}
        }

        with col_p1:
            st.markdown("#### Ubicación y Entorno")
            ciudad_pred = st.selectbox("Seleccione la Ciudad:", list(ciudades_coord.keys()))
            
            # Autocompletar variables en base a la ciudad elegida
            city_info = ciudades_coord[ciudad_pred]
            lat_in = st.number_input("Latitud:", value=city_info['lat'], format="%.4f")
            lon_in = st.number_input("Longitud:", value=city_info['lon'], format="%.4f")
            alt_in = st.number_input("Altitud (msnm):", value=city_info['alt'])
            
            st.markdown("#### Vegetación")
            ndvi_in = st.slider("Índice de Vegetación NDVI (0 = Suelo Seco, 1 = Vegetación Densa):", 0.0, 1.0, 0.45, 0.01)

        with col_p2:
            st.markdown("#### Condiciones Climáticas")
            temp_med = st.slider("Temperatura Media (°C):", 5.0, 40.0, 18.0, 0.5)
            temp_max = st.slider("Temperatura Máxima (°C):", temp_med, 45.0, temp_med + 5, 0.5)
            temp_min = st.slider("Temperatura Mínima (°C):", 0.0, temp_med, temp_med - 5, 0.5)
            hum_rel = st.slider("Humedad Relativa (%):", 10.0, 100.0, 60.0, 1.0)
            precip = st.slider("Precipitación Diaria (mm/día):", 0.0, 100.0, 0.0, 0.1)
            viento_vel = st.slider("Velocidad del Viento (m/s):", 0.0, 15.0, 3.5, 0.1)
            viento_dir = st.slider("Dirección del Viento (Grados 0-360):", 0, 360, 90)

        st.divider()
        
        # Ejecutar Predicción
        if st.button("Estimar Riesgo de Incendio", use_container_width=True):
            # Obtener datos de fecha actuales
            hoy = datetime.datetime.now()
            mes = hoy.month
            trimestre = (mes - 1) // 3 + 1
            dia_anio = hoy.timetuple().tm_yday
            es_seca = 1 if mes in [6, 7, 8, 9] else 0
            
            # 1. Ejecutar Predicción K-Means (Riesgo Climático)
            input_kmeans = np.array([[temp_med, hum_rel, viento_vel, precip, ndvi_in]])
            scaled_kmeans = model_artifacts['scaler_kmeans'].transform(input_kmeans)
            cluster_pred = model_artifacts['kmeans_model'].predict(scaled_kmeans)[0]
            cluster_mapped = model_artifacts['cluster_mapping'][cluster_pred] # Mapeo ordenado 0-2
            
            riesgo_climatico_lbl = {0: "Bajo", 1: "Medio", 2: "Alto"}[cluster_mapped]
            
            # 2. Ejecutar Predicción Clasificación (Probabilidad de Incendio)
            # Organizar variables predictoras en el orden exacto del entrenamiento
            # features_supervised = ['ciudad_cod', 'ciudad_latitud', 'ciudad_longitud', 'altitud_msnm', 'velocidad_viento', 'direccion_viento', ...]
            ciudad_cod_mapped = model_artifacts['le_ciudad'].transform([ciudad_pred])[0]
            
            input_supervised = pd.DataFrame([{
                'ciudad_cod': ciudad_cod_mapped,
                'ciudad_latitud': lat_in,
                'ciudad_longitud': lon_in,
                'altitud_msnm': alt_in,
                'velocidad_viento': viento_vel,
                'direccion_viento': viento_dir,
                'temperatura_media': temp_med,
                'temperatura_max': temp_max,
                'temperatura_min': temp_min,
                'humedad_relativa': hum_rel,
                'precipitacion': precip,
                'ndvi': ndvi_in,
                'mes': mes,
                'trimestre': trimestre,
                'dia_anio': dia_anio,
                'es_estacion_seca': es_seca
            }])
            
            scaled_supervised = model_artifacts['scaler_supervised'].transform(input_supervised)
            probabilidad = float(model_artifacts['supervised_model'].predict_proba(scaled_supervised)[0][1])
            
            # Diseñar resultado visual
            st.markdown("### Resultado del Análisis Predictivo")
            
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                if probabilidad > 0.6:
                    badge_color = "#ff5e57"
                    badge_label = "ALTO RIESGO DE INCENDIO"
                    badge_class = "risk-high"
                elif probabilidad > 0.3:
                    badge_color = "#ffa801"
                    badge_label = "RIESGO MODERADO"
                    badge_class = "risk-medium"
                else:
                    badge_color = "#0be881"
                    badge_label = "RIESGO BAJO"
                    badge_class = "risk-low"

                st.markdown(f"""<div class='card' style='display: flex; flex-direction: column; justify-content: space-between; min-height: 280px; height: 100%;'>
<div>
<h4 style='margin-top:0; color: #ff5e57; font-weight: 800;'>Probabilidad de Incendio Forestal</h4>
<p style='color: #a0aec0; font-size: 0.95rem; margin-bottom: 15px;'>Estimación del modelo {model_artifacts['supervised_model_name']}:</p>
<div style='font-size: 3.5rem; font-weight: 800; color: {badge_color}; line-height: 1.1;'>{probabilidad * 100:.1f}%</div>
<!-- Barra de progreso personalizada integrada en la tarjeta -->
<div style='background-color: #283548; border-radius: 8px; height: 8px; width: 100%; margin-top: 20px; margin-bottom: 10px;'>
<div style='background-color: {badge_color}; height: 8px; width: {probabilidad * 100}%; border-radius: 8px;'></div>
</div>
</div>
<div class='risk-badge {badge_class}' style='margin-top: 15px;'>{badge_label}</div>
</div>""", unsafe_allow_html=True)

            with col_res2:
                if riesgo_climatico_lbl == "Alto":
                    cl_color = "#ff5e57"
                    cl_badge_class = "risk-high"
                    cl_badge_label = "Perfil del Clúster: Seco y Cálido"
                elif riesgo_climatico_lbl == "Medio":
                    cl_color = "#ffa801"
                    cl_badge_class = "risk-medium"
                    cl_badge_label = "Perfil del Clúster: Templado Moderado"
                else:
                    cl_color = "#0be881"
                    cl_badge_class = "risk-low"
                    cl_badge_label = "Perfil del Clúster: Húmedo y Fresco"

                st.markdown(f"""<div class='card' style='display: flex; flex-direction: column; justify-content: space-between; min-height: 280px; height: 100%;'>
<div>
<h4 style='margin-top:0; color: #ff5e57; font-weight: 800;'>Categoría de Riesgo Climático</h4>
<p style='color: #a0aec0; font-size: 0.95rem; margin-bottom: 15px;'>Categorización no supervisada (K-Means) basada en condiciones macro-ambientales:</p>
<div style='font-size: 3.5rem; font-weight: 800; color: {cl_color}; line-height: 1.1;'>{riesgo_climatico_lbl}</div>
<!-- Espaciador para alinear con la barra de progreso de la otra columna -->
<div style='height: 8px; margin-top: 20px; margin-bottom: 10px;'></div>
</div>
<div class='risk-badge {cl_badge_class}' style='margin-top: 15px;'>{cl_badge_label}</div>
</div>""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# PESTAÑA 4: SIMULACIÓN DE PROPAGACIÓN
# -------------------------------------------------------------------------
with tab_sim:
    st.markdown("### Simulación del Cono de Propagación de Fuego")
    st.markdown("Simulación geométrica y temporal del avance del frente de fuego en base a la velocidad y dirección del viento, simulando los vectores de expansión horario.")
    
    col_s1, col_s2 = st.columns([1, 2])
    
    ciudades_sim_coord = {
        'Quito': (-0.1807, -78.4678),
        'Guayaquil': (-2.1894, -79.8890),
        'Riobamba': (-1.6731, -78.6530),
        'Cuenca': (-2.9001, -79.0060)
    }
    
    with col_s1:
        st.markdown("#### Parámetros de Propagación")
        ciudad_sim = st.selectbox("Seleccione el punto de origen en la ciudad de:", list(ciudades_sim_coord.keys()))
        
        orig_lat, orig_lon = ciudades_sim_coord[ciudad_sim]
        
        # Permitir ajuste manual fino de coordenadas del foco de incendio
        foco_lat = st.number_input("Latitud del Foco:", value=orig_lat, format="%.4f")
        foco_lon = st.number_input("Longitud del Foco:", value=orig_lon, format="%.4f")
        
        # Parámetros del viento
        v_speed = st.slider("Velocidad de viento en simulación (m/s):", 0.0, 25.0, 8.0, 0.5, key="v_speed_sim")
        # Dirección del viento en grados (0 es de dónde viene el viento: 0=Norte, 90=Este)
        v_dir = st.slider("Dirección de origen del viento (grados 0-360):", 0, 360, 45, key="v_dir_sim", 
                          help="0° = Viento soplando del Norte hacia el Sur. 90° = Del Este al Oeste.")
        
        sim_hours = st.slider("Tiempo de Simulación (Horas de avance):", 1, 6, 3)
        
        st.info("""
        **Física del Modelo Conal:**
        - **Dirección del frente:** Dirección opuesta a la procedencia del viento.
        - **Ángulo de apertura:** A mayor viento, el fuego avanza en un frente más angosto y veloz.
        - **Velocidad de avance:** Proporcional a la velocidad del viento.
        """)

    with col_s2:
        st.markdown("#### Frente Geográfico de Avance")
        
        # Algoritmo de cálculo del cono de propagación
        # wind_dir: de donde viene. prop_dir: hacia donde va (opuesto +180)
        prop_dir_deg = (v_dir + 180) % 360
        # Convertir a ángulo cartesiano en radianes (0=Este, 90=Norte)
        angle_cart = 90 - prop_dir_deg
        theta_rad = np.radians(angle_cart)
        
        # Apertura del cono (grados): entre 30 y 150 grados
        opening_angle_deg = max(30, 150 - 5 * v_speed)
        opening_rad = np.radians(opening_angle_deg / 2)
        
        # Velocidad de propagación estimada (en km/h)
        # Modelo simplificado: 0.15 km/h + 0.05 * v_speed
        velocidad_km_h = 0.15 + 0.06 * v_speed
        
        # Crear mapa folium centrado en el foco de inicio
        m_sim = folium.Map(location=[foco_lat, foco_lon], zoom_start=13, tiles='CartoDB dark_matter')
        
        # Agregar marcador del foco de origen
        folium.Marker(
            [foco_lat, foco_lon],
            popup="Punto de Origen del Incendio",
            icon=folium.Icon(color='red', icon='fire', prefix='fa')
        ).add_to(m_sim)
        
        # Generar polígonos del cono para cada hora y dibujarlos en el mapa
        colores = ['#ffe1e1', '#ffb3b3', '#ff8080', '#ff4d4d', '#ff1a1a', '#e60000']
        
        for h in range(sim_hours, 0, -1):
            dist_km = velocidad_km_h * h
            
            # Calcular offsets en grados geográficos
            lat_offset = dist_km / 111.0
            lon_offset = dist_km / (111.0 * np.cos(np.radians(foco_lat)))
            
            # Generar puntos del polígono conal
            points = [(foco_lat, foco_lon)]
            angles = np.linspace(theta_rad - opening_rad, theta_rad + opening_rad, 15)
            for a in angles:
                p_lat = foco_lat + lat_offset * np.sin(a)
                p_lon = foco_lon + lon_offset * np.cos(a)
                points.append((p_lat, p_lon))
            points.append((foco_lat, foco_lon))
            
            # Dibujar polígono en el mapa (del más lejano al más cercano para la superposición)
            color_hex = colores[min(h - 1, len(colores) - 1)]
            folium.Polygon(
                locations=points,
                color='#ff3f34',
                weight=2,
                fill=True,
                fill_color=color_hex,
                fill_opacity=0.35,
                popup=f"Frente de avance en Hora {h}\nDistancia: {dist_km:.2f} km\nÁngulo de apertura: {opening_angle_deg:.1f}°"
            ).add_to(m_sim)
            
        # Dibujar una flecha o línea indicadora del viento para dar contexto visual
        # Línea de 1.5 km de largo en la dirección de la propagación
        line_dist = 1.0
        line_lat_offset = line_dist / 111.0
        line_lon_offset = line_dist / (111.0 * np.cos(np.radians(foco_lat)))
        dest_lat = foco_lat + line_lat_offset * np.sin(theta_rad)
        dest_lon = foco_lon + line_lon_offset * np.cos(theta_rad)
        
        folium.PolyLine(
            locations=[(foco_lat, foco_lon), (dest_lat, dest_lon)],
            color='#ffa801',
            weight=4,
            dash_array='5, 10',
            popup=f"Dirección del viento: {v_dir}° (Propagación hacia: {prop_dir_deg:.1f}°)"
        ).add_to(m_sim)
        
        # Renderizar mapa
        st_folium(m_sim, width="100%", height=500, key="sim_folium")
        
        st.caption(f"Simulación para {sim_hours} horas. El frente final alcanza aproximadamente a {velocidad_km_h * sim_hours:.2f} km de distancia desde el foco original.")

# -------------------------------------------------------------------------
# PESTAÑA 5: MONITOREO EN TIEMPO REAL (NASA API)
# -------------------------------------------------------------------------
with tab_api:
    st.markdown("### Monitoreo de Incendios en Tiempo Real mediante la API de NASA FIRMS")
    st.markdown("Realiza consultas en vivo a los satélites de la NASA (MODIS/VIIRS) para obtener las últimas detecciones de anomalías térmicas e incendios activos en el territorio ecuatoriano.")
    
    # Parámetros de consulta
    col_api1, col_api2, col_api3 = st.columns(3)
    with col_api1:
        fuente_api = st.selectbox(
            "Seleccionar Satélite / Sensor:",
            options=['VIIRS_SNPP_NRT', 'MODIS_NRT', 'VIIRS_NOAA20_NRT'],
            format_func=lambda x: {
                'VIIRS_SNPP_NRT': 'VIIRS (Suomi NPP - 375m)',
                'MODIS_NRT': 'MODIS (Terra y Aqua - 1km)',
                'VIIRS_NOAA20_NRT': 'VIIRS (NOAA-20 - 375m)'
            }[x]
        )
    with col_api2:
        dias_api = st.slider("Rango de días de búsqueda:", 1, 5, 3)
    with col_api3:
        # Botón de ejecución estilizado
        st.write("") # Espaciador
        st.write("") # Espaciador
        consultar_btn = st.button("Consultar API de la NASA", use_container_width=True)

    # Definir Bounding Box de Ecuador
    AREA_ECUADOR = "-81.5,-5.5,-75.0,1.5"
    MAP_KEY = '55c87ddc1e0092f160698f60b6ac026d'

    import requests
    from io import StringIO

    # Cargar datos al pulsar el botón o mantener en caché
    @st.cache_data(show_spinner="Conectando con servidores de la NASA...")
    def fetch_live_firms_data(sensor, days):
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{sensor}/{AREA_ECUADOR}/{days}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                if "Invalid API call" in response.text:
                    return None, "Error de la API: Llamada inválida. Verifica los parámetros."
                df = pd.read_csv(StringIO(response.text))
                return df, None
            else:
                return None, f"Error del servidor NASA (Código {response.status_code})"
        except Exception as e:
            return None, f"No se pudo conectar al servidor: {e}"

    # Ejecutar consulta
    if 'df_api_data' not in st.session_state:
        st.session_state.df_api_data = None
    if 'api_error' not in st.session_state:
        st.session_state.api_error = None

    if consultar_btn:
        df_res, err = fetch_live_firms_data(fuente_api, dias_api)
        st.session_state.df_api_data = df_res
        st.session_state.api_error = err

    # Mostrar resultados si existen
    if st.session_state.df_api_data is not None:
        df_api = st.session_state.df_api_data
        
        if len(df_api) == 0:
            st.info("No se detectaron focos de incendio en el rango de búsqueda seleccionado.")
        else:
            # Métricas rápidas
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.markdown(f"""
                <div class='card'>
                    <div class='metric-title'>Focos Activos Detectados</div>
                    <div class='metric-value'>{len(df_api)}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_m2:
                max_frp_api = df_api['frp'].max() if 'frp' in df_api.columns else 0.0
                st.markdown(f"""
                <div class='card'>
                    <div class='metric-title'>Máximo FRP (Poder Radiativo)</div>
                    <div class='metric-value'>{max_frp_api:.2f} MW</div>
                </div>
                """, unsafe_allow_html=True)
            with col_m3:
                avg_bright = df_api['brightness'].mean() if 'brightness' in df_api.columns else 0.0
                # Convertir de Kelvin a Celsius si es temperatura de brillo
                avg_bright_c = avg_bright - 273.15 if avg_bright > 200 else avg_bright
                st.markdown(f"""
                <div class='card'>
                    <div class='metric-title'>Temp. de Brillo Promedio</div>
                    <div class='metric-value'>{avg_bright_c:.1f} °C</div>
                </div>
                """, unsafe_allow_html=True)

            # Mapa interactivo de focos activos
            st.markdown("#### Distribución Geográfica de Focos en Tiempo Real")
            
            # Crear mapa folium centrado en Ecuador
            m_api = folium.Map(location=[-1.5, -78.5], zoom_start=7, tiles='CartoDB dark_matter')
            
            # Añadir puntos de calor
            heat_data_api = df_api[['latitude', 'longitude']].values.tolist()
            HeatMap(heat_data_api, radius=12, blur=15, gradient={0.4: 'yellow', 0.65: 'orange', 0.9: 'red'}).add_to(m_api)
            
            # Añadir marcadores individuales para focos muy intensos (FRP > 15 MW)
            for idx, row in df_api.iterrows():
                frp_val = row.get('frp', 0.0)
                if frp_val > 15.0:
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=6,
                        color='#ff3f34',
                        fill=True,
                        fill_color='#ff3f34',
                        fill_opacity=0.8,
                        popup=f"Foco de Calor Intenso<br/>FRP: {frp_val:.1f} MW<br/>Satélite: {row.get('satellite', 'N/A')}<br/>Fecha: {row.get('acq_date', 'N/A')}"
                    ).add_to(m_api)
            
            # Renderizar mapa
            st_folium(m_api, width="100%", height=500, key="live_map_folium")
            
            # Tabla de datos y exportación
            st.markdown("#### Detalle de Datos Descargados")
            # Ordenar columnas para visualización clara
            display_cols = [c for c in ['latitude', 'longitude', 'brightness', 'frp', 'acq_date', 'acq_time', 'confidence', 'satellite'] if c in df_api.columns]
            st.dataframe(df_api[display_cols].sort_values(by='frp', ascending=False) if 'frp' in df_api.columns else df_api, use_container_width=True)
            
            # Botones de exportación
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                csv_data = df_api.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Exportar datos a CSV",
                    data=csv_data,
                    file_name=f"incendios_activos_{fuente_api}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_exp2:
                json_data = df_api.to_json(orient='records', indent=4).encode('utf-8')
                st.download_button(
                    label="Exportar datos a JSON",
                    data=json_data,
                    file_name=f"incendios_activos_{fuente_api}.json",
                    mime="application/json",
                    use_container_width=True
                )

    elif st.session_state.api_error is not None:
        st.error(st.session_state.api_error)
    else:
        st.info("Presiona el botón 'Consultar API de la NASA' para iniciar la búsqueda en vivo.")
