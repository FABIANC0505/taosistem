from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import get_db
from app.models.orden import Order, OrderStatus
from app.models.producto import Product
from pydantic import BaseModel
from statistics import mean, mode, StatisticsError
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/metrics", tags=["metrics"])

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

@router.get("/dashboard", response_model=MetricsResponse)
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db)):
    """Obtener todas las métricas del dashboard"""
    
    # Total de ingresos
    stmt = select(func.coalesce(func.sum(Order.total_amount), 0)).where(
        Order.status.in_([OrderStatus.ENTREGADO])
    )
    result = await db.execute(stmt)
    total_ingresos = float(result.scalar())
    
    # Total de órdenes
    stmt = select(func.count(Order.id))
    result = await db.execute(stmt)
    total_ordenes = result.scalar()
    
    # Órdenes de hoy
    today = datetime.now().date()
    stmt = select(func.count(Order.id)).where(
        func.date(Order.created_at) == today
    )
    result = await db.execute(stmt)
    ordenes_hoy = result.scalar()
    
    # Productos agotados
    stmt = select(func.count(Product.id)).where(Product.disponible == False)
    result = await db.execute(stmt)
    productos_agotados = result.scalar()
    
    # Ingresos por día (últimos 30 días)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    stmt = select(
        func.date(Order.created_at).label("fecha"),
        func.coalesce(func.sum(Order.total_amount), 0).label("ingresos")
    ).where(
        Order.created_at >= thirty_days_ago,
        Order.status.in_([OrderStatus.ENTREGADO])
    ).group_by(
        func.date(Order.created_at)
    ).order_by(func.date(Order.created_at))
    
    result = await db.execute(stmt)
    ingresos_por_dia = [
        {"fecha": row.fecha.isoformat(), "ingresos": float(row.ingresos)}
        for row in result.all()
    ]
    
    # Media y Moda de ingresos
    ingresos_list = [float(dia["ingresos"]) for dia in ingresos_por_dia]
    media_ingresos = mean(ingresos_list) if ingresos_list else 0.0
    try:
        moda_ingresos = float(mode(ingresos_list)) if ingresos_list else 0.0
    except StatisticsError:
        moda_ingresos = media_ingresos
    
    # Top 10 productos más vendidos
    stmt = select(
        Product.nombre,
        func.count(Order.id).label("cantidad"),
        func.sum(Order.total_amount).label("ingresos")
    ).join(
        Order, True
    ).group_by(
        Product.nombre
    ).order_by(
        func.count(Order.id).desc()
    ).limit(10)
    
    result = await db.execute(stmt)
    productos_top = [
        {
            "nombre": row.nombre,
            "cantidad": row.cantidad,
            "ingresos": float(row.ingresos) if row.ingresos else 0.0
        }
        for row in result.all()
    ]
    
    # Producto más vendido
    producto_mas_vendido = {"nombre": "N/A", "cantidad": 0}
    if productos_top:
        producto_mas_vendido = {
            "nombre": productos_top[0]["nombre"],
            "cantidad": productos_top[0]["cantidad"]
        }
    
    return MetricsResponse(
        total_ingresos=total_ingresos,
        total_ordenes=total_ordenes,
        ordenes_hoy=ordenes_hoy,
        productos_agotados=productos_agotados,
        producto_mas_vendido=producto_mas_vendido,
        media_ingresos=media_ingresos,
        moda_ingresos=moda_ingresos,
        ingresos_por_dia=ingresos_por_dia,
        productos_top=productos_top
    )

@router.get("/income-trends")
async def get_income_trends(days: int = Query(30, ge=1, le=365), db: AsyncSession = Depends(get_db)):
    """Obtener tendencia de ingresos"""
    
    start_date = datetime.now() - timedelta(days=days)
    stmt = select(
        func.date(Order.created_at).label("fecha"),
        func.coalesce(func.sum(Order.total_amount), 0).label("ingresos")
    ).where(
        Order.created_at >= start_date,
        Order.status.in_([OrderStatus.ENTREGADO])
    ).group_by(
        func.date(Order.created_at)
    ).order_by(func.date(Order.created_at))
    
    result = await db.execute(stmt)
    return [
        {"fecha": row.fecha.isoformat(), "ingresos": float(row.ingresos)}
        for row in result.all()
    ]

@router.get("/top-products")
async def get_top_products(limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    """Obtener productos más vendidos"""
    
    # Nota: Esta es una aproximación simplificada
    # En producción, necesitarías una tabla separada para items de orden
    stmt = select(
        Product.nombre,
        func.count(Order.id).label("cantidad"),
        func.sum(Order.total_amount).label("ingresos")
    ).join(
        Order, True
    ).group_by(
        Product.nombre
    ).order_by(
        func.count(Order.id).desc()
    ).limit(limit)
    
    result = await db.execute(stmt)
    return [
        {
            "nombre": row.nombre,
            "cantidad": row.cantidad,
            "ingresos": float(row.ingresos) if row.ingresos else 0.0
        }
        for row in result.all()
    ]

@router.get("/statistics")
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """Obtener estadísticas generales"""
    
    # Órdenes por estado
    stmt = select(
        Order.status,
        func.count(Order.id).label("cantidad")
    ).group_by(Order.status)
    
    result = await db.execute(stmt)
    ordenes_por_estado = {
        row.status.value: row.cantidad
        for row in result.all()
    }
    
    # Promedio de gasto por orden
    stmt = select(func.coalesce(func.avg(Order.total_amount), 0))
    result = await db.execute(stmt)
    promedio_gasto = float(result.scalar())
    
    return {
        "ordenes_por_estado": ordenes_por_estado,
        "promedio_gasto_por_orden": promedio_gasto
    }
