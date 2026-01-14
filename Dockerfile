# 1. Etapa de base con Node y pnpm
FROM node:20-alpine AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
RUN npm install -g pnpm@9.0.0 turbo

# 2. Etapa de "Pruning" (Limpieza de código innecesario)
FROM base AS pruner
WORKDIR /app
COPY . .
ARG APP_NAME
# Extrae solo lo necesario para el microservicio específico
RUN turbo prune ${APP_NAME} --docker

# 3. Etapa de Instalación de dependencias
FROM base AS installer
WORKDIR /app
COPY --from=pruner /app/out/json/ .
COPY --from=pruner /app/out/pnpm-lock.yaml ./pnpm-lock.yaml
RUN pnpm install --frozen-lockfile

# 4. Etapa de Build (Compilación)
COPY --from=pruner /app/out/full/ .
COPY turbo.json turbo.json
ARG APP_NAME
RUN pnpm turbo run build --filter=${APP_NAME}

# 5. Etapa Final (Imagen que correrá en AWS)
FROM node:20-alpine AS runner
WORKDIR /app
ARG APP_NAME
ARG APP_PATH

# Copiamos lo compilado desde la etapa de installer
# Nota: APP_PATH será algo como "services/user-service"
COPY --from=installer /app/${APP_PATH}/dist ./dist
COPY --from=installer /app/${APP_PATH}/package.json ./package.json
COPY --from=installer /app/node_modules ./node_modules

# Comando para iniciar el microservicio
CMD ["node", "dist/main.js"]