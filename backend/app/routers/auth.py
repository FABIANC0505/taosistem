from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, UserRole
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    nombre: str
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

    class Config:
        from_attributes = True

@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Autenticar usuario y obtener token JWT"""
    
    # Buscar usuario por email
    stmt = select(User).where(User.email == credentials.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # Verificar credenciales
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear token
    access_token = create_access_token({"sub": user.id, "email": user.email})
    
    return AuthResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email,
            "rol": user.rol.value,
            "activo": user.activo,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
    )

@router.post("/register", response_model=AuthResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Registrar nuevo usuario (solo para primeros registros o admin)"""
    import traceback
    try:
        # Verificar si ya existe
        stmt = select(User).where(User.email == data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya registrado"
            )
        
        # Crear usuario como ADMIN si es el primero
        stmt = select(User)
        result = await db.execute(stmt)
        existing_users = result.scalars().all()
        rol = UserRole.ADMIN if not existing_users else UserRole.MESERO
        
        new_user = User(
            nombre=data.nombre,
            email=data.email,
            password_hash=hash_password(data.password),
            rol=rol,
            activo=True
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Crear token
        access_token = create_access_token({"sub": new_user.id, "email": new_user.email})
        
        return AuthResponse(
            access_token=access_token,
            user={
                "id": new_user.id,
                "nombre": new_user.nombre,
                "email": new_user.email,
                "rol": new_user.rol.value,
                "activo": new_user.activo,
                "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
                "updated_at": new_user.updated_at.isoformat() if new_user.updated_at else None,
            }
        )
    except Exception as e:
        traceback.print_exc()
        raise e
