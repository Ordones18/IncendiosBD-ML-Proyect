-- =========================================================================
-- Proyecto de Investigación Formativa: Predicción de Incendios Forestales
-- Fase 3: Seguridad y Auditoría (Triggers de Auditoría)
-- Archivo: 03_triggers_auditoria.sql
-- =========================================================================

USE IncendiosForestalesEC;
GO

-- 1. Trigger de Auditoría para la tabla Incendios
IF OBJECT_ID('trg_Incendios_Audit', 'TR') IS NOT NULL
    DROP TRIGGER trg_Incendios_Audit;
GO

CREATE TRIGGER trg_Incendios_Audit
ON Incendios
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @operacion VARCHAR(50);
    DECLARE @datos_anteriores NVARCHAR(MAX) = NULL;
    DECLARE @datos_nuevos NVARCHAR(MAX) = NULL;

    -- Determinar el tipo de operación
    IF EXISTS(SELECT 1 FROM inserted) AND EXISTS(SELECT 1 FROM deleted)
        SET @operacion = 'UPDATE';
    ELSE IF EXISTS(SELECT 1 FROM inserted)
        SET @operacion = 'INSERT';
    ELSE IF EXISTS(SELECT 1 FROM deleted)
        SET @operacion = 'DELETE';
    ELSE
        RETURN; -- Si no hay registros afectados, terminar

    -- Capturar datos anteriores (deleted) para UPDATE o DELETE
    IF @operacion IN ('UPDATE', 'DELETE')
    BEGIN
        SET @datos_anteriores = (
            SELECT 
                id_incendio, id_ciudad, latitud, longitud, brightness, 
                scan, track, fecha_deteccion, hora_deteccion, satelite, 
                instrumento, confianza, version, bright_t31, frp, dia_noche, tipo
            FROM deleted
            FOR JSON PATH
        );
    END

    -- Capturar datos nuevos (inserted) para INSERT o UPDATE
    IF @operacion IN ('INSERT', 'UPDATE')
    BEGIN
        SET @datos_nuevos = (
            SELECT 
                id_incendio, id_ciudad, latitud, longitud, brightness, 
                scan, track, fecha_deteccion, hora_deteccion, satelite, 
                instrumento, confianza, version, bright_t31, frp, dia_noche, tipo
            FROM inserted
            FOR JSON PATH
        );
    END

    -- Insertar en la tabla de Auditoría
    INSERT INTO Auditoria (tabla_afectada, operacion, fecha_hora, usuario, datos_anteriores, datos_nuevos)
    VALUES ('Incendios', @operacion, GETDATE(), SYSTEM_USER, @datos_anteriores, @datos_nuevos);
END;
GO


-- 2. Trigger de Auditoría para la tabla Clima
IF OBJECT_ID('trg_Clima_Audit', 'TR') IS NOT NULL
    DROP TRIGGER trg_Clima_Audit;
GO

CREATE TRIGGER trg_Clima_Audit
ON Clima
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @operacion VARCHAR(50);
    DECLARE @datos_anteriores NVARCHAR(MAX) = NULL;
    DECLARE @datos_nuevos NVARCHAR(MAX) = NULL;

    -- Determinar el tipo de operación
    IF EXISTS(SELECT 1 FROM inserted) AND EXISTS(SELECT 1 FROM deleted)
        SET @operacion = 'UPDATE';
    ELSE IF EXISTS(SELECT 1 FROM inserted)
        SET @operacion = 'INSERT';
    ELSE IF EXISTS(SELECT 1 FROM deleted)
        SET @operacion = 'DELETE';
    ELSE
        RETURN;

    -- Capturar datos anteriores para UPDATE o DELETE
    IF @operacion IN ('UPDATE', 'DELETE')
    BEGIN
        SET @datos_anteriores = (
            SELECT 
                id_clima, id_ciudad, fecha, velocidad_viento, direccion_viento, 
                temperatura_media, temperatura_max, temperatura_min, humedad_relativa, precipitacion
            FROM deleted
            FOR JSON PATH
        );
    END

    -- Capturar datos nuevos para INSERT o UPDATE
    IF @operacion IN ('INSERT', 'UPDATE')
    BEGIN
        SET @datos_nuevos = (
            SELECT 
                id_clima, id_ciudad, fecha, velocidad_viento, direccion_viento, 
                temperatura_media, temperatura_max, temperatura_min, humedad_relativa, precipitacion
            FROM inserted
            FOR JSON PATH
        );
    END

    -- Insertar en la tabla de Auditoría
    INSERT INTO Auditoria (tabla_afectada, operacion, fecha_hora, usuario, datos_anteriores, datos_nuevos)
    VALUES ('Clima', @operacion, GETDATE(), SYSTEM_USER, @datos_anteriores, @datos_nuevos);
END;
GO
