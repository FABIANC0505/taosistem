from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DB: str = "bdtaosistem"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_URL: str | None = None
    MYSQLHOST: str | None = None
    MYSQLPORT: int | None = None
    MYSQLUSER: str | None = None
    MYSQLPASSWORD: str | None = None
    MYSQLDATABASE: str | None = None
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 480
    JWT_REFRESH_EXPIRE_DAYS: int = 30
    APP_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"
    DATABASE_URL: str | None = None
    CORS_ORIGINS: str | None = None

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            db_url = self.DATABASE_URL
        elif self.MYSQL_URL:
            db_url = self.MYSQL_URL
        elif self.MYSQLHOST and self.MYSQLUSER and self.MYSQLDATABASE:
            mysql_password = self.MYSQLPASSWORD or ""
            mysql_port = self.MYSQLPORT or 3306
            db_url = (
                f"mysql://{self.MYSQLUSER}:{mysql_password}"
                f"@{self.MYSQLHOST}:{mysql_port}/{self.MYSQLDATABASE}"
            )
        else:
            return (
                f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
            )
        if db_url.startswith("mysql://"):
            db_url = db_url.replace("mysql://", "mysql+aiomysql://", 1)
        if db_url.startswith("mysql+pymysql://"):
            db_url = db_url.replace("mysql+pymysql://", "mysql+aiomysql://", 1)
        if db_url.startswith("postgres://"):
            raise ValueError("La configuracion actual del proyecto espera MySQL 8, no PostgreSQL.")
        if db_url.startswith("postgresql://"):
            raise ValueError("La configuracion actual del proyecto espera MySQL 8, no PostgreSQL.")
        return db_url

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
            self.FRONTEND_URL,
        ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
