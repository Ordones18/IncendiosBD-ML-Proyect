-- =========================================================================
-- Proyecto de Investigación Formativa: Predicción de Incendios Forestales
-- Fase 3: Seguridad y Roles de Usuario
-- Archivo: 04_roles_permisos.sql
-- =========================================================================

USE IncendiosForestalesEC;
GO

-- =========================================================================
-- 1. CREACIÓN DE ROLES DE BASE DE DATOS
-- =========================================================================

IF DATABASE_PRINCIPAL_ID('rol_analista') IS NULL
BEGIN
    CREATE ROLE rol_analista;
END
GO

IF DATABASE_PRINCIPAL_ID('rol_admin') IS NULL
BEGIN
    CREATE ROLE rol_admin;
END
GO

-- =========================================================================
-- 2. ASIGNACIÓN DE PERMISOS A LOS ROLES
-- =========================================================================

-- El Analista de Datos solo debe ver vistas consolidadas, no las tablas base directo
GRANT SELECT ON vw_DatosUnificados TO rol_analista;
GRANT SELECT ON vw_ResumenMensualCiudad TO rol_analista;
GRANT SELECT ON vw_RiesgoActual TO rol_analista;
GRANT SELECT ON vw_HistoricoIncendios TO rol_analista;

-- El Administrador tiene control total para manipulación de datos y esquema
GRANT SELECT, INSERT, UPDATE, DELETE ON Ciudades TO rol_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON Incendios TO rol_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON Clima TO rol_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON NDVI TO rol_admin;
GRANT SELECT ON Auditoria TO rol_admin;
GRANT SELECT ON vw_DatosUnificados TO rol_admin;
GRANT SELECT ON vw_ResumenMensualCiudad TO rol_admin;
GRANT SELECT ON vw_RiesgoActual TO rol_admin;
GRANT SELECT ON vw_HistoricoIncendios TO rol_admin;

-- Permisos de backup para el Administrador (necesarios para el DRP)
GRANT BACKUP DATABASE TO rol_admin;
GRANT BACKUP LOG TO rol_admin;
GO


-- =========================================================================
-- 3. CREACIÓN DE LOGINS (NIVEL SERVIDOR) Y USUARIOS (NIVEL BASE DE DATOS)
-- Para demostrar y probar el funcionamiento del control de accesos.
-- =========================================================================

USE master;
GO

-- Eliminar logins de prueba si ya existen para crearlos de nuevo limpios
IF EXISTS (SELECT * FROM sys.server_principals WHERE name = 'user_analista_test')
    DROP LOGIN user_analista_test;
    
IF EXISTS (SELECT * FROM sys.server_principals WHERE name = 'user_admin_test')
    DROP LOGIN user_admin_test;
GO

-- Crear logins con contraseñas seguras
CREATE LOGIN user_analista_test WITH PASSWORD = 'AnalistaPassword2026*', DEFAULT_DATABASE = IncendiosForestalesEC;
CREATE LOGIN user_admin_test WITH PASSWORD = 'AdminPassword2026*', DEFAULT_DATABASE = IncendiosForestalesEC;
GO

USE IncendiosForestalesEC;
GO

-- Eliminar usuarios de prueba si ya existen
IF EXISTS (SELECT * FROM sys.database_principals WHERE name = 'user_analista_test')
    DROP USER user_analista_test;

IF EXISTS (SELECT * FROM sys.database_principals WHERE name = 'user_admin_test')
    DROP USER user_admin_test;
GO

-- Crear usuarios vinculados a los logins en la base de datos
CREATE USER user_analista_test FOR LOGIN user_analista_test;
CREATE USER user_admin_test FOR LOGIN user_admin_test;
GO

-- Asignar los usuarios a sus respectivos roles
ALTER ROLE rol_analista ADD MEMBER user_analista_test;
ALTER ROLE rol_admin ADD MEMBER user_admin_test;
GO

-- =========================================================================
-- 4. CONSULTA DE VERIFICACIÓN
-- =========================================================================
SELECT 
    DP1.name AS Rol,
    DP2.name AS Miembro
FROM sys.database_role_members DRM
INNER JOIN sys.database_principals DP1 ON DRM.role_principal_id = DP1.principal_id
INNER JOIN sys.database_principals DP2 ON DRM.member_principal_id = DP2.principal_id
WHERE DP1.name IN ('rol_analista', 'rol_admin');
GO
