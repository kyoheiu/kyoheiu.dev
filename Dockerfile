FROM node:alpine AS build
WORKDIR /app
COPY . .
RUN npm i
RUN npm run build

FROM docker.io/lipanski/docker-static-website:latest
COPY --from=build /app/dist .
