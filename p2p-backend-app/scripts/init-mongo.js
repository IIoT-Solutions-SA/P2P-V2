// MongoDB initialization script
// This runs when MongoDB container starts for the first time

// Switch to our database
db = db.getSiblingDB('p2p_sandbox');

// Create collections with validation schemas
db.createCollection('forum_posts', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['topic_id', 'content', 'author_id', 'created_at'],
      properties: {
        topic_id: {
          bsonType: 'string',
          description: 'UUID of the forum topic'
        },
        content: {
          bsonType: 'string',
          description: 'Post content in HTML/Markdown'
        },
        author_id: {
          bsonType: 'string',
          description: 'UUID of the author'
        },
        attachments: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              type: { enum: ['image', 'document', 'video'] },
              url: { bsonType: 'string' },
              filename: { bsonType: 'string' },
              size: { bsonType: 'number' }
            }
          }
        },
        replies: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              id: { bsonType: 'string' },
              content: { bsonType: 'string' },
              author_id: { bsonType: 'string' },
              created_at: { bsonType: 'date' },
              is_best_answer: { bsonType: 'bool' },
              upvotes: { bsonType: 'array' }
            }
          }
        },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' }
      }
    }
  }
});

// Create indexes for better performance
db.forum_posts.createIndex({ topic_id: 1, created_at: -1 });
db.forum_posts.createIndex({ author_id: 1 });
db.forum_posts.createIndex({ 'content': 'text' }); // For text search

// Create use_cases collection
db.createCollection('use_cases', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['title', 'organization_id', 'submitted_by', 'created_at'],
      properties: {
        submission_id: { bsonType: 'string' },
        title: { bsonType: 'string' },
        organization_id: { bsonType: 'string' },
        submitted_by: { bsonType: 'string' },
        industry: { bsonType: 'string' },
        technology: { bsonType: 'array' },
        problem_statement: { bsonType: 'string' },
        solution: { bsonType: 'string' },
        outcomes: { bsonType: 'object' },
        vendor_info: { bsonType: 'object' },
        media: { bsonType: 'array' },
        location: { bsonType: 'object' },
        tags: { bsonType: 'array' },
        views: { bsonType: 'number' },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' }
      }
    }
  }
});

// Create indexes for use_cases
db.use_cases.createIndex({ organization_id: 1 });
db.use_cases.createIndex({ industry: 1 });
db.use_cases.createIndex({ technology: 1 });
db.use_cases.createIndex({ tags: 1 });
db.use_cases.createIndex({ 'title': 'text', 'problem_statement': 'text', 'solution': 'text' });

print('MongoDB initialization completed successfully!');