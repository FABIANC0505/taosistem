import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base


class OrderStatus(str, enum.Enum):
    PENDIENTE = "pendiente"
    EN_PREPARACION = "en_preparacion"
    LISTO = "listo"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"


class Order(Base):
    __tablename__ = "orders"

    id:                 Mapped[str]         = mapped_column(String(36), primary_key=True,
                                                            default=lambda: str(uuid.uuid4()))
    id_mesero:          Mapped[str]         = mapped_column(String(36),
                                                            ForeignKey("users.id"), nullable=False)
    mesa_numero:        Mapped[int]         = mapped_column(Integer, nullable=False)
    status:             Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus),
                                                            default=OrderStatus.PENDIENTE)
    items:              Mapped[dict]        = mapped_column(JSONB, nullable=False)
    notas:              Mapped[str]         = mapped_column(Text, nullable=True)
    total_amount:       Mapped[float]       = mapped_column(Numeric(10, 2), nullable=False)

    # 4 timestamps del ciclo de vida del pedido (RF9)
    created_at:         Mapped[datetime]    = mapped_column(DateTime(timezone=True),
                                                            server_default=func.now())
    cocinando_at:       Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    served_at:          Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    entregado_at:       Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Cancelación (RF14)
    cancelado_at:       Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelado_por:      Mapped[str]         = mapped_column(String(36),
                                                            ForeignKey("users.id"), nullable=True)
    motivo_cancelacion: Mapped[str]         = mapped_column(Text, nullable=True)