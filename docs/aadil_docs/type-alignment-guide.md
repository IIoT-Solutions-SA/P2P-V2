# Type Alignment Guide: Frontend-Backend Integration

## Overview
This guide addresses the critical challenge of maintaining type consistency between the TypeScript frontend and Python backend in the P2P Sandbox platform. Proper type alignment prevents runtime errors and improves developer experience.

## Table of Contents
1. [Type System Differences](#type-system-differences)
2. [UUID Handling Strategy](#uuid-handling-strategy)
3. [Date and Time Management](#date-and-time-management)
4. [Enum Synchronization](#enum-synchronization)
5. [Naming Convention Mapping](#naming-convention-mapping)
6. [Shared Type Definitions](#shared-type-definitions)
7. [Validation Strategies](#validation-strategies)
8. [Type Transformation Patterns](#type-transformation-patterns)

## Type System Differences

### Python (Backend) vs TypeScript (Frontend)

| Python Type | TypeScript Type | Notes |
|------------|-----------------|-------|
| UUID | string | UUIDs are strings in JSON |
| datetime | string \| Date | ISO 8601 strings in transit |
| Decimal | number | Precision considerations |
| None | null \| undefined | Semantic differences |
| Dict[str, Any] | Record<string, any> | Object mapping |
| List[T] | T[] | Array handling |
| Tuple[A, B] | [A, B] | Fixed-length arrays |
| Optional[T] | T \| null \| undefined | Nullable handling |

### Key Considerations

1. **JSON Serialization**
   - Python objects must be JSON-serializable
   - Complex types need custom encoders
   - Frontend receives JSON, not Python objects

2. **Type Safety**
   - TypeScript provides compile-time checking
   - Python uses runtime validation (Pydantic/SQLModel)
   - Both systems should validate independently

## UUID Handling Strategy

### The Challenge
- Backend: Uses Python's UUID type
- Frontend: Receives UUIDs as strings
- Database: Stores as UUID type

### Recommended Approach

1. **Backend Serialization**
   - Always serialize UUIDs to strings in API responses
   - Accept both UUID and string formats in requests
   - Use Pydantic's UUID validation

2. **Frontend Handling**
   - Define UUID as string type in TypeScript
   - Use regex validation for UUID format
   - Consider branded types for extra safety

3. **Type Definition Example**
   ```typescript
   // Frontend
   type UUID = string; // Consider: type UUID = string & { __brand: "UUID" };
   
   interface User {
     id: UUID;
     organizationId: UUID;
   }
   ```

   ```python
   # Backend
   from uuid import UUID
   from sqlmodel import Field
   
   class User(SQLModel):
       id: UUID = Field(default_factory=uuid4)
       organization_id: UUID
   ```

## Date and Time Management

### Serialization Strategy

1. **Backend to Frontend**
   - Serialize all datetimes to ISO 8601 strings
   - Include timezone information (UTC recommended)
   - Use consistent format: `YYYY-MM-DDTHH:mm:ss.sssZ`

2. **Frontend to Backend**
   - Send dates as ISO 8601 strings
   - Backend parses using Pydantic validators
   - Handle timezone conversions server-side

3. **Frontend Date Handling**
   - Parse ISO strings to Date objects when needed
   - Display in user's local timezone
   - Store as strings until manipulation needed

### Common Patterns

```typescript
// Frontend utility functions
const parseAPIDate = (dateString: string): Date => new Date(dateString);
const formatForAPI = (date: Date): string => date.toISOString();

// Type definitions
interface TimeStamped {
  createdAt: string; // ISO 8601
  updatedAt: string; // ISO 8601
}
```

## Enum Synchronization

### The Challenge
- Backend enums (Python Enum or string literals)
- Frontend enums (TypeScript enums or union types)
- Must stay synchronized across codebases

### Recommended Strategy

1. **Define Enums in Both Systems**
   ```python
   # Backend
   from enum import Enum
   
   class UserRole(str, Enum):
       ADMIN = "admin"
       MEMBER = "member"
   
   class OrganizationSize(str, Enum):
       STARTUP = "startup"
       SMALL = "small"
       MEDIUM = "medium"
       LARGE = "large"
       ENTERPRISE = "enterprise"
   ```

   ```typescript
   // Frontend
   export type UserRole = "admin" | "member";
   export type OrganizationSize = "startup" | "small" | "medium" | "large" | "enterprise";
   ```

2. **Validation**
   - Backend validates using Pydantic
   - Frontend validates using TypeScript types
   - Consider runtime validation on frontend

3. **Maintenance**
   - Document all enums in a central location
   - Use code generation if possible
   - Add tests to ensure synchronization

## Naming Convention Mapping

### Python to TypeScript Conventions

| Backend (Python) | Frontend (TypeScript) | Context |
|-----------------|----------------------|---------|
| snake_case | camelCase | Properties |
| PascalCase | PascalCase | Classes/Types |
| UPPER_CASE | UPPER_CASE | Constants |
| _private | private/# | Private members |

### Transformation Strategy

1. **API Layer**
   - Transform at the API boundary
   - Backend sends snake_case
   - Frontend converts to camelCase

2. **Transformation Functions**
   ```typescript
   // Utility to convert snake_case to camelCase
   const snakeToCamel = (str: string): string =>
     str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
   
   // Deep transformation for objects
   const transformKeys = (obj: any): any => {
     // Implementation for nested object transformation
   };
   ```

3. **Type Mapping**
   ```typescript
   // Backend response type
   interface BackendUser {
     first_name: string;
     last_name: string;
     organization_id: string;
     is_active: boolean;
   }
   
   // Frontend type
   interface User {
     firstName: string;
     lastName: string;
     organizationId: string;
     isActive: boolean;
   }
   ```

## Shared Type Definitions

### Strategies for Type Sharing

1. **Manual Synchronization**
   - Maintain types in both codebases
   - Document in a central location
   - Regular audits for consistency

2. **Code Generation**
   - Generate TypeScript from OpenAPI schema
   - Use tools like openapi-typescript
   - Automate in CI/CD pipeline

3. **Shared Schema Repository**
   - Central repository for schemas
   - Import into both projects
   - Version control for changes

### Recommended Structure

```
shared-types/
├── schemas/
│   ├── user.schema.json
│   ├── organization.schema.json
│   └── forum.schema.json
├── generate-types.sh
└── README.md
```

## Validation Strategies

### Multi-Layer Validation

1. **Frontend Validation**
   - TypeScript compile-time checking
   - Runtime validation with Zod or Yup
   - Form-level validation
   - Optimistic UI updates

2. **Backend Validation**
   - Pydantic/SQLModel automatic validation
   - Custom validators for business logic
   - Database constraints
   - Return detailed error messages

3. **Validation Sync**
   - Share validation rules where possible
   - Document all validation requirements
   - Test validation on both sides

### Error Format Standardization

```typescript
interface ValidationError {
  message: string;
  field?: string;
  code: string;
  details?: Record<string, any>;
}

interface APIError {
  message: string;
  errors?: ValidationError[];
  statusCode: number;
}
```

## Type Transformation Patterns

### Common Transformation Scenarios

1. **Nested Objects**
   - Backend: Flat structure with IDs
   - Frontend: Nested for UI convenience
   - Transform at the service layer

2. **Pagination**
   ```typescript
   // Backend response
   interface BackendPaginated<T> {
     items: T[];
     total: number;
     page: number;
     page_size: number;
   }
   
   // Frontend transformed
   interface Paginated<T> {
     items: T[];
     total: number;
     page: number;
     pageSize: number;
     totalPages: number;
   }
   ```

3. **File Handling**
   - Backend: File metadata with S3 URLs
   - Frontend: File objects with preview
   - Transform for UI requirements

### Best Practices

1. **Type Guards**
   ```typescript
   const isUser = (obj: any): obj is User => {
     return obj && 
            typeof obj.id === 'string' &&
            typeof obj.email === 'string';
   };
   ```

2. **Transformation Layer**
   - Centralize all transformations
   - Make transformations pure functions
   - Test transformation logic thoroughly

3. **Documentation**
   - Document all type mappings
   - Explain transformation rationale
   - Provide examples for complex cases

## Implementation Checklist

- [ ] Define UUID type strategy
- [ ] Establish date/time format standards
- [ ] Create enum mapping documentation
- [ ] Implement key transformation utilities
- [ ] Set up validation on both ends
- [ ] Create type transformation layer
- [ ] Document all type mappings
- [ ] Add type synchronization tests
- [ ] Consider code generation tools
- [ ] Establish type review process

## Common Pitfalls

1. **Assuming Direct Mapping**
   - JSON limitations affect type transfer
   - Not all Python types have JS equivalents

2. **Ignoring Nullability**
   - Python None vs JS null/undefined
   - Optional fields need careful handling

3. **Date Timezone Issues**
   - Always use UTC in API
   - Convert to local time in UI only

4. **Number Precision**
   - JavaScript number limitations
   - Use strings for high precision

5. **Array vs Tuple**
   - TypeScript tuples are just arrays
   - Length validation needed