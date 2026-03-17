# Importar todos los modelos para que Alembic los detecte automáticamente
from app.models.user import User, UserRole
from app.models.producto import Product
from app.models.orden import Order, OrderStatus
from app.models.audit_log import AuditLog

__all__ = ["User", "UserRole", "Product", "Order", "OrderStatus", "AuditLog"]