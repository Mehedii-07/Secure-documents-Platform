# ============================================================
# Frontend Dockerfile — multi-stage build
# Stage 1: build  — Node + Vite build
# Stage 2: runtime — Nginx serves the SPA
# ============================================================

# ---- Stage 1: Build ----
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first (Docker layer cache — npm install only reruns when these change)
COPY package.json package-lock.json* ./

RUN npm ci --frozen-lockfile --quiet

# Copy source and build
COPY . .

# VITE_API_BASE_URL should be set at build time via --build-arg or .env
ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build


# ---- Stage 2: Runtime (Nginx) ----
FROM nginx:1.27-alpine AS runtime

LABEL maintainer="Platform Team"
LABEL description="AI-Powered Secure Document & Compliance Platform — Frontend"

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config (SPA routing support)
COPY nginx.conf /etc/nginx/conf.d/app.conf

# Copy built React app from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
