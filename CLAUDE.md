# P2P Sandbox Project Context

## Project Overview

P2P Sandbox is a peer-driven collaboration platform for Saudi Arabia's industrial SMEs, featuring forums, use case submissions, and knowledge sharing capabilities.

**Tech Stack:**
- Frontend: React + TypeScript + Vite + TailwindCSS + shadcn/ui
- Backend: FastAPI (Python) with Async/Await
- Databases: PostgreSQL (async with AsyncPG) + MongoDB (async with Motor)
- Authentication: SuperTokens
- File Storage: AWS S3 / Azure Blob Storage

## Project Structure

```
P2P-V2/
├── docs/                      # Project documentation
│   ├── aadil_docs/           # Backend development guides
│   ├── architecture/         # System architecture docs
│   ├── epics/               # Project epics
│   ├── prd/                 # Product requirement docs
│   └── stories/             # User stories by epic
├── p2p-frontend-app/         # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── contexts/        # React contexts (Auth)
│   │   ├── pages/           # Page components
│   │   └── types/           # TypeScript types
│   └── package.json
└── p2p-backend-app/          # FastAPI backend (to be implemented)
    ├── requirements.txt
    └── venv/
```

## Current Development Status

- **Frontend**: Fully implemented with mock data
- **Backend**: Planning phase - async FastAPI implementation pending
- **Branch**: `aadil-backend` (current working branch)

## Backend Development Guidelines

### Async Programming Strategy

All backend code should use async/await patterns for:
- Database operations (AsyncPG for PostgreSQL, Motor for MongoDB)
- File uploads to S3/Azure
- External API calls
- WebSocket connections for real-time features

### API Development Standards

1. **Endpoint Structure**: `/api/v1/{resource}`
2. **Authentication**: All endpoints except auth require SuperTokens session
3. **Response Format**: Consistent JSON structure with proper error handling
4. **Testing**: Write async tests for all endpoints

### Database Schema

**PostgreSQL** (Relational data):
- Users, Organizations, Forum Topics, Messages, Use Case Submissions

**MongoDB** (Document data):
- Forum Posts (with nested replies)
- Use Cases (detailed content with media)
- Activity Logs

### Key Implementation Tasks

1. **Authentication System**
   - SuperTokens integration
   - Organization-based signup
   - Session management

2. **Core Features**
   - Forum system with WebSocket support
   - Use case submission with file uploads
   - User management within organizations
   - Dashboard statistics API

3. **Testing Requirements**
   - Unit tests for all services
   - Integration tests for API endpoints
   - Frontend-backend integration tests
   - Performance tests for async operations

## Documentation Guidelines

When working in the `/docs` folder:
- Follow existing markdown structure
- Update architecture docs when making system changes
- Keep user stories aligned with implementation

## Frontend Integration Points

Key areas requiring backend integration:
- `AuthContext.tsx`: Replace mock auth with API calls
- `Dashboard.tsx`: Connect to real statistics API
- `UseCases.tsx`: Load from backend instead of JSON file
- `Forum.tsx`: Implement real-time updates via WebSocket

## Testing Commands

```bash
# Backend tests (once implemented)
cd p2p-backend-app
pytest

# Frontend tests
cd p2p-frontend-app
npm test
```

## Development Workflow

1. Always work on the `aadil-backend` branch
2. Test API endpoints with frontend before committing
3. Update this file when adding major features
4. Follow async best practices for all I/O operations

## Version Control Requirements for Claude

When making any changes to the project, Claude MUST follow these version control practices:

### Commit Workflow
1. **Every Change Must Be Committed**: No matter how small, every file modification must be committed
2. **Clear Commit Messages**: Each commit must have a descriptive message following this format:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `refactor:` for code restructuring
   - `test:` for test additions/changes
   - `chore:` for maintenance tasks

### Commit Message Examples:
- `docs: add frontend-backend integration guide`
- `feat: create type alignment documentation`
- `fix: update CORS configuration in backend plan`
- `refactor: reorganize authentication flow guide`

### Required Git Commands:
After making changes, always execute:
```bash
# Add all changes
git add .

# Commit with clear message
git commit -m "type: descriptive message explaining the change"

# Push to current branch (aadil-backend)
git push origin aadil-backend
```

### Important Rules:
- Never make changes without committing
- Always push to the remote branch after committing
- If making multiple related changes, commit them separately with clear messages
- Each commit should represent one logical change

## Important Notes

- Never store credentials in code
- Use environment variables for configuration
- Follow REST API conventions
- Implement proper CORS for frontend integration
- Use structured logging for debugging

## Resources

- Backend Plan: `/docs/aadil_docs/unified-backend-development-plan.md`
- Async Guide: `/docs/aadil_docs/async-implementation-guide.md`
- Testing Plan: `/docs/aadil_docs/comprehensive-testing-plan.md`
- Architecture: `/docs/architecture/`

## Developer-Specific Context

For developer-specific guidelines and personal notes, reference:
- Aadil's Backend Context: `/docs/aadil_docs/aadil-backend-context.md`