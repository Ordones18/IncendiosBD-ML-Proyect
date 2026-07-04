-- =========================================================================
-- Proyecto de Investigación Formativa: Predicción de Incendios Forestales
-- Fase 2: Diseño e Implementación de la Base de Datos SQL Server
-- Archivo: 02_indices_vistas.sql
-- =========================================================================

USE IncendiosForestalesEC;
GO

-- =========================================================================
-- 1. CREACIÓN DE ÍNDICES NO AGRUPADOS (NON-CLUSTERED INDEXES)
-- Para acelerar las búsquedas por fecha y relaciones entre tablas
-- =========================================================================

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Incendios_Fecha' AND object_id = OBJECT_ID('Incendios'))
    DROP INDEX IX_Incendios_Fecha ON Incendios;
CREATE NONCLUSTERED INDEX IX_Incendios_Fecha ON Incendios(fecha_deteccion);
GO

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Incendios_Ciudad' AND object_id = OBJECT_ID('Incendios'))
    DROP INDEX IX_Incendios_Ciudad ON Incendios;
CREATE NONCLUSTERED INDEX IX_Incendios_Ciudad ON Incendios(id_ciudad);
GO

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Clima_Ciudad_Fecha' AND object_id = OBJECT_ID('Clima'))
    DROP INDEX IX_Clima_Ciudad_Fecha ON Clima;
CREATE NONCLUSTERED INDEX IX_Clima_Ciudad_Fecha ON Clima(id_ciudad, fecha);
GO

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_NDVI_Ciudad_Fecha' AND object_id = OBJECT_ID('NDVI'))
    DROP INDEX IX_NDVI_Ciudad_Fecha ON NDVI;
CREATE NONCLUSTERED INDEX IX_NDVI_Ciudad_Fecha ON NDVI(id_ciudad, fecha);
GO


-- =========================================================================
-- 2. CREACIÓN DE VISTAS ANALÍTICAS
-- =========================================================================

-- Vista 1: vw_DatosUnificados (Estructura principal para entrenamiento de ML)
-- Une el clima diario con los incendios agregados por día y el NDVI más reciente
IF OBJECT_ID('vw_DatosUnificados', 'V') IS NOT NULL
    DROP VIEW vw_DatosUnificados;
GO

CREATE VIEW vw_DatosUnificados AS
SELECT 
    cli.id_clima,
    cli.id_ciudad,
    ciu.nombre AS ciudad_nombre,
    ciu.region AS ciudad_region,
    ciu.latitud AS ciudad_latitud,
    ciu.longitud AS ciudad_longitud,
    ciu.altitud_msnm,
    cli.fecha,
    cli.velocidad_viento,
    cli.direccion_viento,
    cli.temperatura_media,
    cli.temperatura_max,
    cli.temperatura_min,
    cli.humedad_relativa,
    cli.precipitacion,
    -- Traemos el NDVI más reciente disponible para esa ciudad en esa fecha (as-of join)
    ISNULL(nd.ndvi, 0.4) AS ndvi, -- Valor por defecto neutral si no hay mediciones previas
    ISNULL(nd.evi, 0.2) AS evi,
    ISNULL(f.conteo_incendios, 0) AS conteo_incendios,
    ISNULL(f.max_brightness, 0.0) AS max_brightness,
    ISNULL(f.max_frp, 0.0) AS max_frp,
    CASE WHEN f.conteo_incendios > 0 THEN 1 ELSE 0 END AS incendio_binario
FROM Clima cli
JOIN Ciudades ciu ON cli.id_ciudad = ciu.id_ciudad
OUTER APPLY (
    SELECT TOP 1 n.ndvi, n.evi
    FROM NDVI n
    WHERE n.id_ciudad = cli.id_ciudad
      AND n.fecha <= cli.fecha
    ORDER BY n.fecha DESC
) nd
OUTER APPLY (
    SELECT 
        COUNT(*) AS conteo_incendios,
        MAX(inc.brightness) AS max_brightness,
        MAX(inc.frp) AS max_frp
    FROM Incendios inc
    WHERE inc.id_ciudad = cli.id_ciudad
      AND inc.fecha_deteccion = cli.fecha
    GROUP BY inc.id_ciudad, inc.fecha_deteccion
) f;
GO


-- Vista 2: vw_ResumenMensualCiudad (Reporte agregado para análisis temporal y visualizaciones)
IF OBJECT_ID('vw_ResumenMensualCiudad', 'V') IS NOT NULL
    DROP VIEW vw_ResumenMensualCiudad;
GO

CREATE VIEW vw_ResumenMensualCiudad AS
SELECT 
    ciu.nombre AS ciudad_nombre,
    YEAR(cli.fecha) AS anio,
    MONTH(cli.fecha) AS mes,
    AVG(cli.temperatura_media) AS temp_promedio,
    AVG(cli.humedad_relativa) AS humedad_promedio,
    AVG(cli.velocidad_viento) AS viento_promedio,
    SUM(cli.precipitacion) AS precipitacion_total,
    AVG(ISNULL(nd.ndvi, 0.4)) AS ndvi_promedio,
    COUNT(inc.id_incendio) AS total_incendios,
    AVG(inc.frp) AS frp_promedio_incendios
FROM Clima cli
JOIN Ciudades ciu ON cli.id_ciudad = ciu.id_ciudad
LEFT JOIN Incendios inc ON cli.id_ciudad = inc.id_ciudad AND cli.fecha = inc.fecha_deteccion
OUTER APPLY (
    SELECT TOP 1 n.ndvi
    FROM NDVI n
    WHERE n.id_ciudad = cli.id_ciudad
      AND n.fecha <= cli.fecha
    ORDER BY n.fecha DESC
) nd
GROUP BY ciu.nombre, YEAR(cli.fecha), MONTH(cli.fecha);
GO


-- Vista 3: vw_RiesgoActual (Condiciones meteorológicas más recientes de cada ciudad)
IF OBJECT_ID('vw_RiesgoActual', 'V') IS NOT NULL
    DROP VIEW vw_RiesgoActual;
GO

CREATE VIEW vw_RiesgoActual AS
WITH UltimoClima AS (
    SELECT 
        id_ciudad,
        fecha,
        velocidad_viento,
        direccion_viento,
        temperatura_media,
        temperatura_max,
        temperatura_min,
        humedad_relativa,
        precipitacion,
        ROW_NUMBER() OVER (PARTITION BY id_ciudad ORDER BY fecha DESC) as rn
    FROM Clima
)
SELECT 
    ciu.id_ciudad,
    ciu.nombre AS ciudad_nombre,
    uc.fecha AS ultima_fecha_clima,
    uc.temperatura_media,
    uc.humedad_relativa,
    uc.velocidad_viento,
    uc.precipitacion,
    ISNULL(nd.ndvi, 0.0) AS ndvi_actual,
    (SELECT COUNT(*) FROM Incendios i WHERE i.id_ciudad = ciu.id_ciudad AND i.fecha_deteccion >= DATEADD(day, -30, uc.fecha)) AS incendios_ultimos_30_dias
FROM Ciudades ciu
JOIN UltimoClima uc ON ciu.id_ciudad = uc.id_ciudad AND uc.rn = 1
OUTER APPLY (
    SELECT TOP 1 n.ndvi
    FROM NDVI n
    WHERE n.id_ciudad = ciu.id_ciudad
      AND n.fecha <= uc.fecha
    ORDER BY n.fecha DESC
) nd;
GO

-- Vista 4: vw_HistoricoIncendios (Focos históricos de incendios con relación a ciudades)
IF OBJECT_ID('vw_HistoricoIncendios', 'V') IS NOT NULL
    DROP VIEW vw_HistoricoIncendios;
GO

CREATE VIEW vw_HistoricoIncendios AS
SELECT 
    i.latitud,
    i.longitud,
    i.confianza,
    i.frp,
    i.fecha_deteccion,
    i.satelite,
    i.id_ciudad,
    c.nombre AS ciudad_nombre,
    c.region AS ciudad_region
FROM Incendios i
JOIN Ciudades c ON i.id_ciudad = c.id_ciudad;
GO
