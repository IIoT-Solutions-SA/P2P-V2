# Story 1: Repository Initialization and Project Structure

## Story Details
**Epic**: Epic 1 - Project Foundation & Development Environment  
**Story Points**: 2  
**Priority**: Critical (Must be completed first)

## User Story
**As a** developer  
**I want** a well-organized repository structure  
**So that** I can easily navigate and understand the codebase

## Acceptance Criteria
- [x] Git repository initialized with comprehensive .gitignore
- [x] Clear folder structure separating frontend, backend, and infrastructure
- [x] README.md with project overview and quick start guide
- [x] LICENSE file and contribution guidelines
- [x] Environment variable templates for all services
- [x] Development documentation structure in place

## Technical Specifications

### 1. Repository Structure
Create the following directory structure:
```
p2p-sandbox/
├── frontend/               # React + Vite application
│   ├── src/
│   ├── public/
│   ├── tests/
│   └── package.json
├── backend/                # FastAPI application
│   ├── app/
│   ├── tests/
│   └── requirements.txt
├── infrastructure/         # Docker and deployment configs
│   ├── docker/
│   ├── kubernetes/
│   └── scripts/
├── docs/                   # Project documentation
│   ├── architecture/
│   ├── api/
│   ├── deployment/
│   └── development/
├── .github/               # GitHub specific files
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── docker-compose.yml     # Local development orchestration
├── .gitignore
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

### 2. Git Configuration

#### .gitignore Content
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
dist/
build/
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Docker
.docker/

# Logs
logs/
*.log

# Database
*.db
*.sqlite3
data/
```

### 3. README.md Template
```markdown
# P2P Sandbox for SMEs

A peer-driven collaboration platform for Saudi Arabia's industrial small and medium enterprises, facilitating operational problem-solving, peer mentoring, and access to practical 4IR case studies.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Node.js 18+
- Python 3.11+
- Git

### Setup
1. Clone the repository
   ```bash
   git clone https://github.com/[org]/p2p-sandbox.git
   cd p2p-sandbox
   ```

2. Copy environment files
   ```bash
   cp .env.example .env
   cp frontend/.env.example frontend/.env
   cp backend/.env.example backend/.env
   ```

3. Start all services
   ```bash
   docker-compose up -d
   ```

4. Access the application
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📚 Documentation
- [Architecture Overview](./docs/architecture/README.md)
- [API Documentation](./docs/api/README.md)
- [Development Guide](./docs/development/README.md)
- [Deployment Guide](./docs/deployment/README.md)

## 🛠 Tech Stack
- **Frontend**: React, Vite, Tailwind CSS, shadcn/ui
- **Backend**: Python, FastAPI, PostgreSQL, MongoDB
- **Auth**: SuperTokens
- **Infrastructure**: Docker, GitHub Actions

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

### 4. Environment Templates

#### .env.example (root)
```env
# Environment
NODE_ENV=development
COMPOSE_PROJECT_NAME=p2p-sandbox

# Service URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
SUPERTOKENS_URL=http://localhost:3567

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=p2p_sandbox
POSTGRES_USER=p2p_user
POSTGRES_PASSWORD=changeme

MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_DATABASE=p2p_sandbox
MONGODB_USERNAME=p2p_user
MONGODB_PASSWORD=changeme
```

#### frontend/.env.example
```env
VITE_API_URL=http://localhost:8000
VITE_SUPERTOKENS_APP_NAME=P2P-Sandbox
VITE_SUPERTOKENS_API_DOMAIN=http://localhost:8000
VITE_SUPERTOKENS_WEBSITE_DOMAIN=http://localhost:3000
```

#### backend/.env.example
```env
# API Configuration
API_TITLE=P2P Sandbox API
API_VERSION=1.0.0
DEBUG=True

# Database URLs
DATABASE_URL=postgresql://p2p_user:changeme@postgres:5432/p2p_sandbox
MONGODB_URL=mongodb://p2p_user:changeme@mongodb:27017/p2p_sandbox

# SuperTokens
SUPERTOKENS_CONNECTION_URI=http://supertokens:3567
SUPERTOKENS_API_KEY=changeme

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Security
SECRET_KEY=your-secret-key-here
```

### 5. CONTRIBUTING.md
```markdown
# Contributing to P2P Sandbox

## Code of Conduct
Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Development Process
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Coding Standards
- **Python**: Follow PEP 8, use Black for formatting
- **JavaScript/TypeScript**: Use ESLint and Prettier
- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/)

## Testing
- Write tests for all new features
- Ensure all tests pass before submitting PR
- Maintain or improve code coverage
```

### 6. GitHub Templates

#### .github/PULL_REQUEST_TEMPLATE.md
```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## Implementation Steps

1. **Initialize Git Repository**
   ```bash
   git init
   git branch -M main
   ```

2. **Create Directory Structure**
   ```bash
   mkdir -p frontend/src frontend/public frontend/tests
   mkdir -p backend/app backend/tests
   mkdir -p infrastructure/docker infrastructure/kubernetes infrastructure/scripts
   mkdir -p docs/architecture docs/api docs/deployment docs/development
   mkdir -p .github/workflows .github/ISSUE_TEMPLATE
   ```

3. **Create All Configuration Files**
   - Copy all templates above to their respective locations
   - Ensure all files have proper formatting

4. **Initial Commit**
   ```bash
   git add .
   git commit -m "Initial repository structure and configuration"
   ```

## Testing Checklist
- [ ] All directories created successfully
- [ ] .gitignore properly excludes development files
- [ ] Environment templates contain all necessary variables
- [ ] README provides clear setup instructions
- [ ] GitHub templates are properly formatted

## Documentation Requirements
- Update README.md as new features are added
- Keep environment variable documentation current
- Document any deviations from the initial structure

## Dependencies
None - this is the first story and has no dependencies

## Blockers
- GitHub repository must be created by the user first
- Team agreement on licensing (defaulting to MIT)