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
    *   *Segundos 0-10:* Toma aérea del cerro Auqui cubierto de humo negro denso, con el sol teñido de rojo. *(Audio: Sonido ambiente de sirenas lejanas y viento fuerte).*
    *   *Segundos 10-20:* Tomas rápidas a nivel de suelo en Guápulo. Llamas de más de 10 metros consumiendo pajonales secos cerca de viviendas. Ciudadanos evacuando y ayudando con baldes de agua.
    *   *Segundos 20-30:* El cuerpo de bomberos luchando en laderas empinadas contra ráfagas de viento que reavivan las brasas. Cierre con el lema: *"El aire seco es el verdadero enemigo"*.
*   **🗣️ Guion del Expositor (1 min 15 s):**
    > "Buenos días, señores miembros del tribunal. Septiembre de 2024 quedó marcado en la historia de Quito. La imagen que ven en pantalla no es una escena de ficción: es la ladera de Guápulo ardiendo, consumiendo más de 1,600 hectáreas en cuestión de horas, cubriendo de humo la capital y forzando la evacuación de cientos de familias. Los incendios forestales en nuestro país no son eventos aislados; son crisis climáticas aceleradas por la sequedad y el viento. 
    > 
    > [Iniciar Video de 30s] 
    > 
    > Mientras observamos la ferocidad del fuego en estas escenas reales, nos enfrentamos a una pregunta técnica crucial: ¿Cómo podemos anticipar y mitigar estas catástrofes antes de que las llamas toquen las zonas urbanas? Diariamente se generan terabytes de datos satelitales en la NASA. Sin embargo, la falta de una infraestructura unificada y modelos predictivos calibrados nos impide actuar a tiempo. Hoy les presentamos *FireGuard 360*, una plataforma que combina bases de datos híbridas y machine learning para alertar y simular el riesgo de incendios en Ecuador."

---

### Diapositiva 2: Justificación Física y Elección de Variables
*   **Contenido Visual:**
    *   Gráfica *Latinometrics*: **Precipitación mensual vs. Temperatura Máxima**.
    *   Tres puntos clave: 1) Calor acumulado, 2) Déficit de lluvia veraniega, 3) Salud foliar (NDVI).
*   **🗣️ Guion del Expositor (1 min):**
    > "Para predecir un incendio con bases científicas, primero debemos comprender su física. Analizando los datos históricos (2012-2026), identificamos que el verdadero disparador en la Sierra andina no es solo el calor del día, sino el déficit de humedad. Como se observa en nuestra primera gráfica, durante el verano (julio a septiembre) la precipitación cae a sus mínimos históricos, mientras la curva de temperaturas máximas promedio escala hasta superar los 24.6 °C. 
    > 
    > Esta combinación evapora el agua del suelo y marchita la cobertura vegetal (medida a través del NDVI de la NASA). Esta pérdida de verdor actúa como acumulador de biomasa seca: combustible orgánico listo para arder ante la más mínima chispa. De aquí nace la justificación para seleccionar la temperatura máxima, la precipitación diaria, el NDVI y la humedad relativa como las variables de entrada de nuestro modelo."

---

### Diapositiva 3: Comportamiento Estacional de Incendios en Ecuador
*   **Contenido Visual:**
    *   Gráfica *Latinometrics*: **Detecciones satelitales acumuladas por mes (Noviembre como pico)**.
    *   Llamada visual: *"Noviembre: Pico crítico del año con focos de calor acumulados"*.
*   **🗣️ Guion del Expositor (1 min):**
    > "Al cruzar el registro climático con los focos reales detectados por los satélites MODIS y VIIRS de la NASA, la estacionalidad queda en evidencia. Este gráfico de barras acumuladas muestra cómo la actividad del fuego comienza a crecer a partir de julio y agosto, coincidiendo con los vientos secos, y alcanza su pico crítico absoluto en el mes de **Noviembre**. 
    > 
    > Este patrón de acumulación estival demuestra que el riesgo es temporalmente predecible. La sequía prolongada de los meses previos actúa de forma acumulativa en el terreno. Por esta razón, incluimos variables temporales como el mes, el trimestre y el día del año, además de una bandera binaria de estación seca, permitiendo al algoritmo entender el comportamiento cíclico del fuego en nuestro territorio."

---

### Diapositiva 4: Arquitectura de Persistencia Híbrida (SQL + MongoDB)
*   **Contenido Visual:**
    *   Diagrama de flujo de datos simplificado.
    *   SQL Server (3FN, vw_DatosUnificados con OUTER APPLY).
    *   MongoDB (Experimentos MLOps y logs de auditoría forense en JSON).
*   **🗣️ Guion del Expositor (1 min):**
    > "Unificar datos diarios de clima, lecturas satelitales de vegetación cada 16 días y alertas esporádicas de incendios es un desafío lógico. Para resolverlo, diseñamos una arquitectura de persistencia híbrida.
    > 
    > La base relacional, implementada en SQL Server bajo la Tercera Forma Normal, aloja los datos estructurados en una estrella de hechos y dimensiones. Creamos la vista dinámica `vw_DatosUnificados` mediante el operador `OUTER APPLY`. Esto permite que a cada día de clima se le asocie la lectura real de NDVI más cercana hacia atrás en el tiempo, evitando inyectar datos sintéticos y eliminando la fuga de datos en el entrenamiento.
    > 
    > Complementariamente, integramos MongoDB. Al ser una base documental, nos da la flexibilidad de guardar en formato JSON los hiperparámetros y métricas de cada experimento de MLOps, garantizando la trazabilidad, además de registrar en tiempo real logs forenses de las acciones de los usuarios."

---

### Diapositiva 5: Ingeniería de Variables de Memoria Climática (Lag Features)
*   **Contenido Visual:**
    *   Esquema visual de la ventana móvil de 3 días por ciudad.
    *   Variables creadas: `temp_max_promedio_3d`, `precipitacion_acumulada_3d`, `humedad_promedio_3d`, `viento_promedio_3d`.
*   **🗣️ Guion del Expositor (1 min):**
    > "Una de las mayores innovaciones metodológicas de este proyecto para evitar el sobreajuste y mejorar la precisión fue el desarrollo de variables de memoria climática acumulada, conocidas en ciencia de datos como *Lag Features*. 
    > 
    > En lugar de alimentar al modelo únicamente con el clima de las últimas 24 horas, calculamos la media móvil y sumas acumuladas de los últimos 3 días agrupadas cronológicamente por ciudad. Esto simula el proceso acumulativo real de desecación del material forestal: un día lluvioso seguido de dos días calurosos tiene un riesgo significativamente menor de incendio que tres días consecutivos de calor extremo y nula lluvia. Estas variables le otorgan al modelo una 'memoria temporal' de la salud del suelo."

---

### Diapositiva 6: Resultados y Comparativa de Modelos
*   **Contenido Visual:**
    *   Tabla comparativa de métricas: Random Forest vs. XGBoost.
    *   Métricas del modelo campeón (XGBoost): **Accuracy: 69.22% | Recall: 63.81% | F1-Score: 62.27%**.
*   **🗣️ Guion del Expositor (1 min 30 s):**
    > "Evaluamos dos de los algoritmos más potentes para datos tabulares: Random Forest y XGBoost. Tras una rigurosa división estratificada 80/20 y escalamiento, aplicamos regularizaciones e hiperparámetros para penalizar el ruido y asegurar la generalización.
    > 
    > Como se observa en la tabla de resultados, el modelo ganador es **XGBoost**, logrando una exactitud (Accuracy) de **69.22%** y un área bajo la curva (AUC-ROC) de **73.51%**. Sin embargo, la métrica estrella en nuestro contexto es el **Recall (Sensibilidad)**, el cual logramos impulsar hasta el **63.81%** gracias al ajuste de pesos de clase (`scale_pos_weight=1.5`). 
    > 
    > En la gestión de desastres, el costo de un falso negativo (no predecir un incendio que sí ocurre) es devastador. Un Recall del 63.81% garantiza que el modelo actúa como un escudo preventivo confiable, capturando la mayoría de los eventos críticos en el conjunto de validación independiente."

---

### Diapositiva 7: Importancia de Variables en XGBoost (Feature Importance)
*   **Contenido Visual:**
    *   Gráfico de barras de importancia de variables del modelo XGBoost.
    *   Llamada visual destacando a la velocidad del viento y la memoria climática.
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
