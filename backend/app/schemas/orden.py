from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from app.models.orden import OrderStatus


class OrderItemSchema(BaseModel):
    product_id: str
    nombre: str
    cantidad: int = Field(..., ge=1)
    precio_unitario: float = Field(..., gt=0)
    subtotal: Optional[float] = None

    @model_validator(mode="after")
    def ensure_subtotal(self):
        self.subtotal = round(float(self.cantidad) * float(self.precio_unitario), 2)
        return self


class CrearPedidoSchema(BaseModel):
    mesa_numero: int = Field(..., ge=1, le=300)
    items: list[OrderItemSchema] = Field(..., min_length=1)
    notas: Optional[str] = None


class ActualizarPedidoSchema(BaseModel):
    mesa_numero: Optional[int] = Field(None, ge=1, le=300)
    items: Optional[list[OrderItemSchema]] = Field(None, min_length=1)
    notas: Optional[str] = None


class ActualizarEstadoSchema(BaseModel):
    status: OrderStatus


class CancelarPedidoSchema(BaseModel):
    motivo_cancelacion: Optional[str] = None


class PedidoResponseSchema(BaseModel):
    id: str
    id_mesero: str
    mesa_numero: int
    status: OrderStatus
    items: list[OrderItemSchema]
    notas: Optional[str] = None
    total_amount: float
    created_at: Optional[datetime] = None
    cocinando_at: Optional[datetime] = None
    served_at: Optional[datetime] = None
    entregado_at: Optional[datetime] = None
    cancelado_at: Optional[datetime] = None
    cancelado_por: Optional[str] = None
    motivo_cancelacion: Optional[str] = None

    class Config:
        from_attributes = True