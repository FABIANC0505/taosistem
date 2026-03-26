CREATE DATABASE taosistem_db;
USE taosistem_db;
CREATE TABLE usuarios (
    id CHAR(36) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol ENUM('admin', 'mesero', 'cocina') NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE productos (
    id CHAR(36) PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
    descripcion TEXT,
    imagen_url TEXT,
    categoria VARCHAR(100) NOT NULL,
    disponible BOOLEAN NOT NULL DEFAULT TRUE,
    agotado_por CHAR(36),
    agotado_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agotado_por) REFERENCES users(id)
);
CREATE TABLE ordenes (
    id CHAR(36) PRIMARY KEY,
    id_mesero CHAR(36) NOT NULL,
    mesa_numero INT NOT NULL CHECK (mesa_numero >= 1),
    
    status ENUM('Pendiente', 'En preparacion', 'Listo', 'Entregado', 'Cancelado') NOT NULL,
    
    items JSON NOT NULL,
    notas TEXT,
    
    total_amount DECIMAL(10,2) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cocinando_at TIMESTAMP NULL,
    served_at TIMESTAMP NULL,
    entregado_at TIMESTAMP NULL,
    
    cancelado_at TIMESTAMP NULL,
    cancelado_por CHAR(36),
    motivo_cancelacion TEXT,
    
    FOREIGN KEY (id_mesero) REFERENCES users(id),
    FOREIGN KEY (cancelado_por) REFERENCES users(id)
);
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36),
    accion VARCHAR(255) NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);
