# Importar todos los modelos para que Alembic los detecte automáticamente
from app.models.user import User, UserRole
from app.models.producto import Product
from app.models.orden import Order, OrderStatus
from app.models.app_setting import AppSetting
from app.models.cashier import CashSession, CashMovement, CashMovementType, CashPayment, PaymentMethod, WaiterAlert

__all__ = [
    "User",
    "UserRole",
    "Product",
    "Order",
    "OrderStatus",
    "AppSetting",
    "CashSession",
    "CashMovement",
    "CashMovementType",
    "CashPayment",
    "PaymentMethod",
    "WaiterAlert",
]
