# build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# you can supply VITE_* env variables during build
ARG VITE_ML_URL
ARG VITE_BACKEND_URL
ENV VITE_ML_URL=${VITE_ML_URL}
ENV VITE_BACKEND_URL=${VITE_BACKEND_URL}
RUN npm run build

# production stage
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# use custom configuration to proxy API calls
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]