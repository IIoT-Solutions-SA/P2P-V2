# S3 Bucket Configuration for P2P Platform

## Production Buckets (Currently Active)
- **Profile Images**: `p2p-prod-profile-images`
- **Forum Media**: `p2p-prod-forum-media`
- **Use Case Media**: `p2p-prod-usecase-media`

## Development Buckets (Commented Out)
- **Profile Images**: `p2p-dev-profile-images`
- **Forum Media**: `p2p-dev-forum-media`
- **Use Case Media**: `p2p-dev-usecase-media`

## Files Updated

### 1. `/app/core/config.py`
- Production buckets are now active
- Development buckets are kept but commented out
- Easy to switch between environments by commenting/uncommenting

### 2. `/app/services/usecase_service.py`
- Line 445: Changed from hardcoded `"p2p-dev-usecase-media"` to `settings.S3_USECASE_MEDIA_BUCKET`

### 3. `/app/services/forum_service.py`
- Line 183: Changed from hardcoded `"p2p-dev-forum-media"` to `settings.S3_FORUM_MEDIA_BUCKET`

## AWS S3 Buckets to Create
You need to create these 3 production buckets in AWS S3:

```
p2p-prod-profile-images
p2p-prod-forum-media
p2p-prod-usecase-media
```

### Bucket Configuration Requirements
1. **Region**: `me-south-1` (Bahrain)
2. **Public Access**: Enable public read for media buckets
3. **CORS Configuration**: Same as dev buckets
4. **Bucket Policy**: Allow public read for objects

## Switching Between Environments

### For Production:
```python
# S3 Bucket Names - PRODUCTION
S3_PROFILE_PICTURES_BUCKET: str = "p2p-prod-profile-images"
S3_FORUM_MEDIA_BUCKET: str = "p2p-prod-forum-media"
S3_USECASE_MEDIA_BUCKET: str = "p2p-prod-usecase-media"
```

### For Development:
```python
# S3 Bucket Names - DEVELOPMENT
S3_PROFILE_PICTURES_BUCKET: str = "p2p-dev-profile-images"
S3_FORUM_MEDIA_BUCKET: str = "p2p-dev-forum-media"
S3_USECASE_MEDIA_BUCKET: str = "p2p-dev-usecase-media"
```

Just comment out production lines and uncomment development lines (or vice versa).

## Important Notes
- **No hardcoded bucket names**: All S3 operations now use `settings.S3_*_BUCKET` variables
- **Easy environment switching**: Just comment/uncomment in config.py
- **Both environments preserved**: Dev buckets are not deleted, just commented out