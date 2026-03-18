from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_token
from app.models.orden import Order, OrderStatus
from app.models.user import User, UserRole
from app.services.history_settings import (
    cleanup_expired_dispatched_orders,
    get_history_retention_days,
    get_orders_history,
)
from app.schemas.orden import (
    ActualizarEstadoSchema,
    ActualizarPedidoSchema,
    CancelarPedidoSchema,
    CrearPedidoSchema,
    OrderHistoryResponseSchema,
    PedidoResponseSchema,
    TipoPedido,
)

router = APIRouter(prefix="/orders", tags=["orders"])


async def get_current_user(
    authorization: str = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado o inválido",
        )

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    return user


def order_to_response(order: Order) -> PedidoResponseSchema:
    return PedidoResponseSchema(
        id=order.id,
        id_mesero=order.id_mesero,
        mesa_numero=order.mesa_numero,
        tipo_pedido=order.tipo_pedido,
        cliente_nombre=order.cliente_nombre,
        cliente_telefono=order.cliente_telefono,
        direccion_entrega=order.direccion_entrega,
        status=order.status,
        items=order.items,
        notas=order.notas,
        total_amount=float(order.total_amount),
        created_at=order.created_at,
        cocinando_at=order.cocinando_at,
        served_at=order.served_at,
        entregado_at=order.entregado_at,
        cancelado_at=order.cancelado_at,
        cancelado_por=order.cancelado_por,
        motivo_cancelacion=order.motivo_cancelacion,
    )


def validate_order_access(current_user: User, order: Order):
    if current_user.rol == UserRole.ADMIN:
        return

    if current_user.rol == UserRole.COCINA:
        return

    if current_user.rol == UserRole.MESERO and order.id_mesero == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para gestionar este pedido",
    )


def validate_order_owner_management_access(current_user: User, order: Order):
    if current_user.rol == UserRole.ADMIN:
        return

    if current_user.rol == UserRole.MESERO and order.id_mesero == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para gestionar este pedido",
    )


def validate_status_transition(current_status: OrderStatus, next_status: OrderStatus):
    allowed_transitions = {
        OrderStatus.PENDIENTE: {OrderStatus.EN_PREPARACION, OrderStatus.CANCELADO},
        OrderStatus.EN_PREPARACION: {OrderStatus.LISTO, OrderStatus.CANCELADO},
        OrderStatus.LISTO: {OrderStatus.ENTREGADO, OrderStatus.CANCELADO},
        OrderStatus.ENTREGADO: set(),
        OrderStatus.CANCELADO: set(),
    }

    if next_status == current_status:
        return

    if next_status not in allowed_transitions[current_status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transición de estado no permitida",
        )


def calculate_total(items: list[dict]) -> float:
    total = sum(float(item["cantidad"]) * float(item["precio_unitario"]) for item in items)
    return round(total, 2)


@router.get("", response_model=list[PedidoResponseSchema])
async def get_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    retention_days = await get_history_retention_days(db)
    await cleanup_expired_dispatched_orders(db, retention_days)

    stmt = select(Order).order_by(Order.created_at.desc())

    if current_user.rol == UserRole.MESERO:
        stmt = stmt.where(Order.id_mesero == current_user.id)

    result = await db.execute(stmt)
    orders = result.scalars().all()
    return [order_to_response(order) for order in orders]


@router.get("/history", response_model=OrderHistoryResponseSchema)
async def get_order_history(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.rol not in (UserRole.ADMIN, UserRole.COCINA, UserRole.MESERO):
        raise HTTPException(status_code=403, detail="No autorizado para ver historial")

    mesero_id = current_user.id if current_user.rol == UserRole.MESERO else None
    return await get_orders_history(db, max(1, min(limit, 500)), mesero_id=mesero_id)


@router.get("/{order_id}", response_model=PedidoResponseSchema)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    validate_order_access(current_user, order)
    return order_to_response(order)


@router.post("", response_model=PedidoResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: CrearPedidoSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.rol != UserRole.MESERO and current_user.rol != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="No autorizado para crear pedidos")

    items = [item.model_dump() for item in payload.items]
    total = calculate_total(items)

    order = Order(
        id_mesero=current_user.id,
        mesa_numero=payload.mesa_numero,
        tipo_pedido=payload.tipo_pedido,
        cliente_nombre=payload.cliente_nombre.strip() if payload.cliente_nombre else None,
        cliente_telefono=payload.cliente_telefono.strip() if payload.cliente_telefono else None,
        direccion_entrega=payload.direccion_entrega.strip() if payload.direccion_entrega else None,
        status=OrderStatus.PENDIENTE,
        items=items,
        notas=payload.notas,
        total_amount=total,
    )

    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order_to_response(order)


@router.put("/{order_id}", response_model=PedidoResponseSchema)
async def update_order(
    order_id: str,
    payload: ActualizarPedidoSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    validate_order_owner_management_access(current_user, order)

    if order.status != OrderStatus.PENDIENTE:
        raise HTTPException(status_code=400, detail="Solo se puede editar un pedido pendiente")

    if payload.mesa_numero is not None:
        order.mesa_numero = payload.mesa_numero

    if payload.tipo_pedido is not None:
        order.tipo_pedido = payload.tipo_pedido

    if payload.cliente_nombre is not None:
        order.cliente_nombre = payload.cliente_nombre.strip() or None

    if payload.cliente_telefono is not None:
        order.cliente_telefono = payload.cliente_telefono.strip() or None

    if payload.direccion_entrega is not None:
        order.direccion_entrega = payload.direccion_entrega.strip() or None

    if payload.notas is not None:
        order.notas = payload.notas

    if payload.items is not None:
        items = [item.model_dump() for item in payload.items]
        order.items = items
        order.total_amount = calculate_total(items)

    if order.tipo_pedido == TipoPedido.MESA:
        if order.mesa_numero is None:
            raise HTTPException(status_code=400, detail="Los pedidos de mesa requieren número de mesa")
        order.cliente_nombre = None
        order.cliente_telefono = None
        order.direccion_entrega = None
    else:
        order.mesa_numero = None
        if not order.cliente_nombre or not order.cliente_telefono or not order.direccion_entrega:
            raise HTTPException(status_code=400, detail="Los domicilios requieren datos completos")

    await db.commit()
    await db.refresh(order)
    return order_to_response(order)


@router.put("/{order_id}/status", response_model=PedidoResponseSchema)
async def update_order_status(
    order_id: str,
    payload: ActualizarEstadoSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    validate_order_access(current_user, order)

    if current_user.rol == UserRole.COCINA and payload.status not in (OrderStatus.EN_PREPARACION, OrderStatus.LISTO):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cocina solo puede marcar pedidos en preparación o listos",
        )

    if current_user.rol == UserRole.MESERO and payload.status != OrderStatus.ENTREGADO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mesero solo puede confirmar la entrega final",
        )

    validate_status_transition(order.status, payload.status)

    now = datetime.now(timezone.utc)
    order.status = payload.status

    if payload.status == OrderStatus.EN_PREPARACION and not order.cocinando_at:
        order.cocinando_at = now
    if payload.status == OrderStatus.LISTO and not order.served_at:
        order.served_at = now
    if payload.status == OrderStatus.ENTREGADO and not order.entregado_at:
        order.entregado_at = now

    await db.commit()
    await db.refresh(order)
    return order_to_response(order)


@router.put("/{order_id}/cancel", response_model=PedidoResponseSchema)
async def cancel_order(
    order_id: str,
    payload: CancelarPedidoSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    validate_order_owner_management_access(current_user, order)

    if order.status == OrderStatus.CANCELADO:
        return order_to_response(order)

    validate_status_transition(order.status, OrderStatus.CANCELADO)

    order.status = OrderStatus.CANCELADO
    order.cancelado_at = datetime.now(timezone.utc)
    order.cancelado_por = current_user.id
    order.motivo_cancelacion = payload.motivo_cancelacion

    await db.commit()
    await db.refresh(order)
    return order_to_response(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    validate_order_owner_management_access(current_user, order)

    if order.status != OrderStatus.PENDIENTE:
        raise HTTPException(status_code=400, detail="Solo se puede eliminar un pedido pendiente")

    await db.delete(order)
    await db.commit()
