-- =========================================================================
-- Proyecto de Investigación Formativa: Predicción de Incendios Forestales
-- Fase 3: Plan de Recuperación ante Desastres (DRP) y Respaldos
-- Archivo: 05_drp_backups.sql
-- =========================================================================

-- NOTA: Este script requiere permisos de administrador (sysadmin) en SQL Server.
-- Las rutas de respaldo se guardan por defecto en 'C:\Users\Public\' para asegurar
-- que el servicio de SQL Server (MSSQLSERVER) tenga permisos de escritura.

USE master;
GO

-- =========================================================================
-- 1. CONFIGURACIÓN DEL MODELO DE RECUPERACIÓN (FULL RECOVERY MODEL)
-- Esto permite copias de seguridad de registros de transacciones (Point-in-Time)
-- =========================================================================
ALTER DATABASE IncendiosForestalesEC SET RECOVERY FULL;
GO

-- =========================================================================
-- 2. GENERACIÓN DE COPIAS DE SEGURIDAD (BACKUPS)
-- =========================================================================

-- A. Copia de Seguridad Completa (Full Backup)
PRINT 'Iniciando copia de seguridad COMPLETA...';
BACKUP DATABASE IncendiosForestalesEC
TO DISK = 'C:\Users\Public\IncendiosForestalesEC_Full.bak'
WITH FORMAT,
     MEDIANAME = 'SQLServerBackups',
     NAME = 'Backup Completo de IncendiosForestalesEC',
     STATS = 10;
GO

-- B. Copia de Seguridad Diferencial (Differential Backup)
-- (Se ejecuta después de que hayan ocurrido cambios menores)
PRINT 'Iniciando copia de seguridad DIFERENCIAL...';
BACKUP DATABASE IncendiosForestalesEC
TO DISK = 'C:\Users\Public\IncendiosForestalesEC_Diff.bak'
WITH DIFFERENTIAL,
     FORMAT,
     NAME = 'Backup Diferencial de IncendiosForestalesEC',
     STATS = 10;
GO

-- C. Copia de Seguridad del Log de Transacciones (Transaction Log Backup)
-- (Permite restaurar hasta el último segundo antes de un fallo)
PRINT 'Iniciando copia de seguridad del LOG de transacciones...';
BACKUP LOG IncendiosForestalesEC
TO DISK = 'C:\Users\Public\IncendiosForestalesEC_Log.bak'
WITH FORMAT,
     NAME = 'Backup del Log de IncendiosForestalesEC',
     STATS = 10;
GO


-- =========================================================================
-- 3. SIMULACIÓN DE DESASTRE Y FALLO CRÍTICO (SIMULACIÓN DRP)
-- ADVERTENCIA: Este bloque destruirá la base de datos para simular una pérdida total
-- =========================================================================

/*
-- Ejecutar estas líneas para simular el fallo de pérdida total:
USE master;
GO
ALTER DATABASE IncendiosForestalesEC SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
DROP DATABASE IncendiosForestalesEC;
GO
-- Si intentas hacer SELECT en las tablas, fallará porque la base de datos ya no existe.
*/


-- =========================================================================
-- 4. PROCESO DE RESTAURACIÓN PASO A PASO (RECUPERACIÓN ANTE DESASTRE)
-- =========================================================================

/*
-- Para recuperar la base de datos, ejecuta la siguiente secuencia en master:

USE master;
GO

-- Paso A: Restaurar el Backup Completo (con NORECOVERY para permitir aplicar backups posteriores)
RESTORE DATABASE IncendiosForestalesEC
FROM DISK = 'C:\Users\Public\IncendiosForestalesEC_Full.bak'
WITH NORECOVERY, REPLACE;
GO

-- Paso B: Restaurar el Backup Diferencial (opcional si existe, también con NORECOVERY)
RESTORE DATABASE IncendiosForestalesEC
FROM DISK = 'C:\Users\Public\IncendiosForestalesEC_Diff.bak'
WITH NORECOVERY;
GO

-- Paso C: Restaurar el Backup del Log de Transacciones (con RECOVERY para finalizar y abrir la BD)
RESTORE DATABASE IncendiosForestalesEC
FROM DISK = 'C:\Users\Public\IncendiosForestalesEC_Log.bak'
WITH RECOVERY;
GO

-- Paso D: Verificar que la base de datos esté activa y con datos
USE IncendiosForestalesEC;
GO
SELECT COUNT(*) AS total_ciudades FROM Ciudades;
SELECT COUNT(*) AS total_incendios FROM Incendios;
GO
*/
