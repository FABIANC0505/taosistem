CREATE DATABASE IF NOT EXISTS bdtaosistem CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bdtaosistem;

CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(36) PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(200) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  rol VARCHAR(20) NOT NULL,
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_users_email (email)
);

CREATE TABLE IF NOT EXISTS products (
  id VARCHAR(36) PRIMARY KEY,
  nombre VARCHAR(200) NOT NULL,
  precio DECIMAL(10,2) NOT NULL,
  descripcion TEXT NULL,
  imagen_url VARCHAR(500) NULL,
  categoria VARCHAR(100) NOT NULL,
  disponible BOOLEAN NOT NULL DEFAULT TRUE,
  agotado_por VARCHAR(36) NULL,
  agotado_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_products_agotado_por FOREIGN KEY (agotado_por) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS app_settings (
  `key` VARCHAR(100) PRIMARY KEY,
  value VARCHAR(255) NOT NULL,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO app_settings (`key`, value)
VALUES ('total_mesas', '12')
ON DUPLICATE KEY UPDATE value = VALUES(value);

CREATE TABLE IF NOT EXISTS orders (
  id VARCHAR(36) PRIMARY KEY,
  id_mesero VARCHAR(36) NOT NULL,
  mesa_numero INT NULL,
  tipo_pedido VARCHAR(20) NOT NULL DEFAULT 'mesa',
  cliente_nombre VARCHAR(150) NULL,
  cliente_telefono VARCHAR(30) NULL,
  direccion_entrega TEXT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'pendiente',
  items JSON NOT NULL,
  notas TEXT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  cocinando_at DATETIME NULL,
  served_at DATETIME NULL,
  entregado_at DATETIME NULL,
  cancelado_at DATETIME NULL,
  cancelado_por VARCHAR(36) NULL,
  motivo_cancelacion TEXT NULL,
  CONSTRAINT fk_orders_mesero FOREIGN KEY (id_mesero) REFERENCES users(id),
  CONSTRAINT fk_orders_cancelado_por FOREIGN KEY (cancelado_por) REFERENCES users(id),
  INDEX idx_orders_mesero (id_mesero),
  INDEX idx_orders_status (status),
  INDEX idx_orders_created_at (created_at),
  INDEX idx_orders_entregado_at (entregado_at)
);

CREATE TABLE IF NOT EXISTS cash_sessions (
  id VARCHAR(36) PRIMARY KEY,
  cashier_user_id VARCHAR(36) NOT NULL,
  opening_amount DECIMAL(10,2) NOT NULL,
  opening_note TEXT NULL,
  opened_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  closing_counted_amount DECIMAL(10,2) NULL,
  closing_note TEXT NULL,
  closed_at DATETIME NULL,
  CONSTRAINT fk_cash_sessions_cashier FOREIGN KEY (cashier_user_id) REFERENCES users(id),
  INDEX idx_cash_sessions_cashier (cashier_user_id),
  INDEX idx_cash_sessions_opened_at (opened_at)
);

CREATE TABLE IF NOT EXISTS cash_movements (
  id VARCHAR(36) PRIMARY KEY,
  session_id VARCHAR(36) NOT NULL,
  cashier_user_id VARCHAR(36) NOT NULL,
  movement_type VARCHAR(30) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  description TEXT NOT NULL,
  related_order_id VARCHAR(36) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_cash_movements_session FOREIGN KEY (session_id) REFERENCES cash_sessions(id),
  CONSTRAINT fk_cash_movements_cashier FOREIGN KEY (cashier_user_id) REFERENCES users(id),
  CONSTRAINT fk_cash_movements_order FOREIGN KEY (related_order_id) REFERENCES orders(id),
  INDEX idx_cash_movements_session (session_id),
  INDEX idx_cash_movements_cashier (cashier_user_id),
  INDEX idx_cash_movements_created_at (created_at)
);

CREATE TABLE IF NOT EXISTS cash_payments (
  id VARCHAR(36) PRIMARY KEY,
  session_id VARCHAR(36) NOT NULL,
  cashier_user_id VARCHAR(36) NOT NULL,
  order_id VARCHAR(36) NULL,
  mesa_numero INT NULL,
  payment_method VARCHAR(30) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  reference_note TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_cash_payments_session FOREIGN KEY (session_id) REFERENCES cash_sessions(id),
  CONSTRAINT fk_cash_payments_cashier FOREIGN KEY (cashier_user_id) REFERENCES users(id),
  CONSTRAINT fk_cash_payments_order FOREIGN KEY (order_id) REFERENCES orders(id),
  INDEX idx_cash_payments_session (session_id),
  INDEX idx_cash_payments_cashier (cashier_user_id),
  INDEX idx_cash_payments_order (order_id),
  INDEX idx_cash_payments_mesa (mesa_numero),
  INDEX idx_cash_payments_created_at (created_at)
);

CREATE TABLE IF NOT EXISTS waiter_alerts (
  id VARCHAR(36) PRIMARY KEY,
  mesa_numero INT NOT NULL,
  cashier_user_id VARCHAR(36) NOT NULL,
  mesero_user_id VARCHAR(36) NULL,
  message TEXT NOT NULL,
  resolved BOOLEAN NOT NULL DEFAULT FALSE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  resolved_at DATETIME NULL,
  CONSTRAINT fk_waiter_alerts_cashier FOREIGN KEY (cashier_user_id) REFERENCES users(id),
  CONSTRAINT fk_waiter_alerts_mesero FOREIGN KEY (mesero_user_id) REFERENCES users(id),
  INDEX idx_waiter_alerts_mesa (mesa_numero),
  INDEX idx_waiter_alerts_mesero (mesero_user_id),
  INDEX idx_waiter_alerts_resolved (resolved)
);
