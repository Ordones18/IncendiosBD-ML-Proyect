# 📘 Documentación Técnica y Guía de Replicabilidad — FireGuard 360

Este documento contiene la especificación de la arquitectura, estructura de datos, flujo de ejecución y línea de tiempo del proyecto **FireGuard 360** (Sistema de Persistencia Híbrida y Aprendizaje Automático para la Predicción y Simulación de Incendios Forestales en Ecuador, 2012–2026). Está diseñado para permitir la replicabilidad completa del sistema en nuevos entornos y documentar el ciclo de desarrollo del proyecto.

---

## 1. Ficha Técnica del Sistema

*   **Nombre del Proyecto:** FireGuard 360
*   **Alcance Espacial:** Zonas de influencia de Quito, Guayaquil, Riobamba y Cuenca (Ecuador).
*   **Alcance Temporal:** Registros diarios desde el 01/01/2012 al 31/12/2026.
*   **Paradigma de Persistencia:** Persistencia Híbrida / Políglota.
    *   *Relacional (Estructurado):* SQL Server (DBMS transaccional en 3FN).
    *   *Documental (Semiestructurado):* MongoDB (DBMS para auditoría y registro de experimentos MLOps).
*   **Modelo Predictivo:** XGBoost Classifier (Clasificación supervisada) y K-Means (Clasificación no supervisada de riesgo).
*   **Interfaz Gráfica:** Streamlit (Dashboard web interactivo en modo oscuro con simulación de propagación de fuego).

---

## 2. Arquitectura de Datos y Flujo del Sistema

El siguiente diagrama representa cómo fluyen los datos en la infraestructura del proyecto:

```mermaid
flowchart TD
    subgraph Fuentes de Datos (NASA)
        NASA_POWER[NASA POWER - Clima Diario]
        MODIS_NDVI[MODIS NDVI - Follaje 16 días]
        FIRMS_FRES[NASA FIRMS - Anomalías Térmicas]
    end

    subgraph ETL (Python / Jupyter)
        ETL_Script[cargar_datos_sql.py]
        Clean_Nulos[Imputación ffill/bfill]
        Euclid_Dist[Asociación Espacial NumPy]
    end

    subgraph Almacenamiento Relacional (SQL Server)
        SQL_DB[(IncendiosForestalesEC)]
        Dim_Cities[Dim_Ciudades]
        Fact_Clima[Hecho_Clima]
        Fact_NDVI[Hecho_NDVI]
        Fact_Fire[Hecho_Incendios]
        Unified_View{vw_DatosUnificados - OUTER APPLY}
    end

    subgraph Machine Learning Pipeline
        ML_Pipeline[notebook_ml_pipeline.py]
        Model_PKL[modelo_incendios.pkl]
        Mongo_DB[(MongoDB - Experimentos)]
    end

    subgraph Interfaz (Streamlit Dashboard)
        St_App[app_streamlit.py]
    end

    %% Flujos
    NASA_POWER --> ETL_Script
    MODIS_NDVI --> ETL_Script
    FIRMS_FRES --> ETL_Script
    
    ETL_Script --> Clean_Nulos
    ETL_Script --> Euclid_Dist
    
    Clean_Nulos --> Dim_Cities
    Clean_Nulos --> Fact_Clima
    Clean_Nulos --> Fact_NDVI
    Euclid_Dist --> Fact_Fire
    
    Dim_Cities & Fact_Clima & Fact_NDVI & Fact_Fire --> Unified_View
    
    Unified_View --> ML_Pipeline
    ML_Pipeline --> Model_PKL
    ML_Pipeline -->|Registrar Experimento| Mongo_DB
    
    Model_PKL --> St_App
    SQL_DB -->|Consultas Analíticas| St_App
    Mongo_DB -->|Consultar MLOps Log| St_App
```

---

## 3. Especificaciones del Almacenamiento

### A. Esquema Relacional en SQL Server (3FN)
La base de datos relacional `IncendiosForestalesEC` está normalizada en Tercera Forma Normal para garantizar la integridad referencial espacial y meteorológica:

1.  **`Ciudades` (Dimensión):** `id_ciudad` (PK), `nombre`, `region`, `latitud`, `longitud`, `altitud_msnm`.
2.  **`Clima` (Hecho Diario):** `id_clima` (PK), `id_ciudad` (FK), `fecha`, `temperatura_media`, `temperatura_max`, `temperatura_min`, `humedad_relativa`, `precipitacion`, `velocidad_viento`, `direccion_viento`.
3.  **`NDVI` (Hecho Satelital):** `id_ndvi` (PK), `id_ciudad` (FK), `fecha`, `ndvi`, `evi`, `vi_quality`, `pixel_reliability`, `modis_tile`.
4.  **`Incendios` (Hecho Georreferenciado):** `id_incendio` (PK), `id_ciudad` (FK), `latitud`, `longitud`, `brightness`, `scan`, `track`, `fecha_deteccion`, `hora_deteccion`, `satelite`, `instrumento`, `confianza`, `version`, `bright_t31`, `frp`, `dia_noche`, `tipo`.
5.  **`Auditoria` (Historial):** `id_auditoria` (PK), `tabla_afectada`, `operacion`, `usuario`, `fecha_evento`, `detalle_json`.

#### Vista Clave de Integración: `vw_DatosUnificados`
Dado que el clima es diario, el NDVI es cada 16 días y los incendios son eventuales, la unificación temporal se realiza dinámicamente mediante la siguiente lógica en SQL Server, evitando inyectar datos ficticios en el entrenamiento de Machine Learning:
```sql
CREATE VIEW vw_DatosUnificados AS
SELECT 
    c.id_ciudad,
    c.nombre AS ciudad_nombre,
    c.latitud AS ciudad_latitud,
    c.longitud AS ciudad_longitud,
    c.altitud_msnm,
    cl.fecha,
    cl.temperatura_media,
    cl.temperatura_max,
    cl.temperatura_min,
    cl.humedad_relativa,
    cl.precipitacion,
    cl.velocidad_viento,
    cl.direccion_viento,
    n.ndvi,
    ISNULL(inc.conteo_incendios, 0) AS conteo_incendios,
    ISNULL(inc.max_frp, 0.0) AS max_frp,
    CASE WHEN ISNULL(inc.conteo_incendios, 0) > 0 THEN 1 ELSE 0 END AS incendio_binario
FROM Ciudades c
INNER JOIN Clima cl ON c.id_ciudad = cl.id_ciudad
OUTER APPLY (
    SELECT TOP 1 nd.ndvi
    FROM NDVI nd
    WHERE nd.id_ciudad = c.id_ciudad AND nd.fecha <= cl.fecha
    ORDER BY nd.fecha DESC
) n
OUTER APPLY (
    SELECT 
        COUNT(*) AS conteo_incendios,
        MAX(i.frp) AS max_frp
    FROM Incendios i
    WHERE i.id_ciudad = c.id_ciudad AND i.fecha_deteccion = cl.fecha
    GROUP BY i.id_ciudad, i.fecha_deteccion
) inc;
```

### B. Esquema Documental en MongoDB (MLOps Registry)
Para rastrear cada iteración del entrenamiento, el script de Python inserta documentos BSON en la base de datos `FireGuardExperiments` y colección `runs`:
```json
{
  "_id": "ObjectId",
  "proyecto": "Incendios Forestales Ecuador 2012-2026",
  "fecha": "ISO-Date",
  "algoritmo": "XGBoost",
  "libreria": "xgboost",
  "parametros": {
    "n_estimators": 100,
    "random_state": 42,
    "eval_metric": "logloss"
  },
  "metricas": {
    "accuracy": 0.6782,
    "precision": 0.6180,
    "recall": 0.5018,
    "f1_score": 0.5539,
    "auc_roc": 0.7089
  },
  "variables_entrada": [
    "ciudad_cod", "altitud_msnm", "velocidad_viento", "temperatura_max", "humedad_relativa", "ndvi", "es_estacion_seca", "dia_anio"
  ],
  "seleccionado": true
}
```

---

## 4. Guía Paso a Paso para Réplica Completa del Proyecto

Para desplegar y replicar este proyecto desde cero en una máquina local o servidor, ejecute los siguientes pasos en orden estricto:

### Paso 1: Configurar el Entorno del Sistema
1.  Instale **Python 3.10 o posterior** (verificado en Python 3.12).
2.  Instale **SQL Server** (Edición Express, Developer o Enterprise) y asegúrese de que la autenticación de Windows o SQL esté activa.
3.  Instale el **ODBC Driver 17 para SQL Server** en el sistema operativo.
4.  Instale e inicie **MongoDB Community Server** localmente en su puerto por defecto (`localhost:27017`).

### Paso 2: Crear el Entorno Virtual e Instalar Librerías
Abra su terminal en la raíz del proyecto y ejecute:
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 3: Inicializar Base de Datos Relacional en SQL Server
Abra SQL Server Management Studio (SSMS) o Azure Data Studio, conéctese a su servidor y ejecute en orden secuencial los scripts SQL de la carpeta `/sql`:
1.  `01_crear_base_datos.sql` (Crea la base de datos `IncendiosForestalesEC` y sus tablas relacionales y de auditoría).
2.  `02_indices_vistas.sql` (Crea la vista `vw_DatosUnificados` con `OUTER APPLY` e índices no agrupados).
3.  `03_triggers_auditoria.sql` (Genera los triggers que capturan cambios e insertan auditorías en formato JSON).
4.  `04_roles_permisos.sql` (Crea el rol de analista con accesos restringidos de lectura y el rol administrador).
5.  `05_drp_backups.sql` (Genera el procedimiento para realizar respaldos Full/Diferencial y simular recuperaciones).

### Paso 4: Ejecutar el Proceso ETL e Ingesta de Datos
Asegúrese de tener los archivos crudos en la raíz del proyecto: `clima_diario_4ciudades.csv`, `NDVI-Ecuador-Cities-MOD13Q1-061-results.csv`, y `fire_archive_M-C61_761089.csv`. Luego ejecute:
```bash
python cargar_datos_sql.py
```
Este script:
- Imputará nulos meteorológicos (`-999`).
- Asociará espacialmente más de 72,000 anomalías térmicas a sus respectivas ciudades mediante cálculo vectorial NumPy.
- Insertará todos los registros en las tablas de SQL Server con cargas en bloques (*chunks*).

### Paso 5: Ejecutar el Pipeline de Machine Learning
Para entrenar los modelos, registrar los experimentos en MongoDB y generar el archivo binario del clasificador final, ejecute:
```bash
python notebook_ml_pipeline.py
```
Este proceso escribirá el archivo **`modelo_incendios.pkl`** en la raíz (serialización del XGBoost y escaladores) y creará las gráficas de evaluación en la carpeta `/graficas`. Además, se comunicará con MongoDB para insertar los registros de métricas de Random Forest y XGBoost.

### Paso 6: Lanzar el Dashboard Interactivo
Para iniciar la interfaz interactiva para el usuario final:
```bash
streamlit run app_streamlit.py
```
La aplicación web se abrirá automáticamente en la dirección [http://localhost:8501](http://localhost:8501).

---

## 5. Línea de Tiempo del Proyecto (Fases de Desarrollo)

La siguiente cronología describe la progresión de las fases de desarrollo ejecutadas durante el proyecto:

```
[2026-06-01] ─── Fase 1: Extracción y Limpieza de Fuentes Satelitales (NASA)
                    • Descarga y consolidación meteorológica NASA POWER.
                    • Descarga de mapas raster MODIS NDVI (16 días).
                    • Obtención del histórico de puntos calientes FIRMS.
                    
[2026-06-05] ─── Fase 2: Preprocesamiento y ETL en Python
                    • Diseño del tratamiento de nulos mediante ffill y bfill por ciudad.
                    • Programación de cálculo de distancia euclidiana en NumPy para los focos calientes.
                    • Ingeniería de variables: ciudad_cod, mes, es_estacion_seca, incendio_binario.
                    
[2026-06-10] ─── Fase 3: Infraestructura Transaccional y Gobernanza (SQL Server)
                    • Creación del modelo relacional en Tercera Forma Normal (3FN).
                    • Diseño e implementación de vw_DatosUnificados con OUTER APPLY.
                    • Creación de triggers de auditoría con salida a logs JSON.
                    • Definición del Disaster Recovery Plan (DRP) mediante backups SQL.
                    
[2026-06-12] ─── Fase 4: Persistencia Híbrida e Integración NoSQL (MongoDB)
                    • Conexión de Python a MongoDB mediante PyMongo.
                    • Creación de esquema documental para el registro de métricas e hiperparámetros.
                    
[2026-06-15] ─── Fase 5: Modelado de Machine Learning (MLOps)
                    • Clasificación K-Means (K=3) validada por Coeficiente de Silueta y Codo.
                    • Comparación de modelos supervisados (Random Forest vs XGBoost).
                    • Generación de modelo_incendios.pkl con curva ROC y feature importance.
                    
[2026-06-25] ─── Fase 6: Despliegue de Interfaz Web Interactiva (Streamlit)
                    • Construcción de mapa de calor dinámico con Folium.
                    • Programación del simulador del cono de propagación de fuego basado en vientos locales.
                    • Interfaz predictiva acoplada a SQL Server y MongoDB.
```
