# FireGuard 360

### Sistema de Persistencia Híbrida y Aprendizaje Automático para la Predicción y Simulación de Incendios Forestales en Ecuador

---

## 1. Descripción del Proyecto

**FireGuard 360** es una plataforma de investigación formativa que integra bases de datos relacionales e híbridas, aprendizaje automático y visualización interactiva para el monitoreo, estimación y simulación de incendios forestales en el territorio ecuatoriano (enfocado en las áreas de influencia de **Quito, Guayaquil, Riobamba y Cuenca**).

El sistema utiliza una arquitectura de **persistencia híbrida**:
* **SQL Server**: Almacena de forma relacional estructurada en Tercera Forma Normal (3FN) datos climáticos, de vegetación y registros históricos satelitales.
* **MongoDB**: Registra de manera no estructurada los metadatos e hiperparámetros de los experimentos y entrenamiento de modelos de Machine Learning.

---

## 2. Requisitos y Prerrequisitos

Antes de iniciar la clonación y despliegue del proyecto, asegúrate de contar con:
1. **Python 3.10 o superior** (Recomendado 3.12).
2. **SQL Server**: Una instancia local activa (el script está configurado por defecto para la instancia `LUIS`, modificable en las cadenas de conexión si es necesario).
3. **Controlador ODBC**: Tener instalado el driver oficial de SQL Server en tu sistema (ej: *ODBC Driver 17 for SQL Server*).
4. **MongoDB**: Servicio local en ejecución en el puerto por defecto (`localhost:27017`) para almacenar el historial de experimentos.

---

## 3. Instrucciones de Despliegue (Paso a Paso)

Sigue estos pasos para clonar y ejecutar el proyecto completo en tu máquina local:

### Paso 1: Clonar el Repositorio
Abre tu terminal y clona el proyecto desde GitHub:
```bash
git clone https://github.com/Ordones18/IncendiosBD-ML-Proyect.git
cd IncendiosBD-ML-Proyect
```

### Paso 2: Instalar Dependencias de Python
Instala todas las librerías necesarias ejecutando:
```bash
pip install -r requirements.txt
```

### Paso 3: Inicializar la Base de Datos en SQL Server
Abre SQL Server Management Studio (SSMS) o tu herramienta preferida y ejecuta en orden secuencial los scripts contenidos en la carpeta `sql/`:
1. **`sql/01_crear_base_datos.sql`**: Recrea la base de datos `IncendiosForestalesEC` y sus tablas relacionales.
2. **`sql/02_indices_vistas.sql`**: Genera los índices no agrupados de alto rendimiento y las vistas analíticas (`vw_DatosUnificados` es la estructura clave para el modelamiento).
3. **`sql/03_triggers_auditoria.sql`**: Genera los disparadores que auditan en formato JSON todos los inserts, updates o deletes en las tablas principales.
4. **`sql/04_roles_permisos.sql`**: Configura los roles `rol_analista` y `rol_admin` y crea usuarios de prueba.
5. **`sql/05_drp_backups.sql`**: Proporciona las estrategias de respaldo y restauración ante fallas físicas.

### Paso 4: Carga e Ingesta de Datos (ETL)
Ejecuta el script de carga para procesar las fuentes de datos físicas CSV (datos de clima NASA POWER, NDVI de MODIS y anomalías térmicas NASA FIRMS) e insertarlas en SQL Server:
```bash
python cargar_datos_sql.py
```
*(Nota: El script calcula vectorialmente mediante NumPy la ciudad más cercana de influencia para cada uno de los más de 72,000 focos de calor satelitales en Ecuador).*

### Paso 5: Entrenamiento y Pipeline de Machine Learning
Para entrenar los modelos K-Means (no supervisado) y XGBoost (supervisado) y generar el archivo binario del clasificador:
* **Desde consola**:
  ```bash
  python notebook_ml_pipeline.py
  ```
* **Desde Jupyter**: Abre y ejecuta todas las celdas de **`entrenamiento_modelos_ml.ipynb`** (lo que también generará y mostrará las curvas del Codo, Coeficiente de Silueta y Curva ROC).

Este paso sobreescribirá localmente el archivo **`modelo_incendios.pkl`** y enviará las métricas a MongoDB local.

### Paso 6: Lanzar la Aplicación Interactiva (Streamlit)
Finalmente, ejecuta el dashboard interactivo de visualización:
```bash
streamlit run app_streamlit.py
```
La aplicación se abrirá en tu navegador en **`http://localhost:8501`**.

---

## 4. Estructura de Archivos del Proyecto

* **`sql/`**: Carpeta con los scripts de bases de datos ordenados cronológicamente.
* **`image/Designer (1).png`**: Logotipo oficial del sistema FireGuard 360.
* **`graficas/`**: Directorio donde se guardan las curvas y reportes de importancia de variables del entrenamiento.
* **`app_streamlit.py`**: Código principal del panel de control interactivo (5 pestañas en modo oscuro).
* **`cargar_datos_sql.py`**: Módulo de limpieza, imputación y carga relacional a SQL Server.
* **`notebook_ml_pipeline.py` / `entrenamiento_modelos_ml.ipynb`**: Códigos del flujo analítico de Machine Learning.
* **`etl_cargar_datos.ipynb`**: Notebook explicativo del proceso de Extracción, Transformación y Carga.
* **`modelo_incendios.pkl`**: Serialización empaquetada de los pesos del modelo final entrenado.
* **`requirements.txt`**: Listado de paquetes de Python necesarios para la ejecución.
* **`experimentos_ml.json`**: Historial de métricas de desempeño guardadas en disco local.

---

## 5. Resumen de Modelos Implementados

### Aprendizaje No Supervisado (Segmentación Climática)
* **Algoritmo**: K-Means ($K=3$).
* **Propósito**: Segmenta el territorio ecuatoriano según su vulnerabilidad atmosférica actual en tres clústeres ordenados por temperatura: *Bajo Riesgo*, *Riesgo Moderado* y *Alto Riesgo*.
* **Métricas**: Coeficiente de Silueta: **0.4041** | Inercia: **50,232.26**.

### Aprendizaje Supervisado (Clasificación de Incendio)
* **Algoritmo**: XGBoost Classifier (Ganador por F1-Score frente a Random Forest).
* **Propósito**: Estima en tiempo real la probabilidad (0% a 100%) de que un foco de calor ocurra en las siguientes 24 horas bajo condiciones climáticas dadas.
* **Métricas**: Accuracy: **67.82%** | F1-Score: **0.5539** | AUC-ROC: **0.7089**.
