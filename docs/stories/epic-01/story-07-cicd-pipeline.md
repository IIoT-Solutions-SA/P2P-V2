# Story 7: CI/CD Pipeline Foundation

## Story Details
**Epic**: Epic 1 - Project Foundation & Development Environment  
**Story Points**: 6  
**Priority**: High  
**Dependencies**: Story 6 (Docker Containerization)

## User Story
**As a** team lead  
**I want** automated testing and deployment pipelines  
**So that** code quality is maintained and deployments are reliable

## Acceptance Criteria
- [ ] GitHub Actions workflow for PR validation
- [ ] Automated linting for frontend and backend code
- [ ] Unit test execution in CI pipeline with coverage reporting
- [ ] Build verification for all components
- [ ] Docker image building and registry push
- [ ] Basic deployment workflow structure
- [ ] Security scanning for dependencies and containers
- [ ] Notification system for build failures
- [ ] Branch protection rules configured

## Technical Specifications

### 1. GitHub Actions Workflows

#### .github/workflows/pr-validation.yml
```yaml
name: PR Validation

on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main, develop ]

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'

jobs:
  # Frontend validation
  frontend-validation:
    name: Frontend Validation
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
        
    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci
      
    - name: Run linting
      working-directory: ./frontend
      run: npm run lint
      
    - name: Run type checking
      working-directory: ./frontend
      run: npm run type-check
      
    - name: Run tests
      working-directory: ./frontend
      run: npm run test:ci
      
    - name: Build application
      working-directory: ./frontend
      run: npm run build
      
    - name: Upload build artifacts
      uses: actions/upload-artifact@v4
      with:
        name: frontend-build
        path: frontend/dist
        retention-days: 7

  # Backend validation
  backend-validation:
    name: Backend Validation
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_USER: test_user
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
          
      mongodb:
        image: mongo:7
        env:
          MONGO_INITDB_ROOT_USERNAME: test_user
          MONGO_INITDB_ROOT_PASSWORD: test_password
        options: >-
          --health-cmd "mongosh --eval 'db.adminCommand(\"ping\")'"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 27017:27017
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'
        cache-dependency-path: backend/requirements-dev.txt
        
    - name: Install dependencies
      working-directory: ./backend
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
        
    - name: Run linting (flake8)
      working-directory: ./backend
      run: flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
      
    - name: Run code formatting check (black)
      working-directory: ./backend
      run: black --check app/
      
    - name: Run import sorting check (isort)
      working-directory: ./backend
      run: isort --check-only app/
      
    - name: Run type checking (mypy)
      working-directory: ./backend
      run: mypy app/
      
    - name: Run tests with coverage
      working-directory: ./backend
      env:
        DATABASE_URL: postgresql+asyncpg://test_user:test_password@localhost:5432/test_db
        MONGODB_URL: mongodb://test_user:test_password@localhost:27017/test_db?authSource=admin
        SUPERTOKENS_CONNECTION_URI: http://localhost:3567
      run: |
        pytest --cov=app --cov-report=xml --cov-report=html --cov-report=term-missing
        
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        directory: ./backend
        flags: backend
        name: backend-coverage

  # Security scanning
  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
        
    - name: Run npm audit (frontend)
      working-directory: ./frontend
      run: |
        npm ci
        npm audit --audit-level=moderate
        
    - name: Run pip safety check (backend)
      working-directory: ./backend
      run: |
        pip install safety
        safety check -r requirements.txt

  # Docker build validation
  docker-validation:
    name: Docker Build Validation
    runs-on: ubuntu-latest
    needs: [frontend-validation, backend-validation]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Build frontend Docker image
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        file: ./frontend/Dockerfile
        target: production
        push: false
        tags: p2p-frontend:test
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    - name: Build backend Docker image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        file: ./backend/Dockerfile
        target: production
        push: false
        tags: p2p-backend:test
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    - name: Test Docker Compose
      run: |
        cp .env.example .env
        docker-compose -f docker-compose.yml config
```

#### .github/workflows/deploy-staging.yml
```yaml
name: Deploy to Staging

on:
  push:
    branches: [ develop ]
    
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-deploy:
    name: Build and Deploy to Staging
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=sha,prefix={{branch}}-
          
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Build and push frontend image
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        file: ./frontend/Dockerfile
        target: production
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend:${{ github.sha }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    - name: Build and push backend image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        file: ./backend/Dockerfile
        target: production
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:${{ github.sha }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    # Add deployment steps here when staging environment is ready
    - name: Deploy to staging (placeholder)
      run: |
        echo "Deployment to staging would happen here"
        echo "Images built:"
        echo "- Frontend: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend:${{ github.sha }}"
        echo "- Backend: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:${{ github.sha }}"
```

#### .github/workflows/deploy-production.yml
```yaml
name: Deploy to Production

on:
  release:
    types: [published]
    
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-deploy:
    name: Build and Deploy to Production
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    environment: production
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=tag
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Build and push frontend image
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        file: ./frontend/Dockerfile
        target: production
        push: true
        tags: |
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend:${{ github.event.release.tag_name }}
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend:latest
        labels: ${{ steps.meta.outputs.labels }}
        
    - name: Build and push backend image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        file: ./backend/Dockerfile
        target: production
        push: true
        tags: |
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:${{ github.event.release.tag_name }}
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:latest
        labels: ${{ steps.meta.outputs.labels }}
        
    - name: Create deployment artifact
      run: |
        mkdir deployment
        cp docker-compose.prod.yml deployment/
        cp .env.example deployment/.env.template
        tar -czf deployment-${{ github.event.release.tag_name }}.tar.gz deployment/
        
    - name: Upload deployment artifact to release
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ github.event.release.upload_url }}
        asset_path: ./deployment-${{ github.event.release.tag_name }}.tar.gz
        asset_name: deployment-${{ github.event.release.tag_name }}.tar.gz
        asset_content_type: application/gzip
```

### 2. Frontend Package.json Updates

#### Add to frontend/package.json scripts:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --report-unused-disable-directives --fix",
    "type-check": "tsc --noEmit",
    "test": "vitest",
    "test:ci": "vitest run --coverage",
    "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx,js,jsx,json,css,md}\""
  },
  "devDependencies": {
    "vitest": "^1.2.0",
    "@vitest/ui": "^1.2.0",
    "jsdom": "^24.0.0"
  }
}
```

#### frontend/vitest.config.ts
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      reporter: ['text', 'html', 'clover', 'json']
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

### 3. Backend Development Dependencies

#### Update backend/pyproject.toml
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "p2p-sandbox-backend"
dynamic = ["version"]
description = "P2P Sandbox for SMEs Backend API"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["app"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers --strict-config --cov=app"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]

[tool.coverage.run]
source = ["app"]
omit = ["app/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
]
```

### 4. GitHub Repository Configuration

#### .github/dependabot.yml
```yaml
version: 2
updates:
  # Frontend dependencies
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "team-leads"
    
  # Backend dependencies
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "team-leads"
    
  # Docker dependencies
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    
  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

#### .github/CODEOWNERS
```
# Global owners
* @team-leads

# Frontend specific
/frontend/ @frontend-team @team-leads

# Backend specific
/backend/ @backend-team @team-leads

# Infrastructure and deployment
/infrastructure/ @devops-team @team-leads
/.github/ @devops-team @team-leads
/docker-compose*.yml @devops-team @team-leads

# Documentation
/docs/ @product-team @team-leads
/README.md @product-team @team-leads
```

#### .github/pull_request_template.md
```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## How Has This Been Tested?
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing
- [ ] End-to-end tests

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Screenshots (if applicable)

## Additional Notes
```

### 5. Pre-commit Hooks

#### .pre-commit-config.yaml
```yaml
repos:
  # Frontend hooks
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: ^frontend/.*\.(ts|tsx|js|jsx)$
        additional_dependencies:
          - '@typescript-eslint/eslint-plugin'
          - '@typescript-eslint/parser'
          - 'eslint-config-prettier'
        
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.3
    hooks:
      - id: prettier
        files: ^frontend/.*\.(ts|tsx|js|jsx|json|css|md)$
        
  # Backend hooks
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        files: ^backend/.*\.py$
        
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        files: ^backend/.*\.py$
        
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        files: ^backend/.*\.py$
        
  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
        
  # Docker hooks
  - repo: https://github.com/hadolint/hadolint
    rev: v2.12.0
    hooks:
      - id: hadolint
        files: Dockerfile
```

### 6. Monitoring and Notifications

#### .github/workflows/notify-deployments.yml
```yaml
name: Deployment Notifications

on:
  deployment_status:

jobs:
  notify:
    runs-on: ubuntu-latest
    if: github.event.deployment_status.state == 'success' || github.event.deployment_status.state == 'failure'
    
    steps:
    - name: Notify Slack
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ github.event.deployment_status.state }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        fields: repo,message,commit,author,action,eventName,ref,workflow
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Implementation Steps

1. **Create GitHub Actions Workflows**
   ```bash
   mkdir -p .github/workflows
   # Create all workflow files as specified above
   ```

2. **Configure Repository Settings**
   - Enable branch protection for main/develop branches
   - Require PR reviews and status checks
   - Enable Dependabot for security updates

3. **Set Up Secrets**
   ```bash
   # Add to GitHub repository secrets:
   # - DOCKERHUB_USERNAME
   # - DOCKERHUB_TOKEN
   # - SLACK_WEBHOOK (optional)
   # - Production environment variables
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Test CI/CD Pipeline**
   - Create a test PR to verify all checks pass
   - Test the build and deployment workflows

## Testing Checklist
- [ ] PR validation workflow runs successfully
- [ ] All linting and testing steps pass
- [ ] Docker images build without errors
- [ ] Security scanning completes
- [ ] Branch protection rules are enforced
- [ ] Pre-commit hooks run locally
- [ ] Dependabot creates update PRs
- [ ] Deployment workflows trigger correctly

## Security Considerations
- [ ] Secrets are stored securely in GitHub
- [ ] Container images are scanned for vulnerabilities
- [ ] Dependencies are regularly updated
- [ ] Access controls are properly configured
- [ ] Production deployments require manual approval

## Monitoring and Alerting
- [ ] Build failures trigger notifications
- [ ] Deployment status is tracked
- [ ] Performance metrics are collected
- [ ] Error tracking is implemented

## Dependencies
- Story 6 (Docker Containerization) must be completed
- GitHub repository must be created
- Team access and permissions configured

## Future Enhancements
- [ ] Integration with staging environments
- [ ] Automated performance testing
- [ ] Blue-green deployment strategies
- [ ] Canary release deployments
- [ ] Advanced monitoring and alerting
- [ ] Integration with project management tools

## Notes
- Keep workflows simple and focused
- Use caching to speed up builds
- Implement proper error handling and notifications
- Regular review and update of security scanning rules
- Monitor CI/CD performance and optimize as needed