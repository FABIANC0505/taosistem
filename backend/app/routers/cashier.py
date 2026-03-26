from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.app_setting import AppSetting
from app.models.cashier import CashMovement, CashMovementType, CashPayment, CashSession, PaymentMethod, WaiterAlert
from app.models.orden import Order, OrderStatus
from app.models.user import User, UserRole
from app.routers.users import get_current_user

router = APIRouter(prefix="/cashier", tags=["cashier"])

TOTAL_TABLES_KEY = "total_mesas"
DEFAULT_TOTAL_TABLES = 12


def require_cashier_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.rol not in (UserRole.CAJERO, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="No autorizado")
    return current_user


def require_cashier(current_user: User = Depends(get_current_user)) -> User:
    if current_user.rol != UserRole.CAJERO:
        raise HTTPException(status_code=403, detail="No autorizado")
    return current_user


class CashSessionOpenRequest(BaseModel):
    opening_amount: float = Field(..., ge=0)
    opening_note: str | None = None


class CashSessionCloseRequest(BaseModel):
    counted_amount: float = Field(..., ge=0)
    closing_note: str | None = None


class CashMovementRequest(BaseModel):
    movement_type: CashMovementType
    amount: float = Field(..., ge=0.01)
    description: str = Field(..., min_length=3, max_length=500)
    related_order_id: str | None = None


class CashPaymentRequest(BaseModel):
    amount: float = Field(..., ge=0.01)
    payment_method: PaymentMethod
    order_id: str | None = None
    mesa_numero: int | None = Field(default=None, ge=1, le=300)
    reference_note: str | None = Field(default=None, max_length=500)


class WaiterAlertRequest(BaseModel):
    mesa_numero: int = Field(..., ge=1, le=300)
    message: str = Field(..., min_length=3, max_length=500)


class WaiterAlertResponse(BaseModel):
    id: str
    mesa_numero: int
    cashier_user_id: str
    mesero_user_id: str | None
    message: str
    resolved: bool
    created_at: str | None
    resolved_at: str | None


class CashMovementResponse(BaseModel):
    id: str
    session_id: str
    cashier_user_id: str
    movement_type: CashMovementType
    amount: float
    description: str
    related_order_id: str | None
    created_at: str | None


class CashPaymentResponse(BaseModel):
    id: str
    session_id: str
    cashier_user_id: str
    order_id: str | None
    mesa_numero: int | None
    payment_method: PaymentMethod
    amount: float
    reference_note: str | None
    created_at: str | None


class PaymentMethodSummary(BaseModel):
    payment_method: PaymentMethod
    total_amount: float
    transactions: int


class CashSessionResponse(BaseModel):
    id: str
    cashier_user_id: str
    opening_amount: float
    opening_note: str | None
    opened_at: str | None
    closed_at: str | None
    is_open: bool
    closing_counted_amount: float | None = None
    closing_note: str | None = None


class CashTableSummaryItem(BaseModel):
    mesa_numero: int
    libre: bool
    order_id: str | None = None
    status: str | None = None
    total_amount: float | None = None
    mesero_id: str | None = None
    mesero_nombre: str | None = None
    created_at: str | None = None


class CashierSummaryResponse(BaseModel):
    total_mesas: int
    mesas_ocupadas: list[CashTableSummaryItem]
    mesas_libres: list[CashTableSummaryItem]
    active_alerts: list[WaiterAlertResponse]
    open_session: CashSessionResponse | None
    recent_payments: list[CashPaymentResponse]
    payment_summary: list[PaymentMethodSummary]


def alert_to_response(alert: WaiterAlert) -> WaiterAlertResponse:
    return WaiterAlertResponse(
        id=alert.id,
        mesa_numero=alert.mesa_numero,
        cashier_user_id=alert.cashier_user_id,
        mesero_user_id=alert.mesero_user_id,
        message=alert.message,
        resolved=alert.resolved,
        created_at=alert.created_at.isoformat() if alert.created_at else None,
        resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
    )


def movement_to_response(movement: CashMovement) -> CashMovementResponse:
    return CashMovementResponse(
        id=movement.id,
        session_id=movement.session_id,
        cashier_user_id=movement.cashier_user_id,
        movement_type=movement.movement_type,
        amount=float(movement.amount),
        description=movement.description,
        related_order_id=movement.related_order_id,
        created_at=movement.created_at.isoformat() if movement.created_at else None,
    )


def payment_to_response(payment: CashPayment) -> CashPaymentResponse:
    return CashPaymentResponse(
        id=payment.id,
        session_id=payment.session_id,
        cashier_user_id=payment.cashier_user_id,
        order_id=payment.order_id,
        mesa_numero=payment.mesa_numero,
        payment_method=payment.payment_method,
        amount=float(payment.amount),
        reference_note=payment.reference_note,
        created_at=payment.created_at.isoformat() if payment.created_at else None,
    )


def session_to_response(session: CashSession, include_closing_data: bool) -> CashSessionResponse:
    return CashSessionResponse(
        id=session.id,
        cashier_user_id=session.cashier_user_id,
        opening_amount=float(session.opening_amount),
        opening_note=session.opening_note,
        opened_at=session.opened_at.isoformat() if session.opened_at else None,
        closed_at=session.closed_at.isoformat() if session.closed_at else None,
        is_open=session.closed_at is None,
        closing_counted_amount=float(session.closing_counted_amount) if include_closing_data and session.closing_counted_amount is not None else None,
        closing_note=session.closing_note if include_closing_data else None,
    )


async def get_open_session(db: AsyncSession, cashier_user_id: str) -> CashSession | None:
    result = await db.execute(
        select(CashSession)
        .where(
            CashSession.cashier_user_id == cashier_user_id,
            CashSession.closed_at.is_(None),
        )
        .order_by(CashSession.opened_at.desc())
    )
    return result.scalar_one_or_none()


async def get_total_tables(db: AsyncSession) -> int:
    result = await db.execute(select(AppSetting).where(AppSetting.key == TOTAL_TABLES_KEY))
    setting = result.scalar_one_or_none()
    if not setting:
        return DEFAULT_TOTAL_TABLES
    try:
        return max(1, int(setting.value))
    except (TypeError, ValueError):
        return DEFAULT_TOTAL_TABLES


async def get_recent_payments(db: AsyncSession, session_id: str | None) -> list[CashPayment]:
    if not session_id:
        return []
    result = await db.execute(
        select(CashPayment)
        .where(CashPayment.session_id == session_id)
        .order_by(CashPayment.created_at.desc())
        .limit(20)
    )
    return result.scalars().all()


def build_payment_summary(payments: list[CashPayment]) -> list[PaymentMethodSummary]:
    grouped: dict[PaymentMethod, PaymentMethodSummary] = {}
    for payment in payments:
        existing = grouped.get(payment.payment_method)
        if existing:
            existing.total_amount += float(payment.amount)
            existing.transactions += 1
            continue
        grouped[payment.payment_method] = PaymentMethodSummary(
            payment_method=payment.payment_method,
            total_amount=float(payment.amount),
            transactions=1,
        )
    return sorted(grouped.values(), key=lambda item: item.payment_method.value)


async def get_active_alerts(db: AsyncSession, mesero_user_id: str | None = None) -> list[WaiterAlert]:
    stmt = select(WaiterAlert).where(WaiterAlert.resolved.is_(False)).order_by(WaiterAlert.created_at.desc())
    if mesero_user_id is not None:
        stmt = stmt.where(
            or_(WaiterAlert.mesero_user_id == mesero_user_id, WaiterAlert.mesero_user_id.is_(None))
        )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/summary", response_model=CashierSummaryResponse)
async def get_cashier_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cashier_or_admin),
):
    total_tables = await get_total_tables(db)
    result = await db.execute(
        select(Order, User)
        .join(User, User.id == Order.id_mesero)
        .where(
            and_(
                Order.tipo_pedido == "mesa",
                Order.mesa_numero.is_not(None),
                Order.status.notin_([OrderStatus.ENTREGADO, OrderStatus.CANCELADO]),
            )
        )
        .order_by(Order.created_at.desc())
    )

    occupied_map: dict[int, CashTableSummaryItem] = {}
    for order, mesero in result.all():
        if order.mesa_numero in occupied_map:
            continue
        occupied_map[order.mesa_numero] = CashTableSummaryItem(
            mesa_numero=order.mesa_numero,
            libre=False,
            order_id=order.id,
            status=order.status.value if hasattr(order.status, "value") else str(order.status),
            total_amount=float(order.total_amount),
            mesero_id=mesero.id,
            mesero_nombre=mesero.nombre,
            created_at=order.created_at.isoformat() if order.created_at else None,
        )

    occupied_tables = sorted(occupied_map.values(), key=lambda item: item.mesa_numero)
    free_tables = [
        CashTableSummaryItem(mesa_numero=mesa, libre=True)
        for mesa in range(1, total_tables + 1)
        if mesa not in occupied_map
    ]

    active_alerts = [alert_to_response(alert) for alert in await get_active_alerts(db)]
    open_session = None
    recent_payments: list[CashPaymentResponse] = []
    payment_summary: list[PaymentMethodSummary] = []
    if current_user.rol == UserRole.CAJERO:
        session = await get_open_session(db, current_user.id)
        if session:
            open_session = session_to_response(session, include_closing_data=False)
            payments = await get_recent_payments(db, session.id)
            recent_payments = [payment_to_response(payment) for payment in payments]
            payment_summary = build_payment_summary(payments)

    return CashierSummaryResponse(
        total_mesas=total_tables,
        mesas_ocupadas=occupied_tables,
        mesas_libres=free_tables,
        active_alerts=active_alerts,
        open_session=open_session,
        recent_payments=recent_payments,
        payment_summary=payment_summary,
    )


@router.get("/session/current", response_model=CashSessionResponse | None)
async def get_current_cash_session(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cashier),
):
    session = await get_open_session(db, current_user.id)
    if not session:
        return None
    return session_to_response(session, include_closing_data=False)


@router.post("/session/open", response_model=CashSessionResponse, status_code=status.HTTP_201_CREATED)
async def open_cash_session(
    payload: CashSessionOpenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cashier),
):
    current_session = await get_open_session(db, current_user.id)
    if current_session:
        raise HTTPException(status_code=400, detail="Ya tienes una caja abierta")

    session = CashSession(
        cashier_user_id=current_user.id,
        opening_amount=payload.opening_amount,
        opening_note=payload.opening_note.strip() if payload.opening_note else None,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session_to_response(session, include_closing_data=False)


@router.post("/session/close", response_model=CashSessionResponse)
async def close_cash_session(
    payload: CashSessionCloseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cashier),
):
    session = await get_open_session(db, current_user.id)
    if not session:
        raise HTTPException(status_code=400, detail="No tienes una caja abierta")

    session.closing_counted_amount = payload.counted_amount
    session.closing_note = payload.closing_note.strip() if payload.closing_note else None
    session.closed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(session)
    return session_to_response(session, include_closing_data=False)


@router.get("/movements", response_model=list[CashMovementResponse])
async def get_cash_movements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cashier),
):
    session = await get_open_session(db, current_user.id)
    if not session:
        return []
    result = await db.execute(
        select(CashMovement)
        .where(CashMovement.session_id == session.id)
        .order_by(CashMovement.created_at.desc())
    )
    return [movement_to_response(item) for item in result.scalars().all()]


@router.post("/movements", response_model=CashMovementResponse, status_code=status.HTTP_201_CREATED)
async def create_cash_movement(
    payload: CashMovementRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cashier),
):
    session = await get_open_session(db, current_user.id)
    if not session:
        raise HTTPException(status_code=400, detail="Debes abrir caja antes de registrar movimientos")

    movement = CashMovement(
        session_id=session.id,
        cashier_user_id=current_user.id,
        movement_type=payload.movement_type,
        amount=payload.amount,
        description=payload.description.strip(),
        related_order_id=payload.related_order_id,
    )
    db.add(movement)
    await db.commit()
    await db.refresh(movement)
    return movement_to_response(movement)


@router.get("/payments", response_model=list[CashPaymentResponse])
async def get_cash_payments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cashier),
):
    session = await get_open_session(db, current_user.id)
    if not session:
        return []
    payments = await get_recent_payments(db, session.id)
    return [payment_to_response(payment) for payment in payments]


@router.post("/payments", response_model=CashPaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_cash_payment(
    payload: CashPaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cashier),
):
    session = await get_open_session(db, current_user.id)
    if not session:
        raise HTTPException(status_code=400, detail="Debes abrir caja antes de registrar pagos")

    order_id = payload.order_id.strip() if payload.order_id else None
    reference_note = payload.reference_note.strip() if payload.reference_note else None

    payment = CashPayment(
        session_id=session.id,
        cashier_user_id=current_user.id,
        order_id=order_id,
        mesa_numero=payload.mesa_numero,
        payment_method=payload.payment_method,
        amount=payload.amount,
        reference_note=reference_note,
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment_to_response(payment)


@router.get("/alerts", response_model=list[WaiterAlertResponse])
async def get_cashier_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cashier_or_admin),
):
    return [alert_to_response(alert) for alert in await get_active_alerts(db)]


@router.post("/alerts", response_model=WaiterAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_waiter_alert(
    payload: WaiterAlertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cashier),
):
    result = await db.execute(
        select(Order)
        .where(
            and_(
                Order.tipo_pedido == "mesa",
                Order.mesa_numero == payload.mesa_numero,
                Order.status.notin_([OrderStatus.ENTREGADO, OrderStatus.CANCELADO]),
            )
        )
        .order_by(Order.created_at.desc())
    )
    order = result.scalars().first()

    mesero_user_id = order.id_mesero if order else None

    alert = WaiterAlert(
        mesa_numero=payload.mesa_numero,
        cashier_user_id=current_user.id,
        mesero_user_id=mesero_user_id,
        message=payload.message.strip(),
        resolved=False,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert_to_response(alert)


@router.get("/alerts/my", response_model=list[WaiterAlertResponse])
async def get_my_waiter_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.rol not in (UserRole.MESERO, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="No autorizado")
    alerts = await get_active_alerts(db, mesero_user_id=current_user.id if current_user.rol == UserRole.MESERO else None)
    return [alert_to_response(alert) for alert in alerts]


@router.put("/alerts/{alert_id}/resolve", response_model=WaiterAlertResponse)
async def resolve_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.rol not in (UserRole.CAJERO, UserRole.MESERO, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="No autorizado")

    result = await db.execute(select(WaiterAlert).where(WaiterAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Aviso no encontrado")

    if current_user.rol == UserRole.MESERO and alert.mesero_user_id not in (None, current_user.id):
        raise HTTPException(status_code=403, detail="No autorizado para cerrar este aviso")

    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    await db.commit()
    await db.refresh(alert)
    return alert_to_response(alert)
