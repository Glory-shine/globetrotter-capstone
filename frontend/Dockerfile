# ---- Build stage -----------------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app

# The backend gateway URL is baked into the static build at build time
# (Vite env vars are compile-time, not runtime). Override with
# --build-arg VITE_API_BASE_URL=... for a non-default deployment; the
# docker-compose service below passes the value that matches its own
# gateway port.
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---- Serve stage -------------------------------------------------------
FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
