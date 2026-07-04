# 📘 FireGuard 360 — Sistema de Persistencia Híbrida y Aprendizaje Automático

### Predicción y Simulación de Riesgo de Incendios Forestales en Ecuador (2012–2026)

---

## 1. Descripción General del Proyecto

**FireGuard 360** es una solución analítica e infraestructural integral que unifica bases de datos relacionales y no relacionales, algoritmos de Machine Learning (supervisados y no supervisados) y visualización geográfica para la gestión de riesgos de incendios forestales en Ecuador. El sistema se enfoca en las áreas de influencia de cuatro ciudades clave: **Quito, Guayaquil, Riobamba y Cuenca**.

El proyecto implementa una arquitectura de **persistencia híbrida (políglota)**:
*   **SQL Server (Relacional - 3FN)**: Garantiza la integridad transaccional e indexación eficiente de series temporales de clima (NASA POWER), cobertura vegetal (NDVI de MODIS) y anomalías térmicas georreferenciadas (NASA FIRMS).
*   **MongoDB (No Relacional - Documental)**: Actúa como registro forense de auditoría de usuarios (LOGINS, descargas, backups) y repositorio central de MLOps para la trazabilidad de experimentos y modelos.

---

## 2. Estructura del Directorio del Proyecto

```text
Incendios_Forestales/
├── README.md                           # Única documentación técnica y guía del sistema
├── app_v2.py                           # Aplicación web interactiva en Streamlit (UI/UX Premium)
├── requirements.txt                    # Dependencias y librerías del entorno Python
├── modelo_incendios.pkl                # Modelo predictivo serializado (XGBoost + Scalers)
├── experimentos_ml.json                # Respaldo JSON de las métricas de entrenamiento
├── data/                               # Archivos CSV locales de datos históricos limpios
│   ├── ciudades.csv
│   ├── clima.csv
│   ├── ndvi.csv
│   └── incendios.csv
├── sql/                                # Scripts y DDs de base de datos relacional
│   ├── creacion_tablas.sql
│   ├── vw_DatosUnificados.sql
│   └── triggers_auditoria.sql
├── scripts/                            # Scripts de automatización en Python
│   └── cargar_datos_sql.py             # Script de carga ETL (CSV -> SQL Server)
├── notebooks/                          # Cuadernos de experimentación y EDA
│   ├── entrenamiento_modelos_ml.ipynb  # Pipeline completo de entrenamiento (XGB/K-Means)
│   └── analisis_estilo_latinometrics.ipynb # Notebook EDA con estética editorial de Latinometrics
├── graficas/                           # Gráficos de validación (curva de codo, ROC, etc.)
└── image/                              # Recursos gráficos de la interfaz (Logotipo)
```

---

## 3. Requisitos del Sistema y Dependencias

Asegúrate de contar con los siguientes prerrequisitos en tu entorno:
1.  **Python 3.10 o superior** (Recomendado 3.12).
2.  **SQL Server**: Instancia activa local o remota habilitada para autenticación de SQL Server o Trusted Connection.
3.  **Driver ODBC**: *ODBC Driver 17 for SQL Server* (necesario para la conexión PyODBC).
4.  **MongoDB**: Servicio activo en el puerto `27017` (local o Atlas).

### Instalación de dependencias
Instala las librerías necesarias ejecutando el siguiente comando en la raíz del proyecto:
```bash
pip install -r requirements.txt
```

---

## 4. Guía de Configuración y Replicabilidad (Paso a Paso)

Para clonar y desplegar el proyecto con tus propias instancias de base de datos relacional y documental, sigue estos pasos:

### Paso 1: Reemplazar Cadenas de Conexión de Base de Datos

Deberás configurar tu dirección de servidor y credenciales en tres archivos clave del proyecto:

#### 1. SQL Server Configuration
Localiza la variable `CONN_STR` o la función `check_db_connection` en los siguientes archivos y reemplaza la cadena de conexión por la tuya:
*   [scripts/cargar_datos_sql.py](file:///c:/Users/gonza/OneDrive%20-%20Universidad%20Nacional%20de%20Chimborazo/CUARTO%20SEMESTRE/Base%20de%20Datos/Investigaci%C3%B3n/Incendios_Forestales/scripts/cargar_datos_sql.py)
*   [notebooks/entrenamiento_modelos_ml.ipynb](file:///c:/Users/gonza/OneDrive%20-%20Universidad%20Nacional%20de%20Chimborazo/CUARTO%20SEMESTRE/Base%20de%20Datos/Investigaci%C3%B3n/Incendios_Forestales/notebooks/entrenamiento_modelos_ml.ipynb) (Celda 1 y 2)
*   [app_v2.py](file:///c:/Users/gonza/OneDrive%20-%20Universidad%20Nacional%20de%20Chimborazo/CUARTO%20SEMESTRE/Base%20de%20Datos/Investigaci%C3%B3n/Incendios_Forestales/app_v2.py) (Función `check_db_connection` y `verify_services`)

**Formatos de cadena de conexión a SQL Server:**
*   *Autenticación de Windows (Trusted Connection):*
    `CONN_STR = "mssql+pyodbc://<TU_SERVIDOR>/IncendiosForestalesEC?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"`
*   *Autenticación SQL Server (Usuario/Contraseña):*
    `CONN_STR = "mssql+pyodbc://<USUARIO>:<PASSWORD>@<TU_SERVIDOR>/IncendiosForestalesEC?driver=ODBC+Driver+17+for+SQL+Server"`

#### 2. MongoDB Configuration
Si tu base de datos MongoDB no corre localmente en el puerto `27017`, busca la inicialización de `MongoClient` en:
*   [app_v2.py](file:///c:/Users/gonza/OneDrive%20-%20Universidad%20Nacional%20de%20Chimborazo/CUARTO%20SEMESTRE/Base%20de%20Datos/Investigaci%C3%B3n/Incendios_Forestales/app_v2.py) (Función `log_activity` y en las pestañas de visualización)
*   [notebooks/entrenamiento_modelos_ml.ipynb](file:///c:/Users/gonza/OneDrive%20-%20Universidad%20Nacional%20de%20Chimborazo/CUARTO%20SEMESTRE/Base%20de%20Datos/Investigaci%C3%B3n/Incendios_Forestales/notebooks/entrenamiento_modelos_ml.ipynb)

**Formato de conexión a MongoDB:**
*   *Local:* `MongoClient("mongodb://localhost:27017/")`
*   *Atlas/Remoto:* `MongoClient("mongodb+srv://<USUARIO>:<PASSWORD>@<CLUSTER_URL>/?retryWrites=true&w=majority")`

---

### Paso 2: Crear el Esquema y Cargar Datos en SQL Server

1.  Abre SQL Server Management Studio (SSMS) y ejecuta el script [sql/creacion_tablas.sql](file:///c:/Users/gonza/OneDrive%20-%20Universidad%20Nacional%20de%20Chimborazo/CUARTO%20SEMESTRE/Base%20de%20Datos/Investigaci%C3%B3n/Incendios_Forestales/sql/creacion_tablas.sql) para crear la base de datos `IncendiosForestalesEC` y sus tablas en 3FN.
2.  Ejecuta el script [sql/vw_DatosUnificados.sql](file:///c:/Users/gonza/OneDrive%20-%20Universidad%20Nacional%20de%20Chimborazo/CUARTO%20SEMESTRE/Base%20de%20Datos/Investigaci%C3%B3n/Incendios_Forestales/sql/vw_DatosUnificados.sql) para generar la vista dinámica de integración temporal.
3.  Carga los datos iniciales desde los CSV locales ejecutando el script ETL:
    ```bash
    python scripts/cargar_datos_sql.py
    ```

---

### Paso 3: Entrenar el Pipeline de Machine Learning

Para generar el modelo predictivo serializado `.pkl` y registrar los experimentos en MongoDB, puedes ejecutar las celdas del cuaderno interactivo [notebooks/entrenamiento_modelos_ml.ipynb](file:///c:/Users/gonza/OneDrive%20-%20Universidad%20Nacional%20de%20Chimborazo/CUARTO%20SEMESTRE/Base%20de%20Datos/Investigaci%C3%B3n/Incendios_Forestales/notebooks/entrenamiento_modelos_ml.ipynb) o correr directamente el pipeline de Python:
```bash
python scripts/notebook_ml_pipeline.py
```
Este proceso validará el clustering K-Means ($K=3$), entrenará y comparará XGBoost frente a Random Forest bajo regularización, y guardará el archivo `modelo_incendios.pkl` optimizado.

---

### Paso 4: Desplegar la Aplicación Interactiva

Una vez cargados los datos y generado el modelo, despliega la interfaz gráfica en Streamlit:
```bash
streamlit run app_v2.py
```
La aplicación se abrirá automáticamente en tu navegador web en `http://localhost:8501`.

---

## 5. Especificaciones Técnicas del Almacenamiento y ML

### Esquema Relacional (3FN) y Unificación Temporal
Las tablas de hechos `Clima` (diario), `NDVI` (cada 16 días) e `Incendios` (eventuales) se unifican dinámicamente mediante la vista `vw_DatosUnificados` en SQL Server. Se implementa la cláusula `OUTER APPLY` con `TOP 1 ... ORDER BY fecha DESC` para recuperar la salud vegetal (NDVI) real más reciente sin generar fuga de información en los modelos supervisados.

### Ingeniería de Variables de Memoria Climática (Lag Features)
Para simular la deshidratación biológica y la acumulación estival, la aplicación y el pipeline calculan en Python variables móviles de **3 días de ventana temporal**:
*   `temp_max_promedio_3d`: Media de la temperatura máxima de los últimos 3 días.
*   `precipitacion_acumulada_3d`: Suma de precipitación de los últimos 3 días.
*   `humedad_promedio_3d`: Media de la humedad relativa de los últimos 3 días.
*   `viento_promedio_3d`: Media de la velocidad del viento de los últimos 3 días.

### Regularización e Hiperparámetros de los Modelos
Para garantizar la generalización y evitar el sobreajuste, los modelos se entrenaron bajo estrictas penalizaciones:
*   **XGBoost**: `max_depth=5`, `learning_rate=0.08`, regularización L1/L2 (`reg_alpha=0.5`, `reg_lambda=1.5`), submuestreo (`subsample=0.8`, `colsample_bytree=0.8`), y balanceo de pesos `scale_pos_weight=1.5`.
*   **Random Forest**: `max_depth=8`, `min_samples_split=5`, y balanceo interno de clases `class_weight='balanced'`.

### Métricas de Rendimiento Obtenidas (Test Set)

| Modelo Clasificador | Accuracy | Precision | Recall (Sensibilidad) | F1-Score | AUC-ROC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Random Forest (Regularizado) | 68.18% | 0.5958 | 0.6238 | 0.6095 | 0.7326 |
| **XGBoost Classifier (Optimizado)** | **69.22%** | **0.6081** | **0.6381** | **0.6227** | **0.7351** |
