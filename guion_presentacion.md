# 🎤 Guion de Presentación y Estructura de Diapositivas — FireGuard 360

Este documento contiene la estructura de diapositivas y el guion narrativo detallado para una exposición académica de **máximo 10 minutos**. Está diseñado para captar la atención del tribunal desde el primer segundo, justificar técnicamente las decisiones con las gráficas estilo *Latinometrics* y demostrar la robustez del sistema predictivo.

---

## ⏱️ Distribución del Tiempo Total (10 Minutos)
*   **Diapositiva 1 (Gancho e Impacto):** 0:00 - 1:15 (1 min 15 s) — *Incluye el video de 30 segundos.*
*   **Diapositiva 2 (Justificación Física):** 1:15 - 2:15 (1 min)
*   **Diapositiva 3 (Estacionalidad):** 2:15 - 3:15 (1 min)
*   **Diapositiva 4 (Persistencia Híbrida):** 3:15 - 4:15 (1 min)
*   **Diapositiva 5 (Ingeniería de Variables):** 4:15 - 5:15 (1 min)
*   **Diapositiva 6 (Modelamiento y Métricas):** 5:15 - 6:45 (1 min 30 s)
*   **Diapositiva 7 (Feature Importance):** 6:45 - 7:45 (1 min)
*   **Diapositiva 8 (Demo de la Plataforma):** 7:45 - 9:00 (1 min 15 s)
*   **Diapositiva 9 (Conclusiones y Cierre):** 9:00 - 10:00 (1 min)

---

## 📊 Estructura y Guion por Diapositiva

### Diapositiva 1: Portada e Impacto Histórico (Quito, Septiembre 2024)
*   **Contenido Visual:**
    *   Título de la presentación: *FireGuard 360: Persistencia Híbrida y ML para la Alerta Temprana de Incendios en Ecuador*.
    *   Datos de impacto en texto grande: **Quito, Septiembre 2024: +1,600 Hectáreas Devastadas | Guápulo, Cumbayá y Auqui bajo el fuego**.
    *   Cuadro reproductor de video de 30 segundos.
*   **🎬 Mini-guion del Video (30 segundos - Escenas Impactantes):**
    *   *Segundos 0-10 (Silencio, sonido ambiente de crujir de llamas y sirenas distantes):*
        *   *Voz en off:* "El cielo de Quito se oscureció en pleno mediodía. No era una tormenta de lluvia... era el humo de nuestro propio hogar consumiéndose en las laderas de Guápulo."
    *   *Segundos 10-20 (Música de tensión dramática en crescendo):*
        *   *Voz en off:* "El fuego no respetó linderos ni historias. Familias enteras con baldes de agua intentando detener llamas de 10 metros, impulsadas por ráfagas que devoraban años de vegetación en segundos."
    *   *Segundos 20-30 (Música resolutiva y cierre):*
        *   *Voz en off:* "Esta tragedia nos demostró que el aire seco es el verdadero detonante. Detrás del humo hay datos; y detrás de los datos, la oportunidad de actuar antes de que todo vuelva a ser ceniza."
*   **🗣️ Guion del Expositor (1 min 15 s):**
    > "Buenos días, señores miembros del tribunal. El 24 de septiembre de 2024 no fue un día más para Quito. La ciudad se enfrentó a uno de los peores desastres forestales de la última década, que obligó a suspender clases, evacuar barrios enteros y movilizar a todo el cuerpo de bomberos. 
    > 
    > [Iniciar Video de 30s] 
    > 
    > Los incendios forestales en nuestro país no son accidentes aleatorios, son crisis aceleradas por la sequedad y el viento. La pregunta que motivó nuestra investigación es: ¿Cómo podemos anticiparnos a esta devastación utilizando la tecnología y los datos de la NASA? Hoy les presentamos *FireGuard 360*, una plataforma que combina bases de datos híbridas y machine learning para alertar y simular el riesgo de incendios en Ecuador."

---

### Diapositiva 2: Justificación Física y Elección de Variables
*   **Contenido Visual:**
    *   Gráfica *Latinometrics*: **Precipitación mensual vs. Temperatura Máxima**.
    *   Llamada visual: *"La evaporación de 3 días consecutivos reduce la humedad foliar a menos del 10%, convirtiendo el pajonal en combustible seco"*.
    *   Tres puntos clave: 1) Calor acumulado, 2) Déficit de lluvia veraniega, 3) Salud foliar (NDVI).
*   **🗣️ Guion del Expositor (1 min):**
    > "Para predecir un incendio con bases científicas, primero debemos comprender su física. Analizando los datos históricos (2012-2026), identificamos que el verdadero disparador en la Sierra andina no es solo el calor de un día caluroso aislado, sino el déficit acumulativo de humedad. 
    > 
    > Como se observa en nuestra gráfica en estilo Latinometrics, durante el verano (julio a septiembre) la precipitación cae a sus mínimos históricos, mientras la curva de temperaturas máximas promedio escala hasta superar los 24.6 °C. Esta combinación evapora el agua del suelo y marchita la cobertura vegetal (NDVI), reduciendo la humedad del follaje a niveles críticamente inflamables. Esto justifica por qué seleccionamos temperatura, lluvia, humedad, viento y NDVI como variables predictoras."

---

### Diapositiva 3: Comportamiento Estacional de Incendios en Ecuador
*   **Contenido Visual:**
    *   Gráfica *Latinometrics*: **Detecciones satelitales acumuladas por mes (Noviembre como pico)**.
    *   Llamada visual: *"Noviembre: Pico histórico con un récord de 19,138 focos acumulados en el dataset"*.
*   **🗣️ Guion del Expositor (1 min):**
    > "Al cruzar el registro climático con los focos reales detectados por los satélites MODIS y VIIRS de la NASA, la estacionalidad queda en evidencia. Este gráfico de barras acumuladas muestra cómo la actividad del fuego comienza a crecer a partir de julio y alcanza su pico crítico absoluto en el mes de **Noviembre**, acumulando un récord histórico de **19,138 focos de calor** en nuestro dataset.
    > 
    > Este patrón de acumulación estival demuestra que el riesgo es temporalmente predecible y responde a meses acumulados de sequía. Por esta razón, incluimos variables temporales como el mes, el trimestre y el día del año, además de una bandera binaria de estación seca, permitiendo al algoritmo entender el comportamiento cíclico del fuego en nuestro territorio."

---

### Diapositiva 4: Arquitectura de Persistencia Híbrida (SQL + MongoDB)
*   **Contenido Visual:**
    *   Diagrama de flujo de datos simplificado.
    *   SQL Server (3FN, vw_DatosUnificados con OUTER APPLY).
    *   MongoDB (Experimentos MLOps y logs de actividad en formato JSON).
    *   Llamada de rendimiento: *"Unificación temporal de 72,532 alertas satelitales y 21,100 registros climáticos en 0.45 segundos"*
*   **🗣️ Guion del Expositor (1 min):**
    > "Unificar datos de clima diario, lecturas satelitales de NDVI cada 16 días y alertas esporádicas de incendios es un desafío lógico complejo. Para resolverlo, diseñamos una arquitectura de persistencia híbrida.
    > 
    > La base relacional, implementada en SQL Server bajo la Tercera Forma Normal (3FN), aloja los datos estructurados en una estrella de hechos y dimensiones. Creamos la vista dinámica `vw_DatosUnificados` mediante el operador `OUTER APPLY`. Esto permite que a cada día de clima se le asocie la lectura real de NDVI más cercana hacia atrás en el tiempo, evitando inyectar datos sintéticos y resolviendo el cruce de las **72,532 alertas satelitales de incendios** con las **21,100 filas de clima** en menos de **0.45 segundos** gracias al uso de índices no agrupados.
    > 
    > De manera complementaria, MongoDB actúa como nuestro repositorio NoSQL. Al ser una base documental, nos da la flexibilidad de guardar en formato JSON los hiperparámetros e índices de desempeño de cada experimento de MLOps, garantizando la trazabilidad, además de registrar logs forenses de las acciones de los usuarios en tiempo real."

---

### Diapositiva 5: Ingeniería de Variables de Memoria Climática (Lag Features)
*   **Contenido Visual:**
    *   Esquema visual de la ventana móvil de 3 días por ciudad.
    *   Variables creadas: `temp_max_promedio_3d`, `precipitacion_acumulada_3d`, `humedad_promedio_3d`, `viento_promedio_3d`.
    *   Dato de impacto: *"La media acumulada de 3 días previos superó en peso predictivo al clima del mismo día, confirmando el comportamiento físico acumulativo"*.
*   **🗣️ Guion del Expositor (1 min):**
    > "Una de las mayores innovaciones metodológicas de este proyecto para evitar el sobreajuste y mejorar la precisión fue el desarrollo de variables de memoria climática acumulada, conocidas en ciencia de datos como *Lag Features*. 
    > 
    > En lugar de alimentar al modelo únicamente con el clima de las últimas 24 horas, calculamos la media móvil y sumas acumuladas de los últimos 3 días agrupadas cronológicamente por ciudad. Esto simula el proceso acumulativo real de desecación del material forestal: un día lluvioso seguido de dos días calurosos tiene un riesgo significativamente menor de incendio que tres días de calor extremo y nula lluvia. Estas variables le otorgan al modelo una 'memoria temporal' que mejoró sustancialmente la precisión del modelo."

---

### Diapositiva 6: Resultados y Comparativa de Modelos
*   **Contenido Visual:**
    *   Tabla comparativa de métricas: Random Forest vs. XGBoost.
    *   Métricas del modelo campeón (XGBoost): **Accuracy: 69.22% | Recall: 63.81% | F1-Score: 62.27%**.
    *   Llamada de impacto: *"XGBoost redujo los falsos negativos en un 13.6% al elevar el Recall de 50.18% a 63.81%"*.
*   **🗣️ Guion del Expositor (1 min 30 s):**
    > "Evaluamos dos de los algoritmos más potentes para datos tabulares: Random Forest y XGBoost. Tras una división estratificada 80/20 y escalamiento, aplicamos regularizaciones e hiperparámetros para penalizar el ruido y asegurar la generalización.
    > 
    > Como se observa en la tabla de resultados, el modelo ganador es **XGBoost**, logrando una exactitud (Accuracy) de **69.22%** y un área bajo la curva (AUC-ROC) de **73.51%**. Sin embargo, la métrica estrella en nuestro contexto es el **Recall (Sensibilidad)**, el cual logramos impulsar hasta el **63.81%** gracias al ajuste de pesos de clase (`scale_pos_weight=1.5`). 
    > 
    > En la gestión de desastres, el costo de un falso negativo (no predecir un incendio que sí ocurre) es devastador. Un Recall del 63.81% en el conjunto de prueba independiente (21,100 registros) garantiza que el modelo actúa como un escudo preventivo confiable, capturando la mayoría de los eventos críticos y alertando a los equipos de emergencia a tiempo."

---

### Diapositiva 7: Importancia de Variables en XGBoost (Feature Importance)
*   **Contenido Visual:**
    *   Gráfico de barras de importancia de variables del modelo XGBoost.
    *   Llamada visual destacando a la velocidad del viento y la memoria climática.
    *   Dato real: *"El viento promedio de 3 días (`viento_promedio_3d`) lidera el peso predictivo en la Sierra andina, donde los vientos secos actúan como soplites en pastizales secos"*.
*   **🗣️ Guion del Expositor (1 min):**
    > "Para validar la coherencia física de nuestro modelo de Machine Learning, analizamos el peso predictivo que el algoritmo XGBoost asignó a cada variable.
    > 
    > El gráfico revela un comportamiento lógico e interesante: la velocidad del viento (`velocidad_viento`) y su dirección, junto con el promedio de viento de 3 días, lideran la importancia de variables. El viento no solo aporta el oxígeno necesario para acelerar la combustión, sino que es el motor de la propagación física de las llamas. 
    > 
    > Inmediatamente después se ubican la humedad relativa y la temperatura máxima acumulada de 3 días, seguidas del NDVI. Este resultado valida empíricamente nuestra hipótesis inicial: el riesgo de incendios es un proceso acumulativo condicionado por la desecación del material forestal fino y la fuerza del viento local."

---

### Diapositiva 8: Plataforma Interactiva FireGuard 360 (Streamlit)
*   **Contenido Visual:**
    *   Capturas de pantalla del login, el mapa interactivo de calor, el simulador de cono de viento y la consola de auditoría.
    *   Lista de funciones: Monitoreo Satelital (NASA FIRMS), Predicción en vivo, Simulación física de propagación y DRP transaccional.
    *   Llamada técnica: *"Auditoría forense de logins de MongoDB Compass y restauración DRP de SQL Server en menos de 10 segundos ante fallos críticos simulados"*.
*   **🗣️ Guion del Expositor (1 min 15 s):**
    > "Toda esta complejidad científica fue empaquetada en una aplicación web interactiva desarrollada en Streamlit, llamada *FireGuard 360*. 
    > 
    > La plataforma cuenta con seguridad basada en roles de base de datos. Un usuario analista puede visualizar en vivo mapas georreferenciados del país consumiendo la API activa de anomalías térmicas de la NASA, realizar inferencias ingresando variables en tiempo real y ejecutar simulaciones vectoriales del cono de propagación de llamas según el viento.
    > 
    > Por su parte, la vista del administrador permite auditar los logs forenses de MongoDB, garantizando la gobernanza del sistema, y ejecutar copias de seguridad DRP (Full, Diferencial e incremental) de SQL Server directamente desde la web, asegurando la continuidad del sistema ante fallos críticos."

---

### Diapositiva 9: Conclusiones e Impacto
*   **Contenido Visual:**
    *   Tres grandes conclusiones: 1) Sinergia de persistencia híbrida, 2) Robustez de modelos regularizados, 3) Herramienta de soporte real para gestión de riesgos.
    *   Datos de contacto y cierre.
*   **🗣️ Guion del Expositor (1 min):**
    > "Para concluir, esta investigación demuestra que la integración de variables biológicas y meteorológicas satelitales a través de una persistencia políglota proporciona una herramienta robusta de soporte a las decisiones. 
    > 
    > Logramos eliminar las fugas de datos mediante vistas relacionales y potenciar la sensibilidad predictiva de XGBoost al 63.81% sin incurrir en sobreajuste. *FireGuard 360* demuestra que la ciencia de datos puede y debe ser el pilar fundamental en la prevención de desastres forestales en Ecuador, salvaguardando la biodiversidad y protegiendo vidas humanas en nuestras ciudades.
    > 
    > Quedamos a su entera disposición para la ronda de preguntas. Muchas gracias por su atención."
