from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.app_setting import AppSetting
from app.models.orden import Order, OrderStatus


ORDER_HISTORY_RETENTION_KEY = "order_history_retention_days"
DEFAULT_RETENTION_DAYS = 90


async def get_history_retention_days(db: AsyncSession) -> int:
    stmt = select(AppSetting).where(AppSetting.key == ORDER_HISTORY_RETENTION_KEY)
    result = await db.execute(stmt)
    setting = result.scalar_one_or_none()

    if not setting:
        return DEFAULT_RETENTION_DAYS

    try:
        return max(1, int(setting.value))
    except (ValueError, TypeError):
        return DEFAULT_RETENTION_DAYS


async def set_history_retention_days(db: AsyncSession, retention_days: int) -> int:
    stmt = select(AppSetting).where(AppSetting.key == ORDER_HISTORY_RETENTION_KEY)
    result = await db.execute(stmt)
    setting = result.scalar_one_or_none()

    if not setting:
        setting = AppSetting(key=ORDER_HISTORY_RETENTION_KEY, value=str(retention_days))
        db.add(setting)
    else:
        setting.value = str(retention_days)

    await db.commit()
    return retention_days


async def cleanup_expired_dispatched_orders(db: AsyncSession, retention_days: int) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    delivered_at_expr = func.coalesce(Order.entregado_at, Order.created_at)

    stmt = delete(Order).where(
        Order.status == OrderStatus.ENTREGADO,
        delivered_at_expr < cutoff,
    )

    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0


async def get_dispatched_history(db: AsyncSession) -> dict:
    retention_days = await get_history_retention_days(db)
    await cleanup_expired_dispatched_orders(db, retention_days)

    delivered_at_expr = func.coalesce(Order.entregado_at, Order.created_at)

    daily_stmt = (
        select(
            func.date(delivered_at_expr).label("fecha"),
            func.count(Order.id).label("cantidad"),
        )
        .where(Order.status == OrderStatus.ENTREGADO)
        .group_by(func.date(delivered_at_expr))
        .order_by(func.date(delivered_at_expr))
    )

    monthly_stmt = text("""
        SELECT
            to_char(coalesce(entregado_at, created_at), 'YYYY-MM') AS mes,
            count(id) AS cantidad
        FROM orders
        WHERE status::text = 'ENTREGADO'
        GROUP BY 1
        ORDER BY 1
    """)

    daily_result = await db.execute(daily_stmt)
    monthly_result = await db.execute(monthly_stmt)

    dispatched_por_dia = [
        {"fecha": row.fecha.isoformat(), "cantidad": int(row.cantidad)}
        for row in daily_result.all()
    ]
    dispatched_por_mes = [
        {"mes": row.mes, "cantidad": int(row.cantidad)}
        for row in monthly_result.all()
    ]

    return {
        "retention_days": retention_days,
        "dispatched_por_dia": dispatched_por_dia,
        "dispatched_por_mes": dispatched_por_mes,
    }


async def get_orders_history(db: AsyncSession, limit: int = 100, mesero_id: str | None = None) -> dict:
    retention_days = await get_history_retention_days(db)
    await cleanup_expired_dispatched_orders(db, retention_days)

    stmt = (
        select(Order)
        .where(Order.status.in_([OrderStatus.ENTREGADO, OrderStatus.CANCELADO]))
        .order_by(func.coalesce(Order.entregado_at, Order.cancelado_at, Order.created_at).desc())
        .limit(limit)
    )
    if mesero_id:
        stmt = stmt.where(Order.id_mesero == mesero_id)
    result = await db.execute(stmt)
    orders = result.scalars().all()

    now = datetime.now(timezone.utc)
    start_of_week = now - timedelta(days=now.weekday())
    deliveries_this_week = 0
    prep_durations: list[int] = []
    total_durations: list[int] = []
    history_items = []

    for order in orders:
        total_items = sum(int(item.get("cantidad", 0)) for item in (order.items or []))
        tiempo_hasta_preparacion = None
        tiempo_preparacion = None
        tiempo_total = None

        if order.cocinando_at and order.created_at:
            tiempo_hasta_preparacion = int((order.cocinando_at - order.created_at).total_seconds())

        if order.cocinando_at and order.served_at:
            tiempo_preparacion = int((order.served_at - order.cocinando_at).total_seconds())
            prep_durations.append(tiempo_preparacion)

        if order.created_at and order.entregado_at:
            tiempo_total = int((order.entregado_at - order.created_at).total_seconds())
            total_durations.append(tiempo_total)

        if (
            order.tipo_pedido == "domicilio"
            and order.created_at
            and order.created_at >= start_of_week
            and order.status == OrderStatus.ENTREGADO
        ):
            deliveries_this_week += 1

        history_items.append(
            {
                "id": order.id,
                "tipo_pedido": order.tipo_pedido,
                "mesa_numero": order.mesa_numero,
                "cliente_nombre": order.cliente_nombre,
                "cliente_telefono": order.cliente_telefono,
                "direccion_entrega": order.direccion_entrega,
                "status": order.status,
                "total_amount": float(order.total_amount),
                "created_at": order.created_at,
                "cocinando_at": order.cocinando_at,
                "served_at": order.served_at,
                "entregado_at": order.entregado_at,
                "cancelado_at": order.cancelado_at,
                "notas": order.notas,
                "total_items": total_items,
                "tiempo_hasta_preparacion_segundos": tiempo_hasta_preparacion,
                "tiempo_preparacion_segundos": tiempo_preparacion,
                "tiempo_total_segundos": tiempo_total,
            }
        )

    return {
        "summary": {
            "total_registros": len(history_items),
            "total_domicilios_semana": deliveries_this_week,
            "tiempo_promedio_preparacion_segundos": round(sum(prep_durations) / len(prep_durations), 2)
            if prep_durations
            else 0,
            "tiempo_promedio_total_segundos": round(sum(total_durations) / len(total_durations), 2)
            if total_durations
            else 0,
        },
        "items": history_items,
    }
