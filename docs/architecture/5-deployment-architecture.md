# 5. Deployment Architecture

## Layers
- **Frontend**: React + Vite app deployed via custom Node server or nginx on EC2/GKE; CDN caching
- **API Layer**: FastAPI in Docker; separate WebSocket handler
- **Auth**: SuperTokens in containerized mode (standalone or integrated)
- **Messaging**: WebSocket server or Redis Pub/Sub
- **DB Layer**: PostgreSQL on RDS/CloudSQL; MongoDB Atlas or self-hosted
- **Storage**: AWS S3 with CloudFront

## DevOps
- GitHub-based repo
- CI/CD with GitHub Actions
- Dockerized microservices
- Helm-based deployments on K8s
- Prometheus + Grafana or Datadog
- Error tracking: Sentry