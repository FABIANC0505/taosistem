#!/usr/bin/env python3
"""
Validacion rapida del backend para MySQL 8 / Workbench.
No ejecuta la aplicacion; revisa configuracion y archivos necesarios.
"""

from pathlib import Path


def check(condition: bool, message: str) -> bool:
    prefix = "OK" if condition else "FAIL"
    print(f"[{prefix}] {message}")
    return condition


def file_contains(path: Path, text: str) -> bool:
    return text in path.read_text(encoding="utf-8")


def main() -> int:
    root = Path(".")
    passed = 0
    failed = 0

    required_files = [
        root / "main.py",
        root / "requirements.txt",
        root / "mysql_schema.sql",
        root / "seed_data.py",
        root / "migrate_postgres_to_mysql.py",
        root / "app" / "core" / "config.py",
        root / "app" / "core" / "database.py",
    ]

    for path in required_files:
        if check(path.exists(), f"Existe {path.as_posix()}"):
            passed += 1
        else:
            failed += 1

    requirements = (root / "requirements.txt").read_text(encoding="utf-8")
    for dependency in ("fastapi", "uvicorn", "sqlalchemy", "aiomysql", "PyMySQL", "pg8000"):
        if check(dependency in requirements, f"Dependencia presente: {dependency}"):
            passed += 1
        else:
            failed += 1

    config_path = root / "app" / "core" / "config.py"
    config_checks = [
        ("MYSQL_DB configurado", "MYSQL_DB" in config_path.read_text(encoding="utf-8")),
        ("DATABASE_URL soportado", file_contains(config_path, "DATABASE_URL")),
        ("MYSQL_URL soportado", file_contains(config_path, "MYSQL_URL")),
        ("Bloqueo de PostgreSQL activo", "espera MySQL 8" in config_path.read_text(encoding="utf-8")),
    ]
    for label, result in config_checks:
        if check(result, label):
            passed += 1
        else:
            failed += 1

    env_example = (root / ".env.example").read_text(encoding="utf-8")
    env_checks = [
        ("Ejemplo usa bdtaosistem", "MYSQL_DB=bdtaosistem" in env_example),
        ("Ejemplo incluye CORS_ORIGINS", "CORS_ORIGINS=" in env_example),
        ("Ejemplo incluye JWT_SECRET_KEY", "JWT_SECRET_KEY=" in env_example),
    ]
    for label, result in env_checks:
        if check(result, label):
            passed += 1
        else:
            failed += 1

    print(f"\nResumen: {passed} correctos, {failed} pendientes")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
