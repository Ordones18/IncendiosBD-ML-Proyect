# 🎤 Guion de Presentación y Estructura de Diapositivas — FireGuard 360

Este documento contiene la estructura de diapositivas y el guion narrativo detallado para una exposición académica de **máximo 10 minutos**. Está diseñado para captar la atención desde el primer segundo, justificar técnicamente las decisiones con las gráficas estilo *Latinometrics* y demostrar la robustez del sistema predictivo.

---

## ⏱️ Distribución del Tiempo Total (10 Minutos)
*   **Diapositiva 1, 2 y 3 (Introducción, Justificación e Impacto Histórico):** 0:00 - 2:15 (2 min 15 s) — *Incluye el video de 30 segundos.*
*   **Diapositiva 4 (Justificación Física y Elección de Variables):** 2:15 - 3:00 (45 s)
*   **Diapositiva 5 (Comportamiento Estacional de Incendios):** 3:00 - 3:45 (45 s)
*   **Diapositiva 6 (Factores Críticos y Triángulo del Fuego):** 3:45 - 4:45 (1 min)
*   **Diapositiva 7 (Persistencia Híbrida SQL + MongoDB):** 4:45 - 5:30 (45 s)
*   **Diapositiva 8 (Ingeniería de Variables - Lags):** 5:30 - 6:15 (45 s)
*   **Diapositiva 9 (Resultados y Comparativa de Modelos):** 6:15 - 7:15 (1 min)
*   **Diapositiva 10 (Importancia de Variables en XGBoost):** 7:15 - 8:00 (45 s)
*   **Diapositiva 11 (Demostración de la Plataforma en Vivo):** 8:00 - 9:15 (1 min 15 s)
*   **Diapositiva 12 (Conclusiones y Cierre Emotivo):** 9:15 - 10:00 (45 s)

---

## 📊 Estructura y Guion por Diapositiva

### Diapositiva 1: Portada y Presentación del Proyecto
*   **Contenido Visual:**
    *   Título Principal: **FireGuard 360**
    *   Subtítulo: *Infraestructura de Persistencia Híbrida y Despliegue de Modelos de Machine Learning para la Gestión de Riesgos de Incendios*.
    *   Autores, Universidad y Carrera de Inteligencia Artificial.
*   **🗣️ Guion del Expositor (45 s):**
    > "Hoy les presentaremos nuestro proyecto de investigación formativa titulado FireGuard 360. Nuestra plataforma es una solución de ciencia de datos de extremo a extremo que unifica bases de datos relacionales y documentales con algoritmos predictivos supervisados y no supervisados, para estimar la probabilidad y simular la propagación de incendios forestales en cuatro ciudades críticas del Ecuador."

---

### Diapositiva 2: Introducción a la Justificación
*   **Contenido Visual:**
    *   Problemática nacional: El impacto de los incendios forestales en la infraestructura, fauna y vidas humanas.
    *   Mapas de zonas vulnerables: Quito, Guayaquil, Riobamba y Cuenca.
    *   Objetivo: Transformar terabytes de datos satelitales NASA en alertas operativas tempranas.
*   **🗣️ Guion del Expositor (45 s):**
    > "Los incendios forestales representan una de las mayores crisis climáticas y ambientales en el Ecuador. Año tras año, miles de hectáreas de bosques y páramos andinos son devoradas por las llamas, afectando directamente a la biodiversidad, la calidad del aire de nuestras ciudades y la seguridad de sus habitantes. El problema no es la falta de datos, la NASA genera diariamente terabytes de alertas y lecturas meteorológicas; el verdadero desafío es la ausencia de una infraestructura unificada y modelos calibrados para procesar esta información y alertar a tiempo."

---

### Diapositiva 3: Impacto Histórico (Video y Cierre de Justificación)
*   **Contenido Visual:**
    *   Texto destacado: **Quito, Septiembre 2024: +1,600 Hectáreas Devastadas | Guápulo, Cumbayá y Auqui bajo el fuego**.
    *   Reproductor de video integrado (30 segundos).
*   **🎬 Mini-guion de Video (30s) — Narrativa Dramática:**
    *   **[0-10s - Crujir de llamas]:** "El cielo de Quito se oscureció en pleno mediodía. No era una tormenta de lluvia... era el humo de nuestro propio hogar consumiéndose en las laderas de Guápulo."
    *   **[10-20s - Música de tensión]:** "El fuego no respetó linderos ni historias. Familias enteras con baldes de agua intentando detener llamas de 10 metros, impulsadas por ráfagas que devoraban años de vegetación en segundos."
    *   **[20-30s - Música de cierre]:** "Esta tragedia nos demostró que el aire seco es el verdadero detonante. Detrás del humo hay datos; y detrás de los datos, la oportunidad de actuar antes de que todo vuelva a ser ceniza. Aquí es donde nace FireGuard 360: un escudo tecnológico que transforma la información climática y satelital en alertas tempranas, uniendo la persistencia híbrida y la analítica predictiva para proteger nuestras ciudades y salvar vidas antes de que aparezcan las llamas."
*   **🗣️ Guion del Expositor (45 s):**
    > "La tragedia vivida en Quito durante septiembre de 2024 fue el punto de inflexión que justificó científicamente el desarrollo de FireGuard 360. El video que acabamos de presenciar ilustra la velocidad destructiva del fuego y la necesidad urgente de contar con herramientas tecnológicas predictivas. No podemos seguir reaccionando tarde; debemos anticipar el peligro antes de que comience el fuego."

---

### Diapositiva 4: Justificación Física y Elección de Variables
*   **Contenido Visual:**
    *   Gráfico de doble eje: **Estacionalidad Climática: Sequía y Calor Acumulados** (Precipitación promedio vs. Temperatura Máxima).
    *   Anotación destacada: *Máxima temperatura y menor lluvia registrada en el mes de Septiembre*.
*   **🗣️ Guion del Expositor (45 s):**
    > "Para predecir un incendio, debemos comprender su física. Analizando nuestra serie histórica, identificamos que el verdadero disparador en la Sierra no es solo un día de calor aislado, sino el déficit acumulado de humedad. 
    > 
    > Como se observa en nuestra gráfica, durante el verano andino la precipitación cae a sus mínimos históricos, mientras la curva de temperaturas máximas promedio escala hasta su punto más alto en septiembre. Esta combinación deseca el material vegetal y debilita la resistencia del suelo. De aquí nace la justificación física para seleccionar las coordenadas geográficas, la altitud, la temperatura, el viento, la precipitación y la humedad relativa como nuestras variables climáticas base."

---

### Diapositiva 5: Comportamiento Estacional de Incendios en Ecuador
*   **Contenido Visual:**
    *   Gráfico de barras: **Noviembre: El Mes del Fuego en Ecuador** (Focos acumulados 2012-2026).
    *   Anotación destacada: **Pico del año (19,138 focos acumulados en noviembre)**.
*   **🗣️ Guion del Expositor (45 s):**
    > "Al cruzar el registro climático con los focos reales detectados por satélites, el comportamiento estacional queda en evidencia. En este gráfico observamos cómo la actividad del fuego comienza a incrementarse a partir de julio y agosto, coincidiendo con la época seca, y alcanza su pico crítico absoluto en el mes de noviembre con 19,138 anomalías térmicas acumuladas. 
    > 
    > La acumulación estival seca la biomasa durante meses, dejando la vegetación lista para arder al final de la temporada. Esto justifica por qué incluimos variables temporales como el mes, el trimestre, el día del año y la bandera de estación seca para que el modelo aprenda este ciclo estacional."

---

### Diapositiva 6: Análisis de Factores Críticos y el Triángulo del Fuego
*   **Contenido Visual:**
    *   Panel unificado con 4 gráficos estilo *Latinometrics* (conforme a la gráfica en pantalla):
        *   **Top Izquierda (Viento Fuerte):** Velocidad promedio mensual del viento (m/s), con vientos máximos de verano en julio (3.63 m/s) y agosto (3.59 m/s).
        *   **Top Derecha (Humedad Relativa):** Humedad relativa promedio mensual (%), alcanzando el mínimo del año en septiembre con un 73.3%.
        *   **Bottom Izquierda (NDVI):** Índice NDVI promedio mensual nacional, tocando su punto mínimo de salud foliar en septiembre con 0.22.
        *   **Bottom Derecha (Relación Estacional):** Gráfico combinado de curva de NDVI (verde) vs. volumen de focos históricos de incendios (barras naranjas), mostrando el desfase biológico.
*   **🗣️ Guion del Expositor (1 min):**
    > "Ahora pasamos a explicar el núcleo de nuestra justificación científica: el comportamiento físico del territorio. En esta diapositiva unificamos cuatro análisis exploratorios que explican por qué se desatan los incendios forestales y cómo se conectan las variables. A esto lo llamamos el Triángulo del Fuego:
    > 
    > **Gráfico 1: Viento Fuerte (El Propagador):** El primer gráfico (arriba a la izquierda) nos muestra que durante el verano andino, los vientos alcanzan su velocidad máxima promedio en julio con 3.63 m/s y se mantienen elevados en agosto con 3.59 m/s. Esto funciona como un acelerador físico y un inyector de oxígeno constante sobre cualquier chispa en el terreno.
    > 
    > **Gráfico 2: Humedad Relativa Mínima (El Escudo Débil):** A la derecha, observamos la humedad del aire. Durante el verano, la humedad relativa cae de forma drástica, alcanzando su mínimo anual en septiembre con un 73.3%. Este aire extremadamente seco marchita el suelo y elimina su capacidad de autoenfriamiento.
    > 
    > **Gráfico 3: NDVI (Pérdida de Verdor o Combustible):** Abajo a la izquierda, vemos el índice satelital de verdor de la NASA. Debido al viento fuerte previo y al aire seco, la vegetación sufre un estrés hídrico extremo y se seca. El NDVI llega a su punto más bajo en septiembre con un valor de 0.22, lo que significa que el verdor del follaje desaparece y se convierte en biomasa seca y combustible altamente inflamable.
    > 
    > **Gráfico 4: Relación NDVI vs. Incendios (El Desencadenante):** Finalmente, en el gráfico combinado (abajo a la derecha) vemos la correlación biológica. Conforme la curva verde del NDVI cae al mínimo en septiembre por la sequía, se produce un efecto acumulativo en la biomasa que termina detonando en la explosión de incendios que observamos en las barras de noviembre con 19,138 focos de calor.
    > 
    > En resumen, esta sinergia nos demuestra que un incendio es un proceso acumulativo: el viento seca, el aire seco evapora y la vegetación marchita se acumula hasta explotar en incendios semanas después. Esta es la justificación física de por qué decidimos crear nuestras variables de memoria climática de 3 días en SQL Server y Python, ya que el clima del día de hoy está fuertemente influenciado por la desecación acumulada en los días anteriores."

---

### Diapositiva 7: Arquitectura de Persistencia Híbrida (SQL + MongoDB)
*   **Contenido Visual:**
    *   Esquema de Base de Datos Híbrida.
    *   **SQL Server (Relacional - 3FN):** Dimensión Ciudades, Hecho Clima (21,100 filas), Hecho NDVI (1,328 filas) y Hecho Incendios (72,532 alertas) enlazados por `FK_id_ciudad`.
    *   **MongoDB (No Relacional):** Registro de logs de actividad y experimentos MLOps en documentos JSON.
    *   Dato de impacto: *"Unificación temporal de 72,532 alertas satelitales y 21,100 registros climáticos en 0.45 segundos gracias a la vista vw_DatosUnificados con OUTER APPLY e índices"*
*   **🗣️ Guion del Expositor (45 s):**
    > "Para organizar este gran volumen de datos, diseñamos una arquitectura de persistencia híbrida. En el lado relacional, estructuramos SQL Server bajo la Tercera Forma Normal (3FN), enlazando de forma limpia las dimensiones de ciudades con las tablas de hechos de clima, vegetación e incendios satelitales mediante llaves foráneas. Esto eliminó la redundancia y garantizó la integridad referencial. 
    > 
    > Para cruzar las 72,532 alertas satelitales individuales con las 21,100 filas de clima diario sin generar registros ficticios, creamos una vista indexada optimizada mediante el operador `OUTER APPLY`. Por otra parte, integramos MongoDB como base documental para registrar los logs forenses de usuarios y los hiperparámetros de nuestros experimentos de MLOps en formato JSON, garantizando la gobernanza del sistema."

---

### Diapositiva 8: Ingeniería de Variables de Memoria Climática (Lag Features)
*   **Contenido Visual:**
    *   Diagrama explicativo de la ventana móvil de 3 días agrupada por ciudad.
    *   Fórmulas en pantalla:
        *   `temp_max_promedio_3d = promedio(temperatura_max[T-2..T])`
        *   `precipitacion_acumulada_3d = suma(precipitacion[T-2..T])`
        *   `humedad_promedio_3d = promedio(humedad_relativa[T-2..T])`
        *   `viento_promedio_3d = promedio(velocidad_viento[T-2..T])`
*   **🗣️ Guion del Expositor (45 s):**
    > "La gran innovación de nuestro pipeline para evitar el sobreajuste fue el cálculo de variables de memoria climática acumulada, o Lag Features. En la naturaleza, el material forestal no se seca en un solo día caluroso. Tres días consecutivos de calor extremo acumulan un peligro de incendio infinitamente mayor que un día caluroso precedido por lluvias. 
    > 
    > Mediante transformaciones de ventanas móviles agrupadas por ciudad en Python, calculamos el promedio de temperatura máxima, de humedad, de viento y la suma de precipitaciones de los últimos 3 días. Estas variables de memoria le dieron al algoritmo la capacidad de analizar tendencias acumulativas, mejorando significativamente la precisión."

---

### Diapositiva 9: Resultados y Comparativa de Modelos
*   **Contenido Visual:**
    *   Tabla comparativa de métricas en el conjunto de prueba independiente:
        | Algoritmo | Exactitud (Accuracy) | Precisión | Recall (Sensibilidad) | F1-Score | AUC-ROC |
        | :--- | :--- | :--- | :--- | :--- | :--- |
        | Random Forest (Regularizado) | 68.18% | 0.5958 | 0.6238 | 0.6095 | 0.7326 |
        | **XGBoost (Campeón)** | **69.22%** | **0.6081** | **0.6381** | **0.6227** | **0.7351** |
*   **🗣️ Guion del Expositor (1 min):**
    > "Entrenamos y comparamos dos modelos basados en árboles: Random Forest y XGBoost. XGBoost resultó ser nuestro modelo campeón, logrando una exactitud del 69.22% y un área bajo la curva ROC del 73.51%. 
    > 
    > La métrica prioritaria en la gestión de desastres es el Recall o Sensibilidad, ya que un falso negativo (no predecir un incendio real) puede ser trágico. Al ajustar los pesos de las clases con `scale_pos_weight` en 1.5, logramos elevar el Recall a un robusto 63.81% en el conjunto de prueba independiente, garantizando que el modelo detecte la gran mayoría de las situaciones críticas reales."

---

### Diapositiva 10: Importancia de Variables en el Modelo Predictivo
*   **Contenido Visual:**
    *   Gráfico de barras: **Feature Importance de XGBoost** (liderado por variables temporales y de ubicación).
    *   Destacados en color de énfasis: 1) Trimestre, 2) Mes, 3) Identificador y coordenadas de Ciudad, 4) Día del año.
*   **🗣️ Guion del Expositor (45 s):**
    > "Al analizar la importancia de las variables determinada por XGBoost, observamos un comportamiento sumamente coherente. Como se aprecia en la gráfica, las variables temporales como el trimestre, el mes y el día del año acumulan más del 50% de la importancia predictiva global. Esto refleja la naturaleza cíclica del peligro de incendios en Ecuador, concentrado de manera casi exclusiva durante la temporada seca de verano en la Sierra y la Costa.
    > 
    > Le siguen de cerca las variables geográficas como el código de la ciudad y sus coordenadas de latitud y longitud, que permiten al modelo espacializar y diferenciar los climas basales de cada zona. Finalmente, las variables meteorológicas directas como la temperatura máxima, la precipitación y la humedad actúan en un segundo nivel para afinar la predicción diaria dentro de cada estación. Esto demuestra que nuestro clasificador toma decisiones basadas en el ciclo estacional físico y la geografía real del territorio."

---

### Diapositiva 11: Demostración e Inferencia en Vivo (Streamlit)
*   **Contenido Visual:**
    *   Estructura de la App en 7 Pestañas de la Interfaz:
        1. **Mapa de Calor:** Historial de focos reactivo con filtros de confianza y años sobre mapa Folium.
        2. **Clústeres de Riesgo:** Visualización 3D interactiva de K-Means y reglas asociadas.
        3. **Predicción:** Formulario de inferencia en vivo con cálculo dinámico de Lags climáticos en base a consultas SQL previos.
        4. **Simulación:** Cono vectorial georreferenciado de propagación física de fuego por viento.
        5. **Tiempo Real:** API NASA FIRMS en vivo con exportación CSV/JSON de anomalías térmicas activas.
        6. **Historial de Experimentos:** MLOps para control de versiones del entrenamiento en MongoDB.
        7. **Gobernanza y DRP:** Visualización de logs forenses de usuarios y ejecutor de copias de seguridad físicas en SSMS (Full, Dif, Log).
*   **🗣️ Guion del Expositor (1 min 15 s):**
    > "Toda esta complejidad científica fue empaquetada en una aplicación web interactiva desarrollada en Streamlit, llamada FireGuard 360, la cual cuenta con seguridad basada en roles. 
    > 
    > Un analista puede explorar mapas históricos de focos satelitales, predecir la probabilidad de incendios recuperando automáticamente el historial de clima previo de SQL Server, simular vectorialmente la trayectoria física de las llamas según el viento en mapas Folium y consultar la API de la NASA en tiempo real. 
    > 
    > Por su parte, la consola del administrador lee en vivo los logs forenses de MongoDB y permite ejecutar copias de seguridad DRP (Full, Diferencial e incremental) de SQL Server directamente desde la interfaz, garantizando la gobernanza y la continuidad del sistema ante fallos."

---

### Diapositiva 12: Conclusión y Cierre Emotivo
*   **Contenido Visual:**
    *   Lema de Cierre: **"Prevenir es predecir: Ciencia de Datos para salvaguardar la vida y el futuro de nuestras laderas andinas."**
    *   Integrantes del proyecto y agradecimiento.
*   **🗣️ Guion del Expositor (45 s):**
    > "FireGuard 360 no es simplemente un ejercicio estadístico, ni un conjunto de scripts en un servidor. Nace del recuerdo de ver a nuestra capital cubierta en cenizas, de la desesperación de familias defendiendo sus hogares con baldes de agua frente a las laderas en llamas. 
    > 
    > Cada celda de memoria climática calculada, cada consulta relacional optimizada y cada predicción de XGBoost representa un segundo ganado al fuego. La ciencia de datos cobra su verdadero sentido cuando se pone al servicio de la vida, de la conservación de nuestros páramos y de la seguridad de las futuras generaciones. Predecir es el primer paso para proteger, y hoy, con este sistema, damos ese paso adelante. Muchas gracias por su atención."
