# -------- Stage 1: Builder --------
FROM node:23 AS builder
WORKDIR /app
COPY package.json ./
RUN yarn install --ignore-engines
COPY . .
RUN yarn build

# -------- Stage 2: Final Image for Production --------
FROM node:23 AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
# Copy only production dependencies if needed
COPY package.json ./
RUN yarn install --only=production --ignore-engines

EXPOSE ${PORT:-8080}

#ENV VITE_APP_BACKEND_URL=https://backend-ai-photo.onrender.com:10000

# Default production command (can be overridden in docker-compose)
#CMD ["yarn", "serve"]
CMD ["yarn", "start"]