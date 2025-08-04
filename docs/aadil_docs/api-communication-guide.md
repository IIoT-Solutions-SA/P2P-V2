# API Communication Guide for P2P Sandbox

## Overview
This guide establishes standards and best practices for API communication between the React frontend and FastAPI backend, ensuring consistent, reliable, and maintainable interactions.

## Table of Contents
1. [API Design Principles](#api-design-principles)
2. [Request/Response Standards](#requestresponse-standards)
3. [RESTful Conventions](#restful-conventions)
4. [Error Handling](#error-handling)
5. [Pagination Patterns](#pagination-patterns)
6. [File Upload Strategies](#file-upload-strategies)
7. [Real-time Communication](#real-time-communication)
8. [API Versioning](#api-versioning)
9. [Performance Optimization](#performance-optimization)
10. [Testing Strategies](#testing-strategies)

## API Design Principles

### Core Principles

1. **Consistency**
   - Uniform response structures
   - Predictable endpoint patterns
   - Standardized error formats
   - Consistent naming conventions

2. **Simplicity**
   - Clear resource names
   - Intuitive URL structures
   - Minimal nesting levels
   - Self-documenting endpoints

3. **Security**
   - Authentication on all endpoints
   - Input validation
   - Rate limiting
   - Secure data transmission

4. **Performance**
   - Efficient payload sizes
   - Proper caching headers
   - Pagination for lists
   - Compression support

## Request/Response Standards

### Request Format

1. **Headers**
   ```
   Content-Type: application/json
   Accept: application/json
   Accept-Language: en-US,ar-SA
   X-Request-ID: <unique-request-id>
   ```

2. **Body Structure**
   - Use JSON for all requests
   - Snake_case for field names
   - ISO 8601 for dates
   - UTF-8 encoding

3. **Query Parameters**
   - Filtering: `?status=active&type=admin`
   - Sorting: `?sort=created_at&order=desc`
   - Pagination: `?page=1&page_size=20`
   - Search: `?q=search+term`

### Response Format

1. **Success Response**
   ```json
   {
     "data": {
       // Resource data
     },
     "meta": {
       "timestamp": "2024-01-01T00:00:00Z",
       "request_id": "uuid",
       "version": "1.0"
     }
   }
   ```

2. **List Response**
   ```json
   {
     "data": {
       "items": [...],
       "pagination": {
         "page": 1,
         "page_size": 20,
         "total": 100,
         "total_pages": 5
       }
     },
     "meta": {...}
   }
   ```

3. **Error Response**
   ```json
   {
     "error": {
       "message": "Human readable error message",
       "code": "ERROR_CODE",
       "details": {
         "field": "Specific error detail"
       },
       "trace_id": "uuid"
     },
     "meta": {...}
   }
   ```

## RESTful Conventions

### Resource Naming

1. **URL Structure**
   - Use nouns, not verbs
   - Plural for collections
   - Singular for single resources
   - Lowercase with hyphens

2. **Examples**
   ```
   GET    /api/v1/users              # List users
   POST   /api/v1/users              # Create user
   GET    /api/v1/users/{id}         # Get single user
   PATCH  /api/v1/users/{id}         # Update user
   DELETE /api/v1/users/{id}         # Delete user
   
   GET    /api/v1/users/{id}/posts   # User's posts
   POST   /api/v1/forum-topics       # Create forum topic
   ```

### HTTP Methods

| Method | Usage | Idempotent | Safe |
|--------|-------|------------|------|
| GET | Retrieve resource(s) | Yes | Yes |
| POST | Create new resource | No | No |
| PUT | Replace entire resource | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Remove resource | Yes | No |

### Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## Error Handling

### Error Response Structure

```json
{
  "error": {
    "message": "Email already registered",
    "code": "DUPLICATE_EMAIL",
    "details": {
      "email": "This email is already in use"
    },
    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Error Codes

1. **Authentication Errors**
   - `INVALID_CREDENTIALS`
   - `SESSION_EXPIRED`
   - `INVALID_TOKEN`
   - `ACCOUNT_LOCKED`

2. **Validation Errors**
   - `VALIDATION_ERROR`
   - `REQUIRED_FIELD_MISSING`
   - `INVALID_FORMAT`
   - `VALUE_OUT_OF_RANGE`

3. **Business Logic Errors**
   - `DUPLICATE_ENTRY`
   - `INSUFFICIENT_PERMISSIONS`
   - `RESOURCE_LOCKED`
   - `QUOTA_EXCEEDED`

4. **System Errors**
   - `INTERNAL_ERROR`
   - `SERVICE_UNAVAILABLE`
   - `TIMEOUT_ERROR`
   - `RATE_LIMIT_EXCEEDED`

### Frontend Error Handling

1. **Global Error Handler**
   - Intercept all API errors
   - Show user-friendly messages
   - Log for debugging
   - Report critical errors

2. **Specific Error Handling**
   - Form validation errors
   - Network connectivity
   - Session expiration
   - Permission denied

## Pagination Patterns

### Offset-Based Pagination

1. **Request**
   ```
   GET /api/v1/users?page=2&page_size=20
   ```

2. **Response**
   ```json
   {
     "data": {
       "items": [...],
       "pagination": {
         "page": 2,
         "page_size": 20,
         "total": 100,
         "total_pages": 5,
         "has_next": true,
         "has_previous": true
       }
     }
   }
   ```

### Cursor-Based Pagination

1. **Request**
   ```
   GET /api/v1/posts?cursor=eyJpZCI6MTAwfQ&limit=20
   ```

2. **Response**
   ```json
   {
     "data": {
       "items": [...],
       "pagination": {
         "next_cursor": "eyJpZCI6MTIwfQ",
         "previous_cursor": "eyJpZCI6ODB9",
         "has_more": true
       }
     }
   }
   ```

### Best Practices

- Default page size: 20
- Maximum page size: 100
- Include total count for UI
- Use cursor for real-time data
- Cache paginated results

## File Upload Strategies

### Direct Upload

1. **Single File**
   ```
   POST /api/v1/upload
   Content-Type: multipart/form-data
   
   file: <binary data>
   ```

2. **Multiple Files**
   ```
   POST /api/v1/upload/batch
   Content-Type: multipart/form-data
   
   files[]: <binary data>
   files[]: <binary data>
   ```

### Presigned URL Pattern

1. **Request Upload URL**
   ```
   POST /api/v1/upload/prepare
   {
     "filename": "document.pdf",
     "content_type": "application/pdf",
     "size": 1048576
   }
   ```

2. **Response**
   ```json
   {
     "upload_url": "https://s3.amazonaws.com/...",
     "file_id": "uuid",
     "expires_at": "2024-01-01T01:00:00Z"
   }
   ```

3. **Confirm Upload**
   ```
   POST /api/v1/upload/confirm
   {
     "file_id": "uuid"
   }
   ```

### Upload Progress

- Use XMLHttpRequest for progress
- Show percentage complete
- Handle upload cancellation
- Implement retry logic

## Real-time Communication

### WebSocket Protocol

1. **Connection**
   ```
   ws://localhost:8000/ws/forum/{topic_id}
   Authorization: Bearer <token>
   ```

2. **Message Format**
   ```json
   {
     "type": "message|typing|presence",
     "data": {
       // Message-specific data
     },
     "timestamp": "2024-01-01T00:00:00Z"
   }
   ```

### Event Types

1. **Forum Events**
   - `new_post`
   - `post_edited`
   - `post_deleted`
   - `user_typing`

2. **Notification Events**
   - `new_message`
   - `mention`
   - `activity_update`

### Connection Management

- Automatic reconnection
- Exponential backoff
- Heartbeat/ping-pong
- Connection state tracking

## API Versioning

### URL Versioning Strategy

```
/api/v1/users
/api/v2/users  # New version
```

### Version Management

1. **Deprecation Policy**
   - 6-month deprecation notice
   - Migration guide provided
   - Sunset headers in responses
   - Monitoring old version usage

2. **Breaking Changes**
   - New version required
   - Clear documentation
   - Migration tools
   - Parallel operation period

### Version Headers

```
API-Version: 1.0
API-Deprecated: true
API-Sunset: 2024-06-01
```

## Performance Optimization

### Caching Strategy

1. **Cache Headers**
   ```
   Cache-Control: public, max-age=3600
   ETag: "33a64df551"
   Last-Modified: Mon, 01 Jan 2024 00:00:00 GMT
   ```

2. **Conditional Requests**
   ```
   If-None-Match: "33a64df551"
   If-Modified-Since: Mon, 01 Jan 2024 00:00:00 GMT
   ```

### Response Optimization

1. **Field Selection**
   ```
   GET /api/v1/users?fields=id,name,email
   ```

2. **Nested Resource Control**
   ```
   GET /api/v1/users?include=organization,posts
   ```

3. **Compression**
   - Enable gzip/brotli
   - Compress responses > 1KB
   - Skip binary data

### Request Optimization

1. **Batch Operations**
   ```
   POST /api/v1/batch
   {
     "operations": [
       {"method": "GET", "url": "/users/1"},
       {"method": "GET", "url": "/users/2"}
     ]
   }
   ```

2. **Debouncing**
   - Search inputs: 300ms
   - Form validation: 500ms
   - Auto-save: 1000ms

## Testing Strategies

### API Testing Checklist

1. **Functional Testing**
   - [ ] All CRUD operations work
   - [ ] Validation rules enforced
   - [ ] Business logic correct
   - [ ] Error cases handled

2. **Integration Testing**
   - [ ] Database transactions work
   - [ ] External services integrated
   - [ ] Authentication flows
   - [ ] File uploads successful

3. **Performance Testing**
   - [ ] Response times acceptable
   - [ ] Pagination efficient
   - [ ] Caching working
   - [ ] No memory leaks

4. **Security Testing**
   - [ ] Authentication required
   - [ ] Authorization enforced
   - [ ] Input sanitization
   - [ ] Rate limiting active

### Testing Tools

1. **Backend Testing**
   - Pytest for unit tests
   - HTTPX for API tests
   - Locust for load testing

2. **Frontend Testing**
   - Jest for unit tests
   - MSW for API mocking
   - Cypress for E2E tests

3. **API Documentation**
   - OpenAPI/Swagger spec
   - Postman collections
   - Example requests/responses

## Best Practices Summary

1. **Consistency is Key**
   - Same patterns everywhere
   - Predictable behavior
   - Clear documentation

2. **Security First**
   - Validate all inputs
   - Authenticate all requests
   - Encrypt sensitive data

3. **Performance Matters**
   - Optimize payload size
   - Implement caching
   - Use pagination

4. **Developer Experience**
   - Clear error messages
   - Comprehensive docs
   - Easy testing

5. **Monitor Everything**
   - Log all requests
   - Track performance
   - Alert on errors