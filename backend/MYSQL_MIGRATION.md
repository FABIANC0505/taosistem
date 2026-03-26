# Migracion a MySQL 8

Este backend ya fue ajustado para trabajar con MySQL 8 y puede administrarse desde MySQL Workbench.

## 1. Crear la base en MySQL Workbench

1. Abre MySQL Workbench y conectate a tu servidor MySQL 8.
2. Abre el archivo [mysql_schema.sql](/C:/PRPDETO/taosistem_backend/backend/mysql_schema.sql).
3. Ejecuta el script completo.
4. Verifica que existan las tablas:
   - `users`
   - `products`
   - `app_settings`
   - `orders`

## 2. Configurar el backend local

Usa una de estas opciones en tu archivo `.env`:

```env
DATABASE_URL=mysql://root:tu_password@localhost:3306/bdtaosistem
```

o

```env
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_DB=bdtaosistem
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

## 3. Datos iniciales

Con la base creada, ejecuta el script de datos semilla:

```powershell
venv\Scripts\python.exe seed_data.py
```

## 4. Migrar datos existentes desde PostgreSQL

Si ya tienes informacion en PostgreSQL, puedes migrarla asi:

```powershell
$env:SOURCE_DATABASE_URL="postgresql://usuario:password@host:5432/base_origen"
$env:DATABASE_URL="mysql://root:password@localhost:3306/bdtaosistem"
venv\Scripts\python.exe migrate_postgres_to_mysql.py --dry-run
venv\Scripts\python.exe migrate_postgres_to_mysql.py
```

El script migra en este orden:

1. `users`
2. `products`
3. `app_settings`
4. `orders`

Antes de insertar, limpia las tablas destino para evitar duplicados.

### Flujo seguro recomendado

1. Haz un backup de PostgreSQL.
2. Haz un backup o crea una base nueva en MySQL.
3. Ejecuta primero `--dry-run`.
4. Revisa los conteos de `users`, `products`, `app_settings` y `orders`.
5. Ejecuta la migracion real solo si los conteos tienen sentido.
6. Valida login, usuarios, pedidos e historial.

## 5. Variables en Railway

Si usas Railway con un servicio MySQL, puedes configurar el backend de cualquiera de estas maneras:

### Opcion A

Usar una variable unica:

```env
MYSQL_URL=${{MySQL.MYSQL_URL}}
```

### Opcion B

Usar referencias separadas:

```env
MYSQLHOST=${{MySQL.MYSQLHOST}}
MYSQLPORT=${{MySQL.MYSQLPORT}}
MYSQLUSER=${{MySQL.MYSQLUSER}}
MYSQLPASSWORD=${{MySQL.MYSQLPASSWORD}}
MYSQLDATABASE=${{MySQL.MYSQLDATABASE}}
```

Ademas agrega:

```env
JWT_SECRET_KEY=una_clave_larga_y_segura
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=480
JWT_REFRESH_EXPIRE_DAYS=30
APP_ENV=production
FRONTEND_URL=https://tu-frontend.vercel.app
CORS_ORIGINS=https://tu-frontend.vercel.app
```

## 6. Validacion recomendada

1. Inicia backend.
2. Inicia frontend.
3. Ingresa como admin, mesero y cocina en ventanas distintas.
4. Crea un pedido desde mesero.
5. Verifica que cocina lo vea y cambie su estado.
6. Confirma que admin vea usuarios, historial y metricas.
