# ============================================
# Dockerfile para Frontend React + Vite
# Build Stage
# ============================================

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm ci --prefer-offline --no-audit

# Copiar el código fuente
COPY . .

# Compilar aplicación
RUN npm run build

# Stage 2: Serve
FROM node:18-alpine

WORKDIR /app

# Instalar servidor HTTP simple
RUN npm install -g serve

# Copiar build del stage anterior
COPY --from=builder /app/dist ./dist

# Exponer puerto 3000
EXPOSE 3000

# Comando para servir la aplicación
CMD ["serve", "-s", "dist", "-l", "3000"]
