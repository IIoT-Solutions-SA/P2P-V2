# System Architecture: P2P Sandbox for SMEs

## 1. System Overview

The P2P Sandbox for SMEs is a secure, cloud-native collaboration platform that empowers Saudi Arabian industrial SMEs to exchange knowledge, showcase digital transformation use cases, and co-develop training initiatives. It enables verified users—factory owners, plant engineers, and operations managers—to share insights, solve problems, and access 4IR case studies within a trusted, community-driven environment.

The platform is architected as a modular full-stack web application, designed for scalability, extensibility, and rapid iteration. It follows a three-tier architecture:

- **Frontend (Presentation Layer)**: React + Vite-based, i18n-ready, optimized for desktop/mobile.
- **Backend (Business Logic Layer)**: FastAPI with SuperTokens for authentication.
- **Database & Storage (Persistence Layer)**: PostgreSQL, MongoDB, and S3-compatible object storage.

---

## 2. Tech Stack

### Frontend:
- React.js + Vite
- Tailwind CSS + shadcn/ui
- i18n localization (Arabic/English)
- SuperTokens frontend SDK
- Leaflet.js + OpenStreetMap (for interactive Saudi Arabia map)

### Backend:
- Python + FastAPI
- RESTful API (OpenAPI schema)
- SuperTokens for session management and auth
- WebSockets (FastAPI-native or external)

### Data Layer:
- PostgreSQL (core relational data)
- MongoDB (nested forum content, case study metadata)
- AWS S3 / Azure Blob Storage (media files)

### Infrastructure:
- Docker + Kubernetes (EKS, GKE)
- GitHub Actions (CI/CD)
- Prometheus + Grafana / Datadog (Monitoring)
- AWS/GCP/Azure for hosting

---

## 3. System Components & Services

1. **Frontend Client**: React + Vite SPA with route-level auth, dashboards, messaging, and interactive landing page with use case map.
2. **Authentication Service**: SuperTokens for JWT, email login, password reset, OAuth.
3. **Forum Service**: Topic-based discussions, replies, attachments, best answer tagging.
4. **Use Case Library**: Structured case studies with filters, bookmarks, feedback, and geolocation for map display.
5. **Messaging Service**: WebSocket/private messaging and optional notifications.
6. **Training Collaboration Module**: Coordinate training needs with peers/providers.
7. **Admin Dashboard**: Monitor engagement, content performance, and user trends.
8. **Notifications System**: In-app + email updates for posts, replies, and DMs.

---

## 4. Core Data Models

### User
- id, name, email, role, industry_sector, location, expertise_tags, verified, language_preference, timestamps

### ForumPost
- id, author_id, title, content, category, attachments, best_answer_id, status, timestamps

### ForumReply
- id, post_id, author_id, content, attachments, upvotes, timestamps

### UseCase
- id, submitted_by, title, problem_statement, solution_description, vendor_info, cost_estimate, impact_metrics, industry_tags, region, location {lat, lng}, bookmarks, published, featured

### MessageThread
- id, user_ids, messages [{sender_id, content, timestamp}]

### TrainingPost
- id, creator_id, title, description, skill_topic, location, schedule, interested_users, matched_provider_id

---

## 5. Deployment Architecture

### Layers
- **Frontend**: React + Vite app deployed via custom Node server or nginx on EC2/GKE; CDN caching
- **API Layer**: FastAPI in Docker; separate WebSocket handler
- **Auth**: SuperTokens in containerized mode (standalone or integrated)
- **Messaging**: WebSocket server or Redis Pub/Sub
- **DB Layer**: PostgreSQL on RDS/CloudSQL; MongoDB Atlas or self-hosted
- **Storage**: AWS S3 with CloudFront

### DevOps
- GitHub-based repo
- CI/CD with GitHub Actions
- Dockerized microservices
- Helm-based deployments on K8s
- Prometheus + Grafana or Datadog
- Error tracking: Sentry