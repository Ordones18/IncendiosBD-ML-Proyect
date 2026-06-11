-- =========================================================================
-- Proyecto de Investigación Formativa: Predicción de Incendios Forestales
-- Fase 2: Diseño e Implementación de la Base de Datos SQL Server
-- Archivo: 01_crear_base_datos.sql
-- =========================================================================

USE master;
GO

-- Dropear la base de datos si existe para recrearla limpiamente
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'IncendiosForestalesEC')
BEGIN
    ALTER DATABASE IncendiosForestalesEC SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE IncendiosForestalesEC;
END
GO

CREATE DATABASE IncendiosForestalesEC;
GO

USE IncendiosForestalesEC;
GO

-- 1. Tabla de Ciudades (Dimensión)
CREATE TABLE Ciudades (
    id_ciudad INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    region VARCHAR(50) NOT NULL,
    latitud FLOAT NOT NULL,
    longitud FLOAT NOT NULL,
    altitud_msnm FLOAT NOT NULL
);
GO

-- 2. Tabla de Incendios (Hechos - Histórico de NASA FIRMS)
CREATE TABLE Incendios (
    id_incendio INT IDENTITY(1,1) PRIMARY KEY,
    id_ciudad INT NOT NULL,
    latitud FLOAT NOT NULL,
    longitud FLOAT NOT NULL,
    brightness FLOAT NOT NULL,
    scan FLOAT NOT NULL,
    track FLOAT NOT NULL,
    fecha_deteccion DATE NOT NULL,
    hora_deteccion INT NOT NULL, -- Formato HHMM
    satelite VARCHAR(50) NOT NULL,
    instrumento VARCHAR(50) NOT NULL,
    confianza INT NOT NULL,
    version VARCHAR(50) NOT NULL,
    bright_t31 FLOAT NOT NULL,
    frp FLOAT NOT NULL,
    dia_noche CHAR(1) NOT NULL,
    tipo INT NOT NULL,
    CONSTRAINT FK_Incendios_Ciudades FOREIGN KEY (id_ciudad) REFERENCES Ciudades(id_ciudad),
    CONSTRAINT CHK_Incendios_Confianza CHECK (confianza BETWEEN 0 AND 100),
    CONSTRAINT CHK_Incendios_DiaNoche CHECK (dia_noche IN ('D', 'N'))
);
GO

-- 3. Tabla de Variables Climáticas Diarias (NASA POWER)
CREATE TABLE Clima (
    id_clima INT IDENTITY(1,1) PRIMARY KEY,
    id_ciudad INT NOT NULL,
    fecha DATE NOT NULL,
    velocidad_viento FLOAT NOT NULL,     -- WS10M (m/s)
    direccion_viento FLOAT NOT NULL,     -- WD10M (grados)
    temperatura_media FLOAT NOT NULL,    -- T2M (Celsius)
    temperatura_max FLOAT NOT NULL,      -- T2M_MAX (Celsius)
    temperatura_min FLOAT NOT NULL,      -- T2M_MIN (Celsius)
    humedad_relativa FLOAT NOT NULL,     -- RH2M (%)
    precipitacion FLOAT NOT NULL,        -- PRECTOTCORR (mm/día)
    CONSTRAINT FK_Clima_Ciudades FOREIGN KEY (id_ciudad) REFERENCES Ciudades(id_ciudad),
    CONSTRAINT UQ_Clima_Ciudad_Fecha UNIQUE (id_ciudad, fecha)
);
GO

-- 4. Tabla de Vegetación e Índices NDVI (MODIS MOD13Q1)
CREATE TABLE NDVI (
    id_ndvi INT IDENTITY(1,1) PRIMARY KEY,
    id_ciudad INT NOT NULL,
    fecha DATE NOT NULL,
    ndvi FLOAT NOT NULL,                 -- NDVI index
    evi FLOAT NULL,                      -- EVI index (opcional)
    vi_quality INT NOT NULL,             -- Calidad de píxel
    pixel_reliability INT NOT NULL,      -- Confiabilidad del píxel
    modis_tile VARCHAR(50) NOT NULL,
    CONSTRAINT FK_NDVI_Ciudades FOREIGN KEY (id_ciudad) REFERENCES Ciudades(id_ciudad),
    CONSTRAINT UQ_NDVI_Ciudad_Fecha UNIQUE (id_ciudad, fecha),
    CONSTRAINT CHK_NDVI_Valor CHECK (ndvi BETWEEN -1.0 AND 1.0),
    CONSTRAINT CHK_EVI_Valor CHECK (evi IS NULL OR (evi BETWEEN -1.0 AND 1.0))
);
GO

-- 5. Tabla de Auditoría (Para monitoreo de cambios)
CREATE TABLE Auditoria (
    id_auditoria INT IDENTITY(1,1) PRIMARY KEY,
    tabla_afectada VARCHAR(100) NOT NULL,
    operacion VARCHAR(50) NOT NULL,      -- INSERT, UPDATE, DELETE
    fecha_hora DATETIME DEFAULT GETDATE() NOT NULL,
    usuario VARCHAR(100) DEFAULT SYSTEM_USER NOT NULL,
    datos_anteriores NVARCHAR(MAX) NULL, -- Guardado en formato JSON
    datos_nuevos NVARCHAR(MAX) NULL      -- Guardado en formato JSON
);
GO
