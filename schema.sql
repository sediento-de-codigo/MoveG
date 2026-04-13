-- Creación de la base de datos (si no existe)
CREATE DATABASE IF NOT EXISTS movilgroup;
USE movilgroup;

-- 1. Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    rol ENUM('pasajero', 'conductor', 'admin') DEFAULT 'pasajero',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Tabla de Vehículos (Incluye los "Extras" acordados)
CREATE TABLE IF NOT EXISTS vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conductor_id INT,
    modelo VARCHAR(50) NOT NULL,
    placa VARCHAR(20) UNIQUE NOT NULL,
    capacidad_total INT DEFAULT 12,
    aire_acondicionado BOOLEAN DEFAULT FALSE,
    musica_ambiental BOOLEAN DEFAULT FALSE,
    categoria ENUM('Estándar', 'Confort', 'Elite') DEFAULT 'Estándar',
    FOREIGN KEY (conductor_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 3. Tabla de Solicitudes (El corazón de MoveG)
CREATE TABLE IF NOT EXISTS solicitudes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo_servicio ENUM('Express', 'Nodo') NOT NULL,
    cantidad_asientos INT DEFAULT 1, -- Aquí se maneja si paga 2 asientos
    
    -- Ubicación de Inicio (Real)
    lat_inicio DECIMAL(10, 8) NOT NULL,
    lng_inicio DECIMAL(11, 8) NOT NULL,
    
    -- Nodo de Encuentro (Sugerido por la App o acordado)
    lat_nodo DECIMAL(10, 8),
    lng_nodo DECIMAL(11, 8),
    
    -- Destino Final
    direccion_destino VARCHAR(255),
    lat_destino DECIMAL(10, 8),
    lng_destino DECIMAL(11, 8),
    
    estatus ENUM('pendiente', 'buscando', 'asignado', 'en_ruta', 'completado', 'cancelado') DEFAULT 'pendiente',
    precio_estimado DECIMAL(10, 2),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;