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

## Code Writing Requirements

### Ref MCP Tool Usage

When writing any code for this project, Claude MUST:

1. **Always Use Ref MCP Tool**: Before writing any code, consult the Ref MCP tool to ensure using the latest and most up-to-date:
   - Language features and syntax
   - Framework versions and best practices
   - Security patterns and recommendations
   - Performance optimizations

2. **Verify Current Practices**: Check for:
   - Latest React 19 patterns and hooks
   - Current FastAPI async patterns
   - Modern TypeScript features
   - Updated library APIs

3. **Implementation Process**:
   - First, query Ref for current best practices
   - Verify version compatibility with project dependencies
   - Implement using the most recent recommended patterns
   - Document any significant updates or changes

### Example Workflow:
1. Before implementing a React component → Check latest React patterns
2. Before writing FastAPI endpoints → Verify current async best practices
3. Before database operations → Confirm latest SQLModel usage patterns

### Semgrep Security Scanning

When writing any code for this project, Claude MUST:

1. **Always Run Security Scans**: After writing any code, use Semgrep via the Bash tool to scan for:
   - Security vulnerabilities (OWASP Top 10)
   - Authentication and authorization issues
   - Injection vulnerabilities (SQL, NoSQL, Command)
   - Cross-site scripting (XSS) risks
   - Insecure data exposure
   - Configuration security issues

2. **Fix Identified Issues**: When Semgrep identifies security issues:
   - Address all high and critical severity findings immediately
   - Document why medium/low severity issues are acceptable if not fixed
   - Re-scan after fixes to ensure issues are resolved

3. **Security Scanning Process**:
   - Write the initial code implementation
   - Run Semgrep scan using: `~/.local/bin/semgrep --config=auto <file_or_directory>`
   - Review and fix any security findings
   - Document any security considerations in comments

### Security Workflow Example:
1. After implementing API endpoints → `~/.local/bin/semgrep --config=auto app/api/`
2. After authentication code → `~/.local/bin/semgrep --config=auto app/auth/`
3. After file handling code → `~/.local/bin/semgrep --config=auto --pattern 'path.join'`
4. After database queries → `~/.local/bin/semgrep --config=auto --pattern 'execute|query'`

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
2. **Exhaustive Commit Messages**: Each commit must have a detailed message that explains:
   - **WHAT**: What changes were made
   - **WHY**: Why the changes were necessary
   - **HOW**: How the changes were implemented
3. **Message Format**: Use conventional commit format with detailed description:
   ```
   type: brief summary
   
   WHAT: Detailed description of changes made
   WHY: Reason for making these changes
   HOW: Implementation approach and any important details
   ```

### Commit Message Examples:
```
docs: add comprehensive frontend-backend integration guide

WHAT: Created a detailed guide covering frontend-backend integration including dependencies, 
environment setup, API client configuration, authentication flow, error handling, and testing strategies
WHY: Frontend currently uses mock data and needs proper integration with the FastAPI backend. 
Developers need clear guidance on how to connect the two systems
HOW: Documented required npm packages, environment variables, CORS configuration, SuperTokens setup, 
and provided testing checklists for verifying integration
```

```
feat: implement type alignment strategy between frontend and backend

WHAT: Added comprehensive documentation for handling type differences between TypeScript and Python
WHY: Type mismatches between frontend and backend can cause runtime errors. UUID, date, and enum 
handling needs standardization
HOW: Created mapping tables, transformation strategies, and validation approaches for consistent 
type handling across the stack
```

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