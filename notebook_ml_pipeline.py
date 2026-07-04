# =========================================================================
# Proyecto de Investigación Formativa: Predicción de Incendios Forestales
# Fase 4: Pipeline de Machine Learning
# Archivo: notebook_ml_pipeline.py
# =========================================================================

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import joblib
from pymongo import MongoClient
import datetime

# Modelos y métricas de scikit-learn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, roc_curve
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# Crear directorio para almacenar las gráficas
os.makedirs('graficas', exist_ok=True)

print("1. Conectando a SQL Server y extrayendo datos...")
CONN_STR = "mssql+pyodbc://LUIS/IncendiosForestalesEC?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
engine = create_engine(CONN_STR)

# Cargar datos desde la vista unificada
df = pd.read_sql("SELECT * FROM vw_DatosUnificados ORDER BY fecha, id_ciudad", con=engine)
print(f"Datos cargados exitosamente: {df.shape[0]} registros y {df.shape[1]} columnas.")

# =========================================================================
# 2. PREPROCESAMIENTO Y FEATURE ENGINEERING
# =========================================================================
print("\n2. Realizando preprocesamiento y feature engineering...")

# Asegurar tipo de fecha y extraer componentes temporales
df['fecha'] = pd.to_datetime(df['fecha'])
df['mes'] = df['fecha'].dt.month
df['trimestre'] = df['fecha'].dt.quarter
df['dia_anio'] = df['fecha'].dt.dayofyear

# Variable binaria para la estación seca (Junio a Septiembre en Ecuador)
df['es_estacion_seca'] = df['mes'].isin([6, 7, 8, 9]).astype(int)

# Codificar el nombre de la ciudad
le_ciudad = LabelEncoder()
df['ciudad_cod'] = le_ciudad.fit_transform(df['ciudad_nombre'])

# Tratar posibles nulos que hayan quedado (imputación con la mediana)
df = df.ffill().bfill()

print("- Variables creadas:")
print(df[['fecha', 'mes', 'trimestre', 'dia_anio', 'es_estacion_seca', 'ciudad_cod']].head())

# =========================================================================
# 3. APRENDIZAJE NO SUPERVISADO: K-MEANS
# =========================================================================
print("\n3. Iniciando aprendizaje no supervisado (K-Means)...")

# Variables climáticas y de vegetación para el clustering
features_kmeans = ['temperatura_media', 'humedad_relativa', 'velocidad_viento', 'precipitacion', 'ndvi']
scaler_kmeans = StandardScaler()
X_kmeans = scaler_kmeans.fit_transform(df[features_kmeans])

# A. Método del Codo y Coeficiente de Silueta
inercias = []
siluetas = []
rango_k = range(2, 9)

# Usar muestra aleatoria para silueta por rendimiento O(N^2)
sample_indices = np.random.RandomState(42).choice(len(X_kmeans), size=min(2000, len(X_kmeans)), replace=False)
X_kmeans_sample = X_kmeans[sample_indices]

print("- Calculando métricas para K de 2 a 8...")
for k in rango_k:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_kmeans)
    inercias.append(km.inertia_)
    
    score_sil = silhouette_score(X_kmeans_sample, labels[sample_indices], random_state=42)
    siluetas.append(score_sil)
    print(f"  k={k} | Inercia (Codo): {km.inertia_:.2f} | Silueta: {score_sil:.4f}")

# Graficar Método del Codo
plt.figure(figsize=(8, 4))
plt.plot(rango_k, inercias, marker='o', color='#1f77b4', linewidth=2)
plt.title('Método del Codo para K-Means')
plt.xlabel('Número de Clústeres (K)')
plt.ylabel('Inercia')
plt.grid(True)
plt.tight_layout()
plt.savefig('graficas/curva_codo.png', dpi=150)
plt.close()

# Graficar Coeficiente de Silueta
plt.figure(figsize=(8, 4))
plt.plot(rango_k, siluetas, marker='o', color='#2ca02c', linewidth=2)
plt.title('Coeficiente de Silueta para K-Means')
plt.xlabel('Número de Clústeres (K)')
plt.ylabel('Coeficiente de Silueta')
plt.grid(True)
plt.tight_layout()
plt.savefig('graficas/coeficiente_silueta.png', dpi=150)
plt.close()

# B. Ejecutar K-Means óptimo (k=3 representar Niveles de Riesgo)
print("- Ejecutando K-Means definitivo con K=3...")
kmeans_optimo = KMeans(n_clusters=3, random_state=42, n_init=10)
df['cluster'] = kmeans_optimo.fit_predict(X_kmeans)

# Mapear clusters a etiquetas de riesgo consistentes (Ordenados por temperatura media)
# Esto asegura que 0 = Bajo, 1 = Medio, 2 = Alto Riesgo
cluster_temps = df.groupby('cluster')['temperatura_media'].mean().sort_values()
cluster_mapping = {old_label: new_label for new_label, old_label in enumerate(cluster_temps.index)}
df['cluster_riesgo'] = df['cluster'].map(cluster_mapping)

print("- Perfiles de Clústeres de Riesgo (Centroides Promedio):")
perfiles = df.groupby('cluster_riesgo')[features_kmeans].mean()
perfiles['conteo_dias'] = df.groupby('cluster_riesgo').size()
perfiles['conteo_incendios'] = df.groupby('cluster_riesgo')['incendio_binario'].sum()
perfiles['tasa_incendios'] = df.groupby('cluster_riesgo')['incendio_binario'].mean()
print(perfiles)

# =========================================================================
# 4. APRENDIZAJE SUPERVISADO: CLASIFICACIÓN
# =========================================================================
print("\n4. Iniciando aprendizaje supervisado (Clasificación de Incendios)...")

# Variables predictoras (X) y objetivo (y)
features_supervised = [
    'ciudad_cod', 'ciudad_latitud', 'ciudad_longitud', 'altitud_msnm',
    'velocidad_viento', 'direccion_viento', 'temperatura_media', 'temperatura_max', 
    'temperatura_min', 'humedad_relativa', 'precipitacion', 'ndvi', 
    'mes', 'trimestre', 'dia_anio', 'es_estacion_seca'
]

X = df[features_supervised]
y = df['incendio_binario']

print(f"- Frecuencia de clases de incendio (0=No Incendio, 1=Incendio):\n{y.value_counts()}")

# Dividir dataset 80/20 con semilla 42 y estratificación
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Escalar las variables para los clasificadores
scaler_supervised = StandardScaler()
X_train_scaled = scaler_supervised.fit_transform(X_train)
X_test_scaled = scaler_supervised.transform(X_test)

# A. Clasificador 1: Random Forest
print("- Entrenando Random Forest...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train_scaled, y_train)
y_pred_rf = rf_model.predict(X_test_scaled)
y_prob_rf = rf_model.predict_proba(X_test_scaled)[:, 1]

# B. Clasificador 2: XGBoost
print("- Entrenando XGBoost...")
xgb_model = XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss', n_jobs=-1)
xgb_model.fit(X_train_scaled, y_train)
y_pred_xgb = xgb_model.predict(X_test_scaled)
y_prob_xgb = xgb_model.predict_proba(X_test_scaled)[:, 1]

# Evaluar métricas
def evaluar_modelo(y_true, y_pred, y_prob, name):
    metrics = {
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
        'f1_score': float(f1_score(y_true, y_pred, zero_division=0)),
        'auc_roc': float(roc_auc_score(y_true, y_prob))
    }
    print(f"\nMétricas para {name}:")
    for k, v in metrics.items():
        print(f"  {k:10s}: {v:.4f}")
    return metrics

metrics_rf = evaluar_modelo(y_test, y_pred_rf, y_prob_rf, "Random Forest")
metrics_xgb = evaluar_modelo(y_test, y_pred_xgb, y_prob_xgb, "XGBoost")

# Determinar el mejor modelo
best_model_name = "XGBoost" if metrics_xgb['f1_score'] > metrics_rf['f1_score'] else "Random Forest"
best_model = xgb_model if best_model_name == "XGBoost" else rf_model
best_metrics = metrics_xgb if best_model_name == "XGBoost" else metrics_rf
print(f"\n>> El mejor modelo seleccionado por F1-Score es: {best_model_name}")

# =========================================================================
# 5. GUARDAR RESULTADOS Y MODELOS
# =========================================================================
print("\n5. Guardando artefactos y gráficas de evaluación...")

# Graficar curva ROC comparativa
plt.figure(figsize=(8, 6))
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_prob_rf)
fpr_xgb, tpr_xgb, _ = roc_curve(y_test, y_prob_xgb)
plt.plot(fpr_rf, tpr_rf, label=f"Random Forest (AUC = {metrics_rf['auc_roc']:.4f})", color='#d62728', lw=2)
plt.plot(fpr_xgb, tpr_xgb, label=f"XGBoost (AUC = {metrics_xgb['auc_roc']:.4f})", color='#1f77b4', lw=2)
plt.plot([0, 1], [0, 1], 'k--', lw=1.5)
plt.xlabel('Tasa de Falsos Positivos (FPR)')
plt.ylabel('Tasa de Verdaderos Positivos (TPR)')
plt.title('Curva ROC Comparativa')
plt.legend(loc='lower right')
plt.grid(True)
plt.tight_layout()
plt.savefig('graficas/curva_roc.png', dpi=150)
plt.close()

# Graficar Importancia de Variables del mejor modelo
importancias = best_model.feature_importances_
indices_imp = np.argsort(importancias)[::-1]
plt.figure(figsize=(10, 6))
sns.barplot(x=importancias[indices_imp], y=np.array(features_supervised)[indices_imp], palette='viridis')
plt.title(f'Importancia de Variables - {best_model_name}')
plt.xlabel('Importancia Relativa')
plt.grid(axis='x')
plt.tight_layout()
plt.savefig('graficas/importancia_features.png', dpi=150)
plt.close()

# Guardar el archivo pickle para la aplicación de Streamlit
model_artifacts = {
    'supervised_model': best_model,
    'supervised_model_name': best_model_name,
    'kmeans_model': kmeans_optimo,
    'scaler_supervised': scaler_supervised,
    'scaler_kmeans': scaler_kmeans,
    'le_ciudad': le_ciudad,
    'features_supervised': features_supervised,
    'features_kmeans': features_kmeans,
    'cluster_mapping': cluster_mapping
}
joblib.dump(model_artifacts, 'modelo_incendios.pkl')
print("- Archivo 'modelo_incendios.pkl' guardado exitosamente.")

# =========================================================================
# 6. EXPORTAR RESULTADOS A JSON Y PERSISTENCIA EN MONGODB (LOGS)
# =========================================================================
print("\n6. Exportando resultados a JSON y registrando experimentos en MongoDB...")

# Documento para Random Forest (equivalente a JSON)
doc_rf = {
    'proyecto': "Incendios Forestales Ecuador 2012-2026",
    'fecha': datetime.datetime.now(),
    'algoritmo': 'Random Forest',
    'libreria': 'scikit-learn',
    'parametros': {
        'n_estimators': 100,
        'random_state': 42,
        'n_jobs': -1
    },
    'metricas': metrics_rf,
    'variables_entrada': features_supervised,
    'seleccionado': bool(best_model_name == "Random Forest")
}

# Documento para XGBoost (equivalente a JSON)
doc_xgb = {
    'proyecto': "Incendios Forestales Ecuador 2012-2026",
    'fecha': datetime.datetime.now(),
    'algoritmo': 'XGBoost',
    'libreria': 'xgboost',
    'parametros': {
        'n_estimators': 100,
        'random_state': 42,
        'eval_metric': 'logloss',
        'n_jobs': -1
    },
    'metricas': metrics_xgb,
    'variables_entrada': features_supervised,
    'seleccionado': bool(best_model_name == "XGBoost")
}

# A. Exportar a archivo JSON físico
try:
    import json
    def format_doc_for_json(d):
        d_copy = d.copy()
        if isinstance(d_copy['fecha'], datetime.datetime):
            d_copy['fecha'] = d_copy['fecha'].isoformat()
        return d_copy

    json_data = [format_doc_for_json(doc_rf), format_doc_for_json(doc_xgb)]
    with open('experimentos_ml.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
    print("- Archivo 'experimentos_ml.json' exportado exitosamente en el espacio de trabajo.")
except Exception as e:
    print(f"[ERROR] No se pudo escribir el archivo JSON: {e}")

# B. Persistencia en MongoDB
try:
    # Conexión local a MongoDB
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
    db = client['IncendiosForestales_ML']
    collection = db['experimentos']
    
    # Limpiar experimentos anteriores de esta ejecución para mantener consistencia
    collection.delete_many({"proyecto": "Incendios Forestales Ecuador 2012-2026"})
    
    # Guardar en base de datos
    collection.insert_one(doc_rf)
    collection.insert_one(doc_xgb)
    
    print("- Ambos experimentos se registraron correctamente en MongoDB.")
    
    # Verificar leyendo el último guardado
    print("\nVerificando datos guardados en MongoDB:")
    for doc in collection.find({"proyecto": "Incendios Forestales Ecuador 2012-2026"}):
        print(f"  * Guardado: {doc['algoritmo']} | F1-Score: {doc['metricas']['f1_score']:.4f} | Seleccionado: {doc['seleccionado']}")
        
except Exception as e:
    print(f"\n[ERROR] No se pudo conectar a MongoDB: {e}")
    print("Asegúrate de tener iniciado el servicio de MongoDB en localhost:27017.")

print("\nPipeline de ML ejecutado y guardado completamente.")
