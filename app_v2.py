# -*- coding: utf-8 -*-
# =========================================================================
# Proyecto de Investigación Formativa: Predicción de Incendios Forestales
# Fase 6: Aplicación Streamlit v2 — Interfaz Profesional
# Archivo: app_v2.py
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
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import datetime
import base64
import requests
import uuid
from io import StringIO
from pymongo import MongoClient

# -------------------------------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="FireGuard 360",
    page_icon="image/Designer (1).png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------------------
# PALETA DE COLORES (Tema Claro Fijo)
# -------------------------------------------------------------------------
C = {
    "bg": "#f8fafc", "surface": "#ffffff", "card": "#ffffff",
    "border": "#e2e8f0", "border_h": "rgba(234,88,12,0.2)",
    "t1": "#0f172a", "t2": "#64748b", "t3": "#94a3b8",
    "red": "#ef4444", "amber": "#f59e0b", "green": "#10b981",
    "blue": "#3b82f6", "purple": "#8b5cf6", "pink": "#db2777", "cyan": "#0891b2",
    "glow": "0 0 40px rgba(251,146,60,0.04)",
    "ptpl": "plotly_white", "pfont": "#1e293b", "pgrid": "#e2e8f0",
    "tiles": "CartoDB positron",
}

# -------------------------------------------------------------------------
# ID DE SESIÓN ÚNICO (para tracking de logs)
# -------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

# -------------------------------------------------------------------------
# FUNCIÓN DE LOGGING EN MONGODB
# -------------------------------------------------------------------------
def log_activity(action: str, details: dict = None):
    """Registra una actividad del usuario en MongoDB (colección logs_actividad)."""
    try:
        mongo_client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=1500)
        db = mongo_client['IncendiosForestales_ML']
        collection = db['logs_actividad']
        doc = {
            "timestamp": datetime.datetime.now(),
            "usuario": st.session_state.get("username", "desconocido"),
            "rol": st.session_state.get("role", "sin_rol"),
            "accion": action,
            "detalles": details or {},
            "session_id": st.session_state.get("session_id", "N/A"),
        }
        collection.insert_one(doc)
        mongo_client.close()
    except Exception:
        pass  # No interrumpir la app si MongoDB falla al loguear

# -------------------------------------------------------------------------
# COMPROBACIÓN DE SERVICIOS ACTIVOS (SIN CACHÉ — se ejecuta cada recarga)
# -------------------------------------------------------------------------
def verify_services():
    """Verifica que SQL Server y MongoDB estén activos. Retorna (ok, error_msg)."""
    errors = []
    # 1. Verificar SQL Server
    try:
        test_engine = create_engine(
            "mssql+pyodbc://LUIS/IncendiosForestalesEC?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes",
            poolclass=NullPool
        )
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        errors.append(f"SQL Server: {e}")

    # 2. Verificar MongoDB
    try:
        mc = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=1500)
        mc.admin.command('ping')
        mc.close()
    except Exception as e:
        errors.append(f"MongoDB: {e}")

    if errors:
        return False, "\n\n".join(errors)
    return True, ""

db_ok, db_err = verify_services()

if not db_ok:
    st.markdown(f"""
    <div style="max-width: 650px; margin: 100px auto 0 auto; padding: 40px; background: {C['card']}; border: 2px solid {C['red']}; border-radius: 24px; text-align: center; box-shadow: {C['glow']}; font-family: 'Inter', sans-serif;">
        <div style="font-size: 4rem; margin-bottom: 15px;">⚠️</div>
        <h2 style="color: {C['red']}; font-weight: 900; margin-bottom: 16px; letter-spacing: -0.02em;">Bases de Datos Fuera de Línea</h2>
        <p style="color: {C['t1']}; font-size: 0.92rem; line-height: 1.6; margin-bottom: 24px;">
            Para ejecutar <strong>FireGuard 360</strong>, es obligatorio iniciar los servicios locales de 
            <strong>SQL Server</strong> y <strong>MongoDB</strong> (puerto 27017).
        </p>
        <div style="background: rgba(220,38,38,0.06); padding: 18px; border-radius: 12px; text-align: left; font-family: monospace; font-size: 0.76rem; color: #991b1b; max-height: 150px; overflow-y: auto; margin-bottom: 24px; border: 1px solid {C['border']};">
            <strong>Error detectado:</strong><br>{db_err.replace(chr(10), '<br>')}
        </div>
        <p style="color: {C['t2']}; font-size: 0.8rem; font-weight: 500;">
            Inicia los motores en el Panel de Servicios de Windows y <strong>recarga esta página</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# -------------------------------------------------------------------------
# CSS — DISEÑO COMPLETO
# -------------------------------------------------------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    *, *::before, *::after {{ box-sizing: border-box; }}
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .main {{ background: {C["bg"]}; color: {C["t1"]}; }}

    .block-container {{
        padding: 1rem 2.5rem 4rem 2.5rem;
        max-width: 1380px;
    }}

    /* Ocultar sidebar y header nativo */
    section[data-testid="stSidebar"],
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {{ display: none !important; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 5px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {C["border"]}; border-radius: 10px; }}

    /* ========== HERO ========== */
    .hero {{
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 22px;
        padding: 40px 0 25px 0;
    }}
    .hero img {{
        width: 110px;
        height: 110px;
        border-radius: 26px;
        box-shadow: {C["glow"]};
        margin: 0;
    }}
    .hero-name {{
        font-size: 4.2rem;
        font-weight: 900;
        letter-spacing: -0.05em;
        background: linear-gradient(135deg, {C["red"]}, {C["amber"]});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin: 0;
    }}

    /* ========== TABS ========== */
    .stTabs [data-baseweb="tab-list"] {{
        justify-content: center;
        gap: 6px;
        background: {C["surface"]};
        border: 1px solid {C["border"]};
        border-radius: 16px;
        padding: 6px 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 12px;
        padding: 11px 24px;
        font-weight: 700;
        font-size: 0.82rem;
        color: {C["t3"]};
        background: transparent;
        border: none;
        transition: all 0.2s ease;
        white-space: nowrap;
    }}
    .stTabs [data-baseweb="tab"]:hover {{ color: {C["t1"]}; }}

    /* Colores por pestaña */
    .stTabs button:nth-child(1)[aria-selected="true"] {{
        background: rgba(239,68,68,0.08) !important;
        color: {C["red"]} !important;
    }}
    .stTabs button:nth-child(2)[aria-selected="true"] {{
        background: rgba(245,158,11,0.08) !important;
        color: {C["amber"]} !important;
    }}
    .stTabs button:nth-child(3)[aria-selected="true"] {{
        background: rgba(16,185,129,0.08) !important;
        color: {C["green"]} !important;
    }}
    .stTabs button:nth-child(4)[aria-selected="true"] {{
        background: rgba(59,130,246,0.08) !important;
        color: {C["blue"]} !important;
    }}
    .stTabs button:nth-child(5)[aria-selected="true"] {{
        background: rgba(139,92,246,0.08) !important;
        color: {C["purple"]} !important;
    }}
    .stTabs button:nth-child(6)[aria-selected="true"] {{
        background: rgba(219,39,119,0.08) !important;
        color: {C["pink"]} !important;
    }}
    .stTabs button:nth-child(7)[aria-selected="true"] {{
        background: rgba(8,145,178,0.08) !important;
        color: {C["cyan"]} !important;
    }}
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {{ display: none; }}

    /* ========== CARDS ========== */
    .kpi {{
        background: {C["card"]};
        border: 1px solid {C["border"]};
        border-radius: 14px;
        padding: 20px 22px;
        position: relative;
        overflow: hidden;
        transition: all 0.2s ease;
    }}
    .kpi:hover {{
        border-color: {C["border_h"]};
        transform: translateY(-2px);
        box-shadow: {C["glow"]};
    }}
    .kpi::after {{
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
    }}
    .kpi.k-red::after {{ background: {C["red"]}; }}
    .kpi.k-amb::after {{ background: {C["amber"]}; }}
    .kpi.k-grn::after {{ background: {C["green"]}; }}
    .kpi.k-blu::after {{ background: {C["blue"]}; }}
    .kpi.k-pnk::after {{ background: {C["pink"]}; }}
    .kpi.k-cyn::after {{ background: {C["cyan"]}; }}
    .kpi-label {{
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: {C["t3"]};
        margin-bottom: 6px;
    }}
    .kpi-val {{
        font-size: 1.75rem;
        font-weight: 800;
        color: {C["t1"]};
        line-height: 1.15;
    }}
    .kpi-unit {{
        font-size: 0.8rem;
        font-weight: 500;
        color: {C["t2"]};
    }}

    /* ========== SECCIONES ========== */
    .sec-t {{
        font-size: 1.35rem;
        font-weight: 850;
        color: {C["t1"]};
        letter-spacing: -0.02em;
        margin-bottom: 6px;
        border-left: 4px solid {C["red"]};
        padding-left: 10px;
    }}
    .sec-d {{
        font-size: 0.82rem;
        color: {C["t2"]};
        line-height: 1.55;
        margin-bottom: 18px;
    }}
    .note {{
        font-size: 0.8rem;
        color: {C["t2"]};
        line-height: 1.7;
        margin-top: 14px;
    }}
    .note strong {{ color: {C["t1"]}; }}
    strong {{
        font-size: 1.1em;
        font-weight: 800;
        color: {C["t1"]} !important;
    }}

    /* ========== RESULTADO PREDICCIÓN ========== */
    .res-card {{
        background: {C["card"]};
        border: 1px solid {C["border"]};
        border-radius: 18px;
        padding: 30px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 290px;
        transition: all 0.25s ease;
    }}
    .res-card:hover {{
        border-color: {C["border_h"]};
        box-shadow: {C["glow"]};
    }}
    .res-tag {{
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {C["t3"]};
    }}
    .res-title {{
        font-size: 0.9rem;
        font-weight: 700;
        color: {C["t1"]};
        margin: 4px 0 18px 0;
    }}
    .res-big {{
        font-size: 3.25rem;
        font-weight: 900;
        line-height: 1;
    }}
    .bar-bg {{
        background: {C["border"]};
        border-radius: 4px;
        height: 4px;
        width: 100%;
        margin-top: 16px;
    }}
    .bar-fg {{
        height: 4px;
        border-radius: 4px;
        transition: width 0.5s ease;
    }}
    .badge {{
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 6px 16px;
        border-radius: 8px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #fff;
        margin-top: 16px;
    }}
    .b-hi {{ background: linear-gradient(135deg,#dc2626,#ef4444); }}
    .b-md {{ background: linear-gradient(135deg,#d97706,#f59e0b); }}
    .b-lo {{ background: linear-gradient(135deg,#059669,#10b981); }}

    /* ========== PERFILES CLÚSTER ========== */
    .prof {{
        background: {C["card"]};
        border: 1px solid {C["border"]};
        border-radius: 14px;
        padding: 20px;
        transition: all 0.2s ease;
    }}
    .prof:hover {{ border-color: {C["border_h"]}; transform: translateY(-1px); }}
    .prof-t {{ font-size: 0.88rem; font-weight: 700; margin-bottom: 6px; }}
    .prof-d {{ font-size: 0.78rem; color: {C["t2"]}; line-height: 1.55; }}

    /* ========== INFO BOX ========== */
    .info-box {{
        background: {C["card"]};
        border: 1px solid {C["border"]};
        border-radius: 14px;
        padding: 18px 20px;
        margin-top: 12px;
    }}
    .info-box-t {{
        font-size: 0.78rem;
        font-weight: 700;
        color: {C["t1"]};
        margin-bottom: 6px;
    }}
    .info-box-d {{
        font-size: 0.75rem;
        color: {C["t2"]};
        line-height: 1.6;
    }}
    .info-box-d strong {{ color: {C["t1"]}; }}

    /* ========== BOTONES ========== */
    .stButton > button {{
        background: linear-gradient(135deg, {C["red"]}, {C["amber"]});
        color: #fff;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 10px 28px;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 6px 24px rgba(251,146,60,0.2);
    }}
    .stDownloadButton > button {{
        background: {C["card"]} !important;
        color: {C["t1"]} !important;
        border: 1px solid {C["border"]} !important;
        font-weight: 600 !important;
    }}
    .stDownloadButton > button:hover {{
        border-color: {C["border_h"]} !important;
    }}

    hr {{ border-color: {C["border"]}; opacity: 0.4; }}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# SISTEMA DE SESIÓN Y AUTENTICACIÓN
# -------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.engine = None

def load_ml_model():
    if os.path.exists('modelo_incendios.pkl'):
        return joblib.load('modelo_incendios.pkl')
    return None

model_artifacts = load_ml_model()

def check_db_connection(username, password):
    conn_str = f"mssql+pyodbc://{username}:{password}@LUIS/IncendiosForestalesEC?driver=ODBC+Driver+17+for+SQL+Server"
    try:
        temp_engine = create_engine(conn_str, poolclass=NullPool, pool_pre_ping=True)
        with temp_engine.connect() as conn:
            role_query = """
                SELECT DP1.name AS Rol
                FROM sys.database_role_members DRM
                INNER JOIN sys.database_principals DP1 ON DRM.role_principal_id = DP1.principal_id
                INNER JOIN sys.database_principals DP2 ON DRM.member_principal_id = DP2.principal_id
                WHERE DP2.name = CURRENT_USER
            """
            try:
                result = conn.execute(text(role_query)).fetchone()
                role = result[0] if result else ("rol_admin" if "admin" in username.lower() else "rol_analista")
            except Exception:
                role = "rol_admin" if "admin" in username.lower() else "rol_analista"
        return temp_engine, role, None
    except Exception as e:
        return None, "", str(e)

# -------------------------------------------------------------------------
# IMAGEN DEL LOGOTIPO
# -------------------------------------------------------------------------
try:
    with open("image/Designer (1).png", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    logo_tag = f'<img src="data:image/png;base64,{b64}" />'
except FileNotFoundError:
    logo_tag = ""

# -------------------------------------------------------------------------
# PANTALLA DE LOGUEO SI NO ESTÁ AUTENTICADO
# -------------------------------------------------------------------------
if not st.session_state.logged_in:
    # Header del Login
    st.markdown(f"""
    <div class="hero" style="padding-top: 60px;">
        {logo_tag}
        <div class="hero-name">FireGuard 360</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="max-width: 480px; margin: 20px auto 0 auto; padding: 30px; background: {C['card']}; border: 1px solid {C['border']}; border-radius: 20px; box-shadow: {C['glow']};">
        <h3 style="text-align: center; font-weight: 800; margin-bottom: 12px; color: {C['t1']};">Iniciar Sesión</h3>
        <p style="color: {C['t2']}; font-size: 0.82rem; text-align: center; margin-bottom: 25px; line-height: 1.5;">
            Ingresa tus credenciales de base de datos SQL Server para validar tus permisos y cargar tu rol asignado.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1.2, 1.6, 1.2])
    with col_m:
        with st.form("login_form"):
            user_input = st.text_input("Usuario (Login de SQL Server)", value="user_analista_test")
            pass_input = st.text_input("Contraseña", type="password", value="AnalistaPassword2026*")
            submit = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submit:
                with st.spinner("Autenticando contra SQL Server..."):
                    engine_db, role_db, err = check_db_connection(user_input, pass_input)
                    if engine_db:
                        st.session_state.logged_in = True
                        st.session_state.username = user_input
                        st.session_state.role = role_db
                        st.session_state.engine = engine_db
                        log_activity("LOGIN", {"metodo": "SQL Server Auth", "rol_detectado": role_db})
                        st.success("Acceso concedido con éxito.")
                        st.rerun()
                    else:
                        log_activity("LOGIN_FALLIDO", {"usuario_intento": user_input, "error": err})
                        st.error(f"Fallo de conexión a SQL Server: {err}")
    st.stop()

# -------------------------------------------------------------------------
# HEADER DEL DASHBOARD (LOGUEADO)
# -------------------------------------------------------------------------
role_lbl = "ADMINISTRADOR" if st.session_state.role == "rol_admin" else "ANALISTA"
tag_color = C["amber"] if st.session_state.role == "rol_admin" else C["green"]

st.markdown(f"""
<div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding: 25px 0 10px 0; gap: 8px; text-align:center;">
    {logo_tag.replace('<img', f'<img style="width: 80px; height: 80px; border-radius: 20px; box-shadow: {C["glow"]}; margin: 0 auto;"')}
    <div style="font-size: 2.8rem; font-weight: 900; background: linear-gradient(135deg, {C["red"]}, {C["amber"]}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; letter-spacing: -0.04em;">FireGuard 360</div>
    <div style="display:flex; align-items:center; justify-content:center; gap: 10px; margin-top: 4px;">
        <span class="badge" style="margin-top:0; background:{tag_color}; font-size:0.65rem; padding: 4px 10px; font-weight: 700;">{role_lbl}</span>
        <span style="color: {C['t2']}; font-size: 0.8rem;">Sesión: <strong>{st.session_state.username}</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)

# Botón de control centrado
col_sp1, col_lgt, col_sp2 = st.columns([4.5, 3, 4.5])
with col_lgt:
    if st.button("Cerrar Sesión", key="logout_btn", use_container_width=True):
        log_activity("LOGOUT")
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.engine = None
        st.rerun()

st.markdown("<hr style='margin-top:15px; margin-bottom: 25px;' />", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# DECLARACIÓN DINÁMICA DE PESTAÑAS SEGÚN EL ROL
# -------------------------------------------------------------------------
if st.session_state.role == "rol_admin":
    tab_mapa, tab_cluster, tab_pred, tab_sim, tab_api, tab_exp, tab_gov = st.tabs([
        "Mapa de Calor",
        "Clústeres de Riesgo",
        "Predicción",
        "Simulación",
        "Tiempo Real",
        "Historial de Experimentos",
        "Gobernanza y DRP"
    ])
else:
    tab_mapa, tab_cluster, tab_pred, tab_sim, tab_api = st.tabs([
        "Mapa de Calor",
        "Clústeres de Riesgo",
        "Predicción",
        "Simulación",
        "Tiempo Real"
    ])

# =====================================================================
# 1 — MAPA DE CALOR HISTÓRICO
# =====================================================================
with tab_mapa:
    st.markdown(
        f'<div class="sec-t">Focos Históricos de Incendios Forestales</div>'
        f'<div class="sec-d">Detecciones satelitales MODIS registradas por las misiones Terra y Aqua de la NASA.</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        ciudad_sel = st.selectbox("Área de influencia", ["Todas", "Quito", "Guayaquil", "Riobamba", "Cuenca"], key="m_city")
    with c2:
        conf_min = st.slider("Confianza mínima (%)", 0, 100, 50, key="m_conf")
    with c3:
        years = st.slider("Rango de años", 2012, 2026, (2012, 2026), key="m_yr")

    def load_fires(mc, sy, ey, cn, _engine):
        cw, p = "", {"mc": mc, "sd": f"{sy}-01-01", "ed": f"{ey}-12-31"}
        if cn != "Todas":
            cm = {'Quito': 1, 'Guayaquil': 2, 'Riobamba': 3, 'Cuenca': 4}
            cw = "AND id_ciudad = :cid"
            p["cid"] = cm[cn]
        q = f"""SELECT latitud, longitud, confianza, frp, fecha_deteccion, satelite
                FROM vw_HistoricoIncendios
                WHERE confianza >= :mc AND fecha_deteccion BETWEEN :sd AND :ed {cw}"""
        with _engine.connect() as conn:
            return pd.read_sql(text(q), conn, params=p)

    df_map = load_fires(conf_min, years[0], years[1], ciudad_sel, st.session_state.engine)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi k-red"><div class="kpi-label">Focos detectados</div><div class="kpi-val">{len(df_map):,}</div></div>', unsafe_allow_html=True)
    with c2:
        mf = df_map['frp'].max() if len(df_map) > 0 else 0.0
        st.markdown(f'<div class="kpi k-amb"><div class="kpi-label">Máximo FRP</div><div class="kpi-val">{mf:.1f} <span class="kpi-unit">MW</span></div></div>', unsafe_allow_html=True)
    with c3:
        ac = df_map['confianza'].mean() if len(df_map) > 0 else 0.0
        st.markdown(f'<div class="kpi k-blu"><div class="kpi-label">Confianza promedio</div><div class="kpi-val">{ac:.1f}<span class="kpi-unit">%</span></div></div>', unsafe_allow_html=True)

    if len(df_map) > 0:
        sample = df_map if len(df_map) <= 15000 else df_map.sample(15000, random_state=42)
        if len(df_map) > 15000:
            st.caption("Muestra de 15,000 puntos para optimizar el rendimiento.")
        m = folium.Map(location=[-1.5, -78.5], zoom_start=7, tiles=C["tiles"])
        HeatMap(sample[['latitud', 'longitud']].values.tolist(), radius=10, blur=15,
                gradient={0.4: 'blue', 0.65: 'orange', 0.9: 'red'}).add_to(m)
        st_folium(m, width="100%", height=520, key="hm")
    else:
        st.info("No hay datos para los filtros seleccionados.")

    st.markdown("---")
    f_desc = f" en {ciudad_sel}" if ciudad_sel != "Todas" else " a nivel nacional"
    st.markdown(f'<div class="sec-t">Análisis de patrones históricos{f_desc} ({years[0]}–{years[1]})</div>', unsafe_allow_html=True)

    def load_stats(sy, ey, cf, cn, _engine):
        cw, p = "", {"mc": cf, "sd": f"{sy}-01-01", "ed": f"{ey}-12-31"}
        if cn != "Todas":
            cm = {'Quito': 1, 'Guayaquil': 2, 'Riobamba': 3, 'Cuenca': 4}
            cw = "AND i.id_ciudad = :cid"
            p["cid"] = cm[cn]
        q1 = f"""SELECT i.ciudad_nombre AS Ciudad, COUNT(*) AS Incendios, i.ciudad_region AS Región
                 FROM vw_HistoricoIncendios i
                 WHERE i.confianza >= :mc AND i.fecha_deteccion BETWEEN :sd AND :ed {cw}
                 GROUP BY i.ciudad_nombre, i.ciudad_region ORDER BY Incendios DESC"""
        q2 = f"""SELECT MONTH(i.fecha_deteccion) AS Mes, COUNT(*) AS Incendios
                 FROM vw_HistoricoIncendios i
                 WHERE i.confianza >= :mc AND i.fecha_deteccion BETWEEN :sd AND :ed {cw}
                 GROUP BY MONTH(i.fecha_deteccion) ORDER BY Mes"""
        with _engine.connect() as conn:
            dc = pd.read_sql(text(q1), conn, params=p)
            dm = pd.read_sql(text(q2), conn, params=p)
        mn = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
              7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
        dall = pd.DataFrame(list(mn.items()), columns=['Mes','Nombre_Mes'])
        dm = pd.merge(dall, dm, on='Mes', how='left').fillna(0)
        dm['Incendios'] = dm['Incendios'].astype(int)
        return dc, dm

    try:
        dfc, dfm = load_stats(years[0], years[1], conf_min, ciudad_sel, st.session_state.engine)
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f'<div class="sec-d">Incendios por área de influencia</div>', unsafe_allow_html=True)
            if len(dfc) > 0:
                fig = px.bar(dfc, x='Ciudad', y='Incendios', color='Región',
                    color_discrete_map={'Sierra': C["amber"], 'Costa': C["red"]}, text_auto=True)
                fig.update_layout(template=C["ptpl"], paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)", font_color=C["pfont"],
                    margin=dict(l=10,r=10,t=10,b=10), height=340,
                    legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center"),
                    xaxis=dict(gridcolor=C["pgrid"]), yaxis=dict(gridcolor=C["pgrid"]))
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"""<div class="note">
                <strong>Guayaquil (Costa):</strong> Mayor volumen histórico de alertas. Las altas temperaturas
                costeras y el viento marítimo aceleran la combustión.<br>
                <strong>Quito (Sierra):</strong> Segundo foco nacional. Los vientos secos de verano y la
                topografía montañosa favorecen la propagación.
            </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown(f'<div class="sec-d">Distribución estacional</div>', unsafe_allow_html=True)
            if dfm['Incendios'].sum() > 0:
                fig2 = px.bar(dfm, x='Nombre_Mes', y='Incendios', color='Incendios',
                    color_continuous_scale='OrRd', text_auto=True)
                fig2.update_layout(template=C["ptpl"], paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)", font_color=C["pfont"],
                    coloraxis_showscale=False, margin=dict(l=10,r=10,t=10,b=10), height=340,
                    xaxis=dict(gridcolor=C["pgrid"]), yaxis=dict(gridcolor=C["pgrid"]))
                fig2.update_traces(textposition='outside')
                st.plotly_chart(fig2, use_container_width=True)
            st.markdown(f"""<div class="note">
                <strong>Noviembre:</strong> Pico máximo anual por acumulación de radiación solar y retraso
                en el inicio de las lluvias.<br>
                <strong>Sep–Dic (Estación seca):</strong> Concentra más del 65% de las quemas del país.<br>
                <strong>Mayo:</strong> Menor actividad, coincidiendo con la máxima pluviosidad estacional.
            </div>""", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")


# =====================================================================
# 2 — CLÚSTERES DE RIESGO
# =====================================================================
with tab_cluster:
    st.markdown(
        f'<div class="sec-t">Clústeres de Riesgo mediante K-Means</div>'
        f'<div class="sec-d">Agrupación territorial basada en variables climáticas y vegetación '
        f'para categorizar el nivel de riesgo ambiental.</div>',
        unsafe_allow_html=True
    )

    c_left, c_right = st.columns([3.2, 1.8])

    with c_left:
        def load_unified(_engine):
            with _engine.connect() as conn:
                df = pd.read_sql("SELECT * FROM vw_DatosUnificados", conn)
            if model_artifacts:
                Xk = model_artifacts['scaler_kmeans'].transform(df[model_artifacts['features_kmeans']])
                df['cluster'] = model_artifacts['kmeans_model'].predict(Xk)
                cm = model_artifacts['cluster_mapping']
                df['Riesgo'] = df['cluster'].map(cm).map({0:'Bajo',1:'Medio',2:'Alto'})
            else:
                df['Riesgo'] = 'N/A'
            return df

        dfu = load_unified(st.session_state.engine)
        if model_artifacts:
            s = dfu.sample(min(3000, len(dfu)), random_state=42)
            fig3 = px.scatter_3d(s, x='temperatura_media', y='humedad_relativa', z='ndvi',
                color='Riesgo',
                color_discrete_map={'Bajo': C["green"], 'Medio': C["amber"], 'Alto': C["red"]},
                labels={'temperatura_media':'Temp. Media (°C)','humedad_relativa':'Humedad (%)','ndvi':'NDVI'},
                opacity=0.7)
            fig3.update_layout(
                scene=dict(bgcolor=C["bg"],
                    xaxis=dict(gridcolor=C["pgrid"]),
                    yaxis=dict(gridcolor=C["pgrid"]),
                    zaxis=dict(gridcolor=C["pgrid"]),
                    camera=dict(eye=dict(x=1.1, y=1.1, z=1.1))),
                margin=dict(l=0,r=0,b=0,t=10), height=680,
                paper_bgcolor="rgba(0,0,0,0)", font_color=C["pfont"],
                legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Modelo K-Means no disponible.")

    with c_right:
        st.markdown(f'<div class="sec-d">Validación del algoritmo</div>', unsafe_allow_html=True)
        if os.path.exists('graficas/curva_codo.png'):
            st.image('graficas/curva_codo.png', caption='Método del Codo (K = 3)', use_container_width=True)
        else:
            st.info("Ejecuta el pipeline de ML para generar las curvas.")
        if os.path.exists('graficas/coeficiente_silueta.png'):
            st.image('graficas/coeficiente_silueta.png', caption='Coeficiente de Silueta', use_container_width=True)

    st.divider()
    st.markdown(f'<div class="sec-d">Perfiles de riesgo</div>', unsafe_allow_html=True)
    c0, c1, c2 = st.columns(3)
    with c0:
        st.markdown(f'<div class="prof"><div class="prof-t" style="color:{C["green"]}">Riesgo Bajo</div>'
            f'<div class="prof-d">Menores temperaturas, alta humedad relativa y mayor índice de vegetación (NDVI).</div></div>',
            unsafe_allow_html=True)
    with c1:
        st.markdown(f'<div class="prof"><div class="prof-t" style="color:{C["amber"]}">Riesgo Medio</div>'
            f'<div class="prof-d">Temperaturas templadas a cálidas, humedad y vegetación en niveles intermedios.</div></div>',
            unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="prof"><div class="prof-t" style="color:{C["red"]}">Riesgo Alto</div>'
            f'<div class="prof-d">Altas temperaturas, baja humedad y vientos fuertes. Máxima propensión a la propagación.</div></div>',
            unsafe_allow_html=True)


# =====================================================================
# 3 — PREDICCIÓN DE RIESGO
# =====================================================================
with tab_pred:
    st.markdown(
        f'<div class="sec-t">Predicción de Riesgo en Tiempo Real</div>'
        f'<div class="sec-d">Ingresa los datos meteorológicos para estimar la probabilidad de '
        f'un incendio forestal en las próximas 24 horas.</div>',
        unsafe_allow_html=True
    )

    if not model_artifacts:
        st.error("Modelo de ML no encontrado. Ejecuta el pipeline de entrenamiento primero.")
    else:
        coords = {
            'Quito': {'lat': -0.1807, 'lon': -78.4678, 'alt': 2850.0},
            'Guayaquil': {'lat': -2.1894, 'lon': -79.8890, 'alt': 4.0},
            'Riobamba': {'lat': -1.6731, 'lon': -78.6530, 'alt': 2754.0},
            'Cuenca': {'lat': -2.9001, 'lon': -79.0060, 'alt': 2560.0}
        }

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="sec-d">Ubicación y vegetación</div>', unsafe_allow_html=True)
            cp = st.selectbox("Ciudad", list(coords.keys()), key="pc")
            ci = coords[cp]
            lat_i = st.number_input("Latitud", value=ci['lat'], format="%.4f", key="plat")
            lon_i = st.number_input("Longitud", value=ci['lon'], format="%.4f", key="plon")
            alt_i = st.number_input("Altitud (msnm)", value=ci['alt'], key="palt")
            ndvi_i = st.slider("Índice NDVI (0 = suelo seco, 1 = vegetación densa)", 0.0, 1.0, 0.45, 0.01, key="pndvi")

        with c2:
            st.markdown(f'<div class="sec-d">Condiciones climáticas</div>', unsafe_allow_html=True)
            tm = st.slider("Temperatura media (°C)", 5.0, 40.0, 18.0, 0.5, key="ptm")
            tx = st.slider("Temperatura máxima (°C)", tm, 45.0, tm + 5, 0.5, key="ptx")
            tn = st.slider("Temperatura mínima (°C)", 0.0, tm, tm - 5, 0.5, key="ptn")
            hr = st.slider("Humedad relativa (%)", 10.0, 100.0, 60.0, 1.0, key="phr")
            pp = st.slider("Precipitación (mm/día)", 0.0, 100.0, 0.0, 0.1, key="ppp")
            vv = st.slider("Velocidad del viento (m/s)", 0.0, 15.0, 3.5, 0.1, key="pvv")
            vd = st.slider("Dirección del viento (0–360°)", 0, 360, 90, key="pvd")

        st.divider()

        if st.button("Estimar Riesgo de Incendio", use_container_width=True, key="bp"):
            now = datetime.datetime.now()
            mes = now.month
            tri = (mes - 1) // 3 + 1
            da = now.timetuple().tm_yday
            es = 1 if mes in [6, 7, 8, 9] else 0

            # K-Means
            ik = np.array([[tm, hr, vv, pp, ndvi_i]])
            sk = model_artifacts['scaler_kmeans'].transform(ik)
            cpred = model_artifacts['kmeans_model'].predict(sk)[0]
            cmap = model_artifacts['cluster_mapping'][cpred]
            rlbl = {0: "Bajo", 1: "Medio", 2: "Alto"}[cmap]

            # XGBoost
            ccod = model_artifacts['le_ciudad'].transform([cp])[0]
            
            # Obtener histórico de los últimos 2 días para calcular variables acumulativas de 3 días reales
            hist_tx, hist_pp, hist_hr, hist_vv = [tx, tx], [pp, pp], [hr, hr], [vv, vv]
            try:
                query_history = f"""
                    SELECT TOP 2 temperatura_max, precipitacion, humedad_relativa, velocidad_viento
                    FROM Clima
                    WHERE id_ciudad = (SELECT id_ciudad FROM Ciudades WHERE nombre = '{cp}')
                    ORDER BY fecha DESC
                """
                with st.session_state.engine.connect() as conn:
                    res_hist = conn.execute(text(query_history)).fetchall()
                if len(res_hist) > 0:
                    hist_tx = [float(r[0]) for r in res_hist]
                    hist_pp = [float(r[1]) for r in res_hist]
                    hist_hr = [float(r[2]) for r in res_hist]
                    hist_vv = [float(r[3]) for r in res_hist]
            except Exception:
                pass # Usar el fallback si hay error en la consulta
            
            temp_max_promedio_3d = np.mean(hist_tx + [tx])
            precipitacion_acumulada_3d = np.sum(hist_pp + [pp])
            humedad_promedio_3d = np.mean(hist_hr + [hr])
            viento_promedio_3d = np.mean(hist_vv + [vv])

            inp = pd.DataFrame([{
                'ciudad_cod': ccod, 'ciudad_latitud': lat_i, 'ciudad_longitud': lon_i,
                'altitud_msnm': alt_i, 'velocidad_viento': vv, 'direccion_viento': vd,
                'temperatura_media': tm, 'temperatura_max': tx, 'temperatura_min': tn,
                'humedad_relativa': hr, 'precipitacion': pp, 'ndvi': ndvi_i,
                'mes': mes, 'trimestre': tri, 'dia_anio': da, 'es_estacion_seca': es,
                'temp_max_promedio_3d': temp_max_promedio_3d,
                'precipitacion_acumulada_3d': precipitacion_acumulada_3d,
                'humedad_promedio_3d': humedad_promedio_3d,
                'viento_promedio_3d': viento_promedio_3d
            }])
            ss = model_artifacts['scaler_supervised'].transform(inp)
            prob = float(model_artifacts['supervised_model'].predict_proba(ss)[0][1])

            # Colores
            if prob > 0.6:
                pc_c, pc_l, pc_b = C["red"], "ALTO RIESGO DE INCENDIO", "b-hi"
            elif prob > 0.3:
                pc_c, pc_l, pc_b = C["amber"], "RIESGO MODERADO", "b-md"
            else:
                pc_c, pc_l, pc_b = C["green"], "RIESGO BAJO", "b-lo"

            if rlbl == "Alto":
                cc_c, cc_b, cc_p = C["red"], "b-hi", "Seco y cálido"
            elif rlbl == "Medio":
                cc_c, cc_b, cc_p = C["amber"], "b-md", "Templado moderado"
            else:
                cc_c, cc_b, cc_p = C["green"], "b-lo", "Húmedo y fresco"

            # Registrar predicción en MongoDB
            log_activity("PREDICCION", {
                "ciudad": cp, "latitud": lat_i, "longitud": lon_i,
                "temperatura_media": tm, "humedad_relativa": hr,
                "ndvi": ndvi_i, "velocidad_viento": vv,
                "probabilidad_incendio": round(prob, 4),
                "riesgo_xgboost": pc_l, "riesgo_kmeans": rlbl
            })

            st.markdown(f'<div class="sec-t" style="margin-top:8px;">Resultado del análisis</div>', unsafe_allow_html=True)

            r1, r2 = st.columns(2)
            with r1:
                st.markdown(f"""
                <div class="res-card">
                    <div>
                        <div class="res-tag">Modelo {model_artifacts['supervised_model_name']}</div>
                        <div class="res-title">Probabilidad de Incendio Forestal</div>
                        <div class="res-big" style="color:{pc_c};">{prob * 100:.1f}%</div>
                        <div class="bar-bg"><div class="bar-fg" style="width:{prob * 100}%;background:{pc_c};"></div></div>
                    </div>
                    <div><span class="badge {pc_b}">{pc_l}</span></div>
                </div>""", unsafe_allow_html=True)
            with r2:
                st.markdown(f"""
                <div class="res-card">
                    <div>
                        <div class="res-tag">Categorización K-Means</div>
                        <div class="res-title">Riesgo Climático Ambiental</div>
                        <div class="res-big" style="color:{cc_c};">{rlbl}</div>
                        <div style="height:4px;margin-top:16px;"></div>
                    </div>
                    <div><span class="badge {cc_b}">Perfil: {cc_p}</span></div>
                </div>""", unsafe_allow_html=True)


# =====================================================================
# 4 — SIMULACIÓN DE PROPAGACIÓN
# =====================================================================
with tab_sim:
    st.markdown(
        f'<div class="sec-t">Simulación del Cono de Propagación</div>'
        f'<div class="sec-d">Simulación geométrica y temporal del avance del frente de fuego '
        f'en base a la velocidad y dirección del viento.</div>',
        unsafe_allow_html=True
    )

    sim_coords = {
        'Quito': (-0.1807, -78.4678), 'Guayaquil': (-2.1894, -79.8890),
        'Riobamba': (-1.6731, -78.6530), 'Cuenca': (-2.9001, -79.0060)
    }

    s1, s2 = st.columns([1, 2])
    with s1:
        st.markdown(f'<div class="sec-d">Parámetros</div>', unsafe_allow_html=True)
        csim = st.selectbox("Punto de origen", list(sim_coords.keys()), key="sc")
        olat, olon = sim_coords[csim]
        flat = st.number_input("Latitud del foco", value=olat, format="%.4f", key="slat")
        flon = st.number_input("Longitud del foco", value=olon, format="%.4f", key="slon")
        vs = st.slider("Velocidad del viento (m/s)", 0.0, 25.0, 8.0, 0.5, key="svs")
        vdir = st.slider("Dirección del viento (0–360°)", 0, 360, 45, key="svd",
            help="0° = Viento del Norte. 90° = Del Este.")
        sh = st.slider("Horas de simulación", 1, 6, 3, key="sh")

        st.markdown(f"""
        <div class="info-box">
            <div class="info-box-t">Física del modelo conal</div>
            <div class="info-box-d">
                <strong>Dirección:</strong> Opuesta a la procedencia del viento.<br>
                <strong>Apertura:</strong> A mayor viento, frente más angosto y veloz.<br>
                <strong>Velocidad:</strong> Proporcional a la velocidad del viento.
            </div>
        </div>""", unsafe_allow_html=True)

    with s2:
        pd2 = (vdir + 180) % 360
        ac2 = 90 - pd2
        tr = np.radians(ac2)
        oad = max(30, 150 - 5 * vs)
        oar = np.radians(oad / 2)
        vkh = 0.15 + 0.06 * vs

        ms = folium.Map(location=[flat, flon], zoom_start=13, tiles=C["tiles"])
        folium.Marker([flat, flon], popup="Punto de Origen",
            icon=folium.Icon(color='red', icon='fire', prefix='fa')).add_to(ms)

        cols_fire = ['#fecaca', '#fca5a5', '#f87171', '#ef4444', '#dc2626', '#b91c1c']
        for h in range(sh, 0, -1):
            dk = vkh * h
            lo = dk / 111.0
            loo = dk / (111.0 * np.cos(np.radians(flat)))
            pts = [(flat, flon)]
            for a in np.linspace(tr - oar, tr + oar, 15):
                pts.append((flat + lo * np.sin(a), flon + loo * np.cos(a)))
            pts.append((flat, flon))
            folium.Polygon(locations=pts, color=C["red"], weight=2, fill=True,
                fill_color=cols_fire[min(h - 1, len(cols_fire) - 1)], fill_opacity=0.35,
                popup=f"Hora {h} | {dk:.2f} km | Apertura: {oad:.1f}°").add_to(ms)

        # Flecha de dirección del viento
        ld = 1.0
        dl = flat + (ld / 111.0) * np.sin(tr)
        dlo = flon + (ld / (111.0 * np.cos(np.radians(flat)))) * np.cos(tr)
        folium.PolyLine(locations=[(flat, flon), (dl, dlo)], color=C["amber"],
            weight=4, dash_array='5,10',
            popup=f"Viento: {vdir}° → Propagación: {pd2:.1f}°").add_to(ms)

        st_folium(ms, width="100%", height=500, key="sm")
        st.caption(f"Frente final a ~{vkh * sh:.2f} km del foco en {sh} horas.")


# =====================================================================
# 5 — MONITOREO EN TIEMPO REAL
# =====================================================================
with tab_api:
    st.markdown(
        f'<div class="sec-t">Monitoreo en Tiempo Real — NASA FIRMS</div>'
        f'<div class="sec-d">Consulta en vivo a los satélites de la NASA (MODIS / VIIRS) '
        f'para detectar anomalías térmicas activas en Ecuador.</div>',
        unsafe_allow_html=True
    )

    a1, a2, a3 = st.columns(3)
    with a1:
        fa = st.selectbox("Satélite / Sensor",
            ['VIIRS_SNPP_NRT', 'MODIS_NRT', 'VIIRS_NOAA20_NRT'],
            format_func=lambda x: {
                'VIIRS_SNPP_NRT': 'VIIRS (Suomi NPP — 375m)',
                'MODIS_NRT': 'MODIS (Terra y Aqua — 1km)',
                'VIIRS_NOAA20_NRT': 'VIIRS (NOAA-20 — 375m)'
            }[x], key="as")
    with a2:
        da2 = st.slider("Días de búsqueda", 1, 10, 3, key="ad")
    with a3:
        st.write("")
        st.write("")
        cb = st.button("Consultar NASA", use_container_width=True, key="ab")

    AREA_EC = "-81.5,-5.5,-75.0,1.5"
    API_KEY = '55c87ddc1e0092f160698f60b6ac026d'

    def fetch_firms(sensor, days):
        try:
            r = requests.get(
                f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{sensor}/{AREA_EC}/{days}",
                timeout=20)
            if r.status_code == 200:
                if "Invalid API call" in r.text:
                    return None, "Error de la API: llamada inválida."
                return pd.read_csv(StringIO(r.text)), None
            return None, f"Error del servidor NASA (código {r.status_code})"
        except requests.exceptions.Timeout:
            return None, "Tiempo de espera agotado. La NASA no respondió a tiempo."
        except Exception as e:
            return None, str(e)

    if 'df_api_data' not in st.session_state:
        st.session_state.df_api_data = None
    if 'api_error' not in st.session_state:
        st.session_state.api_error = None

    if cb:
        with st.spinner("Conectando con los servidores de la NASA..."):
            dr, er = fetch_firms(fa, da2)
        st.session_state.df_api_data = dr
        st.session_state.api_error = er
        log_activity("CONSULTA_NASA", {
            "sensor": fa, "dias": da2,
            "focos_encontrados": len(dr) if dr is not None else 0,
            "error": er
        })

    if st.session_state.df_api_data is not None:
        dfa = st.session_state.df_api_data
        if len(dfa) == 0:
            st.info("Sin focos detectados en el rango seleccionado.")
        else:
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f'<div class="kpi k-red"><div class="kpi-label">Focos activos</div><div class="kpi-val">{len(dfa)}</div></div>', unsafe_allow_html=True)
            with m2:
                mfa = dfa['frp'].max() if 'frp' in dfa.columns else 0.0
                st.markdown(f'<div class="kpi k-amb"><div class="kpi-label">Máximo FRP</div><div class="kpi-val">{mfa:.2f} <span class="kpi-unit">MW</span></div></div>', unsafe_allow_html=True)
            with m3:
                ab = dfa['brightness'].mean() if 'brightness' in dfa.columns else 0.0
                abc = ab - 273.15 if ab > 200 else ab
                st.markdown(f'<div class="kpi k-blu"><div class="kpi-label">Temp. de brillo promedio</div><div class="kpi-val">{abc:.1f} <span class="kpi-unit">°C</span></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="sec-d" style="margin-top:16px;">Distribución geográfica en tiempo real</div>', unsafe_allow_html=True)
            ma = folium.Map(location=[-1.5, -78.5], zoom_start=7, tiles=C["tiles"])
            HeatMap(dfa[['latitude', 'longitude']].values.tolist(), radius=12, blur=15,
                    gradient={0.4: 'yellow', 0.65: 'orange', 0.9: 'red'}).add_to(ma)
            for _, row in dfa.iterrows():
                fv = row.get('frp', 0.0)
                if fv > 15.0:
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']], radius=6,
                        color=C["red"], fill=True, fill_color=C["red"], fill_opacity=0.8,
                        popup=f"FRP: {fv:.1f} MW | {row.get('satellite','N/A')} | {row.get('acq_date','N/A')}"
                    ).add_to(ma)
            st_folium(ma, width="100%", height=500, key="lm")

            st.markdown(f'<div class="sec-d" style="margin-top:16px;">Detalle de datos descargados</div>', unsafe_allow_html=True)
            dc2 = [c for c in ['latitude','longitude','brightness','frp','acq_date','acq_time','confidence','satellite'] if c in dfa.columns]
            st.dataframe(
                dfa[dc2].sort_values(by='frp', ascending=False) if 'frp' in dfa.columns else dfa,
                use_container_width=True)

            e1, e2 = st.columns(2)
            with e1:
                csv_data = dfa.to_csv(index=False).encode('utf-8')
                if st.download_button("Exportar CSV", csv_data,
                    f"incendios_activos_{fa}.csv", "text/csv", use_container_width=True):
                    log_activity("DESCARGA_CSV", {"sensor": fa, "registros": len(dfa)})
            with e2:
                json_data = dfa.to_json(orient='records', indent=4).encode('utf-8')
                if st.download_button("Exportar JSON", json_data,
                    f"incendios_activos_{fa}.json", "application/json", use_container_width=True):
                    log_activity("DESCARGA_JSON", {"sensor": fa, "registros": len(dfa)})

    elif st.session_state.api_error is not None:
        st.error(st.session_state.api_error)
    else:
        st.info("Presiona el botón para consultar los servidores de la NASA.")


# =====================================================================
# 6 — HISTORIAL DE EXPERIMENTOS (MONGODB - STRICT)
# =====================================================================
if st.session_state.role == "rol_admin":
    with tab_exp:
        st.markdown(
            f'<div class="sec-t">Historial de Experimentos y MLOps</div>'
            f'<div class="sec-d">Persistencia documental en MongoDB para el registro y auditoría del entrenamiento de los modelos.</div>',
            unsafe_allow_html=True
        )
        
        mongo_success = False
        experiments_data = []
        
        try:
            client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
            client.admin.command('ping')
            db = client['IncendiosForestales_ML']
            collection = db['experimentos']
            
            docs = list(collection.find({"proyecto": "Incendios Forestales Ecuador 2012-2026"}).sort("fecha", -1))
            if len(docs) > 0:
                for doc in docs:
                    doc['_id'] = str(doc['_id'])
                    if isinstance(doc['fecha'], datetime.datetime):
                        doc['fecha'] = doc['fecha'].strftime("%Y-%m-%d %H:%M:%S")
                    experiments_data.append(doc)
                mongo_success = True
                st.success("Conectado con éxito a base de datos documental MongoDB (Localhost:27017)")
        except Exception as e:
            st.error(f"Fallo de conexión a base de datos MongoDB: {e}. Por favor inicie el servicio para cargar los experimentos.")
                
        if mongo_success and len(experiments_data) > 0:
            col_ex1, col_ex2, col_ex3 = st.columns(3)
            with col_ex1:
                st.markdown(f'<div class="kpi k-pnk"><div class="kpi-label">Experimentos registrados</div><div class="kpi-val">{len(experiments_data)}</div></div>', unsafe_allow_html=True)
            with col_ex2:
                max_f1 = max([exp['metricas']['f1_score'] for exp in experiments_data]) if len(experiments_data) > 0 else 0.0
                st.markdown(f'<div class="kpi k-amb"><div class="kpi-label">Mejor F1-Score</div><div class="kpi-val">{max_f1:.4f}</div></div>', unsafe_allow_html=True)
            with col_ex3:
                max_auc = max([exp['metricas']['auc_roc'] for exp in experiments_data]) if len(experiments_data) > 0 else 0.0
                st.markdown(f'<div class="kpi k-blu"><div class="kpi-label">Mejor AUC-ROC</div><div class="kpi-val">{max_auc:.4f}</div></div>', unsafe_allow_html=True)
                
            
            st.markdown('<div class="sec-d" style="font-weight:700; margin-top:20px; color:'+C["red"]+';">Modelos Activos (Último Entrenamiento)</div>', unsafe_allow_html=True)
            
            # Mostrar los 2 experimentos más recientes (el último entrenamiento realizado)
            active_experiments = experiments_data[:2]
            for exp in active_experiments:
                is_selected = exp.get('seleccionado', False)
                border_style = f"border-color: {C['amber']}; box-shadow: {C['glow']};" if is_selected else ""
                selected_tag = f'<span class="badge b-md">EN PRODUCCIÓN</span>' if is_selected else f'<span class="badge b-lo">CANDIDATO</span>'
                params_str = ", ".join([f"{k}: {v}" for k, v in exp.get('parametros', {}).items()])
                
                st.markdown(f"""
                <div class="fg-card" style="{border_style} margin-bottom: 20px; padding: 25px; background: {C['card']}; border: 1px solid {C['border']}; border-radius: 18px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div style="font-size:1.15rem; font-weight:800; color:{C["t1"]};">{exp.get('algoritmo')} (Librería: {exp.get('libreria')})</div>
                        {selected_tag}
                    </div>
                    <div class="sec-d" style="margin-bottom:12px;">Fecha del experimento: <strong>{exp.get('fecha')}</strong></div>
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin-bottom:15px;">
                        <div class="prof">
                            <div class="prof-t" style="color:{C["t2"]}; font-size:0.72rem; text-transform:uppercase;">Accuracy</div>
                            <div style="font-size:1.25rem; font-weight:800; color:{C["t1"]};">{exp['metricas']['accuracy']:.4f}</div>
                        </div>
                        <div class="prof">
                            <div class="prof-t" style="color:{C["t2"]}; font-size:0.72rem; text-transform:uppercase;">Precision</div>
                            <div style="font-size:1.25rem; font-weight:800; color:{C["t1"]};">{exp['metricas']['precision']:.4f}</div>
                        </div>
                        <div class="prof">
                            <div class="prof-t" style="color:{C["t2"]}; font-size:0.72rem; text-transform:uppercase;">Recall</div>
                            <div style="font-size:1.25rem; font-weight:800; color:{C["t1"]};">{exp['metricas']['recall']:.4f}</div>
                        </div>
                        <div class="prof">
                            <div class="prof-t" style="color:{C["t2"]}; font-size:0.72rem; text-transform:uppercase;">F1-Score</div>
                            <div style="font-size:1.25rem; font-weight:800; color:{C["t1"]};">{exp['metricas']['f1_score']:.4f}</div>
                        </div>
                    </div>
                    <div class="info-box" style="margin-top:0;">
                        <div class="info-box-t">Parámetros & Configuración</div>
                        <div class="info-box-d">
                            <strong>Hiperparámetros:</strong> {params_str}<br>
                            <strong>Variables de entrada:</strong> {", ".join(exp.get('variables_entrada', []))}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            # Mostrar los experimentos antiguos en una tabla compacta
            older_experiments = experiments_data[2:]
            if len(older_experiments) > 0:
                st.markdown('<div class="sec-d" style="font-weight:700; margin-top:30px; color:'+C["t1"]+';">Historial de Entrenamientos Anteriores (Logs Históricos)</div>', unsafe_allow_html=True)
                
                hist_table = []
                for exp in older_experiments:
                    hist_table.append({
                        "Fecha": exp.get("fecha"),
                        "Algoritmo": exp.get("algoritmo"),
                        "Accuracy": round(exp['metricas']['accuracy'], 4),
                        "Precision": round(exp['metricas']['precision'], 4),
                        "Recall": round(exp['metricas']['recall'], 4),
                        "F1-Score": round(exp['metricas']['f1_score'], 4),
                        "AUC-ROC": round(exp['metricas']['auc_roc'], 4),
                        "Parámetros": str(exp.get('parametros', {}))
                    })
                df_hist = pd.DataFrame(hist_table)
                st.dataframe(df_hist, use_container_width=True)
        elif mongo_success:
            st.warning("No hay registros de experimentos disponibles en MongoDB.")


# =====================================================================
# 7 — GOBERNANZA Y DRP (ADMIN EXCLUSIVE)
# =====================================================================
if st.session_state.role == "rol_admin":
    with tab_gov:
        st.markdown(
            f'<div class="sec-t">Gobernanza de Datos y Plan de Recuperación ante Desastres (DRP)</div>'
            f'<div class="sec-d">Monitoreo de auditoría en tiempo real, ejecución de copias de seguridad y registro de actividad del sistema.</div>',
            unsafe_allow_html=True
        )
        
        col_gov1, col_gov2 = st.columns([6, 4])
        
        with col_gov1:
            st.markdown(f'<div class="sec-d" style="font-weight:700;">Registro de Auditoría Reciente (Triggers SQL Server)</div>', unsafe_allow_html=True)
            try:
                query_audit = "SELECT TOP 30 id_auditoria, tabla_afectada, operacion, fecha_hora, usuario FROM Auditoria ORDER BY fecha_hora DESC"
                with st.session_state.engine.connect() as conn:
                    df_audit = pd.read_sql(text(query_audit), conn)
                if len(df_audit) > 0:
                    st.dataframe(df_audit, use_container_width=True)
                else:
                    st.info("No hay registros de auditoría en la tabla.")
            except Exception as e:
                st.error(f"Error al leer la tabla de auditoría: {e}")
                
        with col_gov2:
            st.markdown(f'<div class="sec-d" style="font-weight:700;">Respaldos y Recuperación (DRP)</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="info-box" style="margin-top:0; margin-bottom:15px;">
                <div class="info-box-t">Modelo de Recuperación Full</div>
                <div class="info-box-d">
                    La base de datos está configurada en <strong>RECOVERY FULL</strong>, lo que permite respaldar el registro de transacciones para restaurar a un punto específico en el tiempo.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Ejecutar Backup Completo (Full)", use_container_width=True):
                with st.spinner("Ejecutando copia de seguridad COMPLETA..."):
                    try:
                        backup_query = """
                            BACKUP DATABASE IncendiosForestalesEC
                            TO DISK = 'C:\\Users\\Public\\IncendiosForestalesEC_Full.bak'
                            WITH FORMAT, INIT, NAME = 'Backup Completo desde Streamlit', STATS = 10;
                        """
                        raw_conn = st.session_state.engine.raw_connection()
                        try:
                            raw_conn.driver_connection.autocommit = True
                            cursor = raw_conn.driver_connection.cursor()
                            cursor.execute(backup_query)
                            while cursor.nextset():
                                pass
                        finally:
                            raw_conn.close()
                        log_activity("BACKUP", {"tipo": "FULL", "resultado": "EXITOSO", "ruta": "C:\\Users\\Public\\IncendiosForestalesEC_Full.bak"})
                        st.success("¡Copia de seguridad COMPLETA ejecutada con éxito!")
                    except Exception as e:
                        log_activity("BACKUP", {"tipo": "FULL", "resultado": "ERROR", "error": str(e)})
                        st.error(f"Error al ejecutar backup: {e}")
                        
            if st.button("Ejecutar Backup Diferencial", use_container_width=True):
                with st.spinner("Ejecutando copia de seguridad DIFERENCIAL..."):
                    try:
                        backup_query = """
                            BACKUP DATABASE IncendiosForestalesEC
                            TO DISK = 'C:\\Users\\Public\\IncendiosForestalesEC_Diff.bak'
                            WITH DIFFERENTIAL, FORMAT, INIT, NAME = 'Backup Diferencial desde Streamlit', STATS = 10;
                        """
                        raw_conn = st.session_state.engine.raw_connection()
                        try:
                            raw_conn.driver_connection.autocommit = True
                            cursor = raw_conn.driver_connection.cursor()
                            cursor.execute(backup_query)
                            while cursor.nextset():
                                pass
                        finally:
                            raw_conn.close()
                        log_activity("BACKUP", {"tipo": "DIFERENCIAL", "resultado": "EXITOSO", "ruta": "C:\\Users\\Public\\IncendiosForestalesEC_Diff.bak"})
                        st.success("¡Copia de seguridad DIFERENCIAL ejecutada con éxito!")
                    except Exception as e:
                        log_activity("BACKUP", {"tipo": "DIFERENCIAL", "resultado": "ERROR", "error": str(e)})
                        st.error(f"Error al ejecutar backup diferencial: {e}")
                        
            if st.button("Ejecutar Backup de Log de Transacciones", use_container_width=True):
                with st.spinner("Ejecutando copia de seguridad de LOG..."):
                    try:
                        backup_query = """
                            BACKUP LOG IncendiosForestalesEC
                            TO DISK = 'C:\\Users\\Public\\IncendiosForestalesEC_Log.bak'
                            WITH FORMAT, INIT, NAME = 'Backup del Log desde Streamlit', STATS = 10;
                        """
                        raw_conn = st.session_state.engine.raw_connection()
                        try:
                            raw_conn.driver_connection.autocommit = True
                            cursor = raw_conn.driver_connection.cursor()
                            cursor.execute(backup_query)
                            while cursor.nextset():
                                pass
                        finally:
                            raw_conn.close()
                        log_activity("BACKUP", {"tipo": "LOG_TRANSACCIONES", "resultado": "EXITOSO", "ruta": "C:\\Users\\Public\\IncendiosForestalesEC_Log.bak"})
                        st.success("¡Copia de seguridad de LOG ejecutada con éxito!")
                    except Exception as e:
                        log_activity("BACKUP", {"tipo": "LOG_TRANSACCIONES", "resultado": "ERROR", "error": str(e)})
                        st.error(f"Error al ejecutar backup de log: {e}")

            st.markdown(f"""
            <div class="info-box">
                <div class="info-box-t">Secuencia de Restauración (Simulación de Fallo)</div>
                <div class="info-box-d">
                    Para recuperar la base de datos en SQL Server Management Studio (SSMS):<br><br>
                    <strong>1. Restaurar Full (NORECOVERY)</strong><br>
                    <code>RESTORE DATABASE IncendiosForestalesEC FROM DISK = 'C:\\Users\\Public\\IncendiosForestalesEC_Full.bak' WITH NORECOVERY, REPLACE;</code><br><br>
                    <strong>2. Restaurar Log (RECOVERY)</strong><br>
                    <code>RESTORE DATABASE IncendiosForestalesEC FROM DISK = 'C:\\Users\\Public\\IncendiosForestalesEC_Log.bak' WITH RECOVERY;</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # --- SECCIÓN DE LOGS DE ACTIVIDAD (MongoDB) ---
        st.markdown("---")
        st.markdown(
            f'<div class="sec-t">Registro de Actividad del Sistema (MongoDB)</div>'
            f'<div class="sec-d">Auditoría documental en MongoDB de todas las acciones realizadas por los usuarios en la plataforma: inicios de sesión, predicciones, descargas y backups.</div>',
            unsafe_allow_html=True
        )

        try:
            mc_logs = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=1500)
            db_logs = mc_logs['IncendiosForestales_ML']
            col_logs = db_logs['logs_actividad']
            
            total_logs = col_logs.count_documents({})
            recent_logs = list(col_logs.find().sort("timestamp", -1).limit(50))
            
            if total_logs > 0:
                # KPIs de actividad
                logins_count = col_logs.count_documents({"accion": "LOGIN"})
                pred_count = col_logs.count_documents({"accion": "PREDICCION"})
                backup_count = col_logs.count_documents({"accion": "BACKUP"})
                
                kl1, kl2, kl3, kl4 = st.columns(4)
                with kl1:
                    st.markdown(f'<div class="kpi k-blu"><div class="kpi-label">Total registros</div><div class="kpi-val">{total_logs}</div></div>', unsafe_allow_html=True)
                with kl2:
                    st.markdown(f'<div class="kpi k-grn"><div class="kpi-label">Inicios de sesión</div><div class="kpi-val">{logins_count}</div></div>', unsafe_allow_html=True)
                with kl3:
                    st.markdown(f'<div class="kpi k-amb"><div class="kpi-label">Predicciones</div><div class="kpi-val">{pred_count}</div></div>', unsafe_allow_html=True)
                with kl4:
                    st.markdown(f'<div class="kpi k-pnk"><div class="kpi-label">Backups ejecutados</div><div class="kpi-val">{backup_count}</div></div>', unsafe_allow_html=True)
                
                # Tabla de logs recientes
                logs_table = []
                for log in recent_logs:
                    ts = log.get("timestamp", "")
                    if isinstance(ts, datetime.datetime):
                        ts = ts.strftime("%Y-%m-%d %H:%M:%S")
                    logs_table.append({
                        "Fecha/Hora": ts,
                        "Usuario": log.get("usuario", ""),
                        "Rol": log.get("rol", ""),
                        "Acción": log.get("accion", ""),
                        "Detalles": str(log.get("detalles", {}))[:120],
                        "Sesión": log.get("session_id", ""),
                    })
                
                df_logs = pd.DataFrame(logs_table)
                st.dataframe(df_logs, use_container_width=True, height=350)
            else:
                st.info("Aún no hay registros de actividad. Las acciones se registrarán automáticamente al usar la plataforma.")
                
            mc_logs.close()
        except Exception as e:
            st.error(f"Error al consultar logs de actividad en MongoDB: {e}")

