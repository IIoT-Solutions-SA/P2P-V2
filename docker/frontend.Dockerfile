# --- Stage 1: Base Image ---
    FROM node:20-alpine AS base
    WORKDIR /app
    
    # --- Stage 2: Development Stage (This was the missing part) ---
    FROM base AS development
    # Copy package files first to leverage Docker's build cache
    COPY ./p2p-frontend-app/package*.json ./
    # Install all dependencies
    RUN npm ci
    # Copy the rest of the application code
    COPY ./p2p-frontend-app/ .
    # Expose the Vite development port
    EXPOSE 5173
    # Command to run the development server
    CMD ["npm", "run", "dev", "--", "--host"]
    
    
    # --- Stage 3: Build Stage for Production ---
    FROM base AS build
    # This stage is only used when you target 'production'
    WORKDIR /app
    COPY ./p2p-frontend-app/package*.json ./
    RUN npm ci
    COPY ./p2p-frontend-app/ .
    RUN npm run build
    
    # --- Stage 4: Production Stage ---
    # This is the final, small image for deployment
    FROM nginx:1.25-alpine AS production
    COPY --from=build /app/dist /usr/share/nginx/html
    COPY ./docker/nginx.conf /etc/nginx/conf.d/default.conf
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]