from collections import defaultdict
from datetime import datetime, timedelta
from statistics import StatisticsError, mean, mode
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.models.orden import Order, OrderStatus
from app.models.producto import Product
from app.models.user import User, UserRole
from app.services.history_settings import get_dispatched_history

router = APIRouter(prefix="/metrics", tags=["metrics"])


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


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.rol != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado",
        )
    return current_user


async def require_admin_or_cocina(current_user: User = Depends(get_current_user)) -> User:
    if current_user.rol not in (UserRole.ADMIN, UserRole.COCINA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado",
        )
    return current_user


class DispatchedByDayPoint(BaseModel):
    fecha: str
    cantidad: int


class DispatchedByMonthPoint(BaseModel):
    mes: str
    cantidad: int


class DispatchedHistoryResponse(BaseModel):
    retention_days: int
    dispatched_por_dia: List[DispatchedByDayPoint]
    dispatched_por_mes: List[DispatchedByMonthPoint]


class MetricsResponse(BaseModel):
    total_ingresos: float
    total_ordenes: int
    ordenes_hoy: int
    productos_agotados: int
    producto_mas_vendido: dict
    media_ingresos: float
    moda_ingresos: float
    ingresos_por_dia: List[dict]
    productos_top: List[dict]
    dispatched_por_dia: List[DispatchedByDayPoint]
    dispatched_por_mes: List[DispatchedByMonthPoint]
    domicilios_semana: int
    tiempo_promedio_preparacion_segundos: float
    tiempo_promedio_entrega_segundos: float


def _normalize_datetime(value):
    return value if value else None


@router.get("/dashboard", response_model=MetricsResponse)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    dispatched_history = await get_dispatched_history(db)

    total_ordenes_result = await db.execute(select(func.count(Order.id)))
    total_ordenes = int(total_ordenes_result.scalar() or 0)

    productos_agotados_result = await db.execute(select(func.count(Product.id)).where(Product.disponible == False))
    productos_agotados = int(productos_agotados_result.scalar() or 0)

    orders_result = await db.execute(select(Order))
    orders = orders_result.scalars().all()

    today = datetime.now().date()
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    thirty_days_ago = datetime.now() - timedelta(days=30)

    delivered_orders = [order for order in orders if order.status == OrderStatus.ENTREGADO]
    total_ingresos = round(sum(float(order.total_amount) for order in delivered_orders), 2)
    ordenes_hoy = sum(1 for order in orders if order.created_at and order.created_at.date() == today)
    domicilios_semana = sum(
        1
        for order in delivered_orders
        if order.tipo_pedido == "domicilio" and order.created_at and order.created_at >= week_start
    )

    ingresos_por_dia_map: dict[str, float] = defaultdict(float)
    for order in delivered_orders:
        if order.created_at and order.created_at >= thirty_days_ago:
            ingresos_por_dia_map[order.created_at.date().isoformat()] += float(order.total_amount)

    ingresos_por_dia = [
        {"fecha": fecha, "ingresos": round(ingresos, 2)}
        for fecha, ingresos in sorted(ingresos_por_dia_map.items())
    ]

    ingresos_list = [float(dia["ingresos"]) for dia in ingresos_por_dia]
    media_ingresos = mean(ingresos_list) if ingresos_list else 0.0
    try:
        moda_ingresos = float(mode(ingresos_list)) if ingresos_list else 0.0
    except StatisticsError:
        moda_ingresos = media_ingresos

    productos_map: dict[str, dict] = defaultdict(lambda: {"cantidad": 0, "ingresos": 0.0})
    for order in delivered_orders:
        for item in order.items or []:
            nombre = str(item.get("nombre", "Sin nombre"))
            cantidad = int(item.get("cantidad", 0))
            precio = float(item.get("precio_unitario", 0))
            productos_map[nombre]["cantidad"] += cantidad
            productos_map[nombre]["ingresos"] += cantidad * precio

    productos_top = sorted(
        [
            {
                "nombre": nombre,
                "cantidad": data["cantidad"],
                "ingresos": round(data["ingresos"], 2),
            }
            for nombre, data in productos_map.items()
        ],
        key=lambda item: item["cantidad"],
        reverse=True,
    )[:10]

    producto_mas_vendido = {"nombre": "N/A", "cantidad": 0}
    if productos_top:
        producto_mas_vendido = {
            "nombre": productos_top[0]["nombre"],
            "cantidad": productos_top[0]["cantidad"],
        }

    prep_durations = [
        (order.served_at - order.cocinando_at).total_seconds()
        for order in delivered_orders
        if order.cocinando_at and order.served_at
    ]
    total_durations = [
        (order.entregado_at - order.created_at).total_seconds()
        for order in delivered_orders
        if order.created_at and order.entregado_at
    ]

    return MetricsResponse(
        total_ingresos=total_ingresos,
        total_ordenes=total_ordenes,
        ordenes_hoy=ordenes_hoy,
        productos_agotados=productos_agotados,
        producto_mas_vendido=producto_mas_vendido,
        media_ingresos=media_ingresos,
        moda_ingresos=moda_ingresos,
        ingresos_por_dia=ingresos_por_dia,
        productos_top=productos_top,
        dispatched_por_dia=dispatched_history["dispatched_por_dia"],
        dispatched_por_mes=dispatched_history["dispatched_por_mes"],
        domicilios_semana=domicilios_semana,
        tiempo_promedio_preparacion_segundos=round(sum(prep_durations) / len(prep_durations), 2) if prep_durations else 0,
        tiempo_promedio_entrega_segundos=round(sum(total_durations) / len(total_durations), 2) if total_durations else 0,
    )


@router.get("/dispatched-history", response_model=DispatchedHistoryResponse)
async def get_dispatched_orders_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_cocina),
):
    history = await get_dispatched_history(db)
    return DispatchedHistoryResponse(**history)


@router.get("/income-trends")
async def get_income_trends(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    start_date = datetime.now() - timedelta(days=days)
    orders_result = await db.execute(select(Order).where(Order.status == OrderStatus.ENTREGADO))
    orders = orders_result.scalars().all()

    ingresos_por_dia_map: dict[str, float] = defaultdict(float)
    for order in orders:
        if order.created_at and order.created_at >= start_date:
            ingresos_por_dia_map[order.created_at.date().isoformat()] += float(order.total_amount)

    return [
        {"fecha": fecha, "ingresos": round(ingresos, 2)}
        for fecha, ingresos in sorted(ingresos_por_dia_map.items())
    ]


@router.get("/top-products")
async def get_top_products(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    orders_result = await db.execute(select(Order).where(Order.status == OrderStatus.ENTREGADO))
    orders = orders_result.scalars().all()

    productos_map: dict[str, dict] = defaultdict(lambda: {"cantidad": 0, "ingresos": 0.0})
    for order in orders:
        for item in order.items or []:
            nombre = str(item.get("nombre", "Sin nombre"))
            cantidad = int(item.get("cantidad", 0))
            precio = float(item.get("precio_unitario", 0))
            productos_map[nombre]["cantidad"] += cantidad
            productos_map[nombre]["ingresos"] += cantidad * precio

    return sorted(
        [
            {
                "nombre": nombre,
                "cantidad": data["cantidad"],
                "ingresos": round(data["ingresos"], 2),
            }
            for nombre, data in productos_map.items()
        ],
        key=lambda item: item["cantidad"],
        reverse=True,
    )[:limit]


@router.get("/statistics")
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    stmt = select(Order.status, func.count(Order.id).label("cantidad")).group_by(Order.status)
    result = await db.execute(stmt)
    ordenes_por_estado = {row.status.value: row.cantidad for row in result.all()}

    avg_result = await db.execute(select(func.coalesce(func.avg(Order.total_amount), 0)))
    promedio_gasto = float(avg_result.scalar() or 0)

    return {
        "ordenes_por_estado": ordenes_por_estado,
        "promedio_gasto_por_orden": promedio_gasto,
    }
