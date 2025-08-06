# P2P Backend Scripts

This directory contains automation scripts for managing the P2P Sandbox backend.

## Quick Commands

### Start Backend
```bash
./scripts/start-backend.sh
```
Comprehensive backend startup with all checks and validations.

### Stop Backend
```bash
./scripts/stop-backend.sh
```
Graceful backend shutdown with cleanup.

### Troubleshoot Issues
```bash
./scripts/troubleshoot-backend.sh
```
Diagnose common backend problems and get solutions.

## Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `start-backend.sh` | Complete backend startup | `./scripts/start-backend.sh` |
| `stop-backend.sh` | Graceful backend shutdown | `./scripts/stop-backend.sh` |
| `troubleshoot-backend.sh` | Diagnose and fix issues | `./scripts/troubleshoot-backend.sh` |

## Features

### Start Script (`start-backend.sh`)
- ✅ Checks for existing processes
- ✅ Validates virtual environment
- ✅ Verifies dependencies  
- ✅ Starts database services
- ✅ Validates models
- ✅ Starts backend with monitoring
- ✅ Tests core API endpoints
- ✅ Provides helpful URLs

### Stop Script (`stop-backend.sh`)
- ✅ Graceful process termination
- ✅ Force kills stubborn processes
- ✅ Port cleanup verification
- ✅ Optional database shutdown
- ✅ Temporary file cleanup

### Troubleshoot Script (`troubleshoot-backend.sh`)
- ✅ System information
- ✅ Process status check
- ✅ Port availability check
- ✅ Backend health verification
- ✅ Dependency validation
- ✅ Database service status
- ✅ Model import testing
- ✅ Common issue solutions

## Quick Reference

### Emergency Commands
```bash
# Complete reset (nuclear option)
pkill -f uvicorn
docker-compose down
docker-compose up -d
sleep 30
./scripts/start-backend.sh

# Force kill all backend processes
pkill -9 -f uvicorn

# Check what's using port 8000
lsof -i :8000
```

### Verification Commands
```bash
# Check backend health
curl http://localhost:8000/health

# Test core APIs
curl http://localhost:8000/api/v1/users/me
curl http://localhost:8000/api/v1/organizations/me

# Monitor logs (if running in background)
tail -f backend.log
```

## Common Workflows

### Daily Development
1. `./scripts/start-backend.sh` - Start for the day
2. Develop and test
3. `./scripts/stop-backend.sh` - Clean shutdown

### Troubleshooting
1. `./scripts/troubleshoot-backend.sh` - Diagnose issues
2. Follow suggested solutions
3. `./scripts/start-backend.sh` - Restart

### Complete Reset
1. `./scripts/stop-backend.sh` - Stop everything
2. `docker-compose down` - Reset databases  
3. `docker-compose up -d` - Start databases
4. `./scripts/start-backend.sh` - Fresh start

## Integration

These scripts integrate with:
- **Documentation**: See `docs/aadil_docs/backend-startup-shutdown-guide.md`
- **Docker**: Manages PostgreSQL and MongoDB services
- **Virtual Environment**: Activates and validates Python venv
- **API Testing**: Verifies all Phase 3 endpoints

## Troubleshooting

If scripts fail, check:

1. **Permissions**: `chmod +x scripts/*.sh`
2. **Location**: Run from `p2p-backend-app/` directory
3. **Dependencies**: Virtual environment and Docker available
4. **Ports**: 8000, 5432, 27017 not occupied by other processes

## Support

For detailed troubleshooting and advanced procedures, see:
- 📚 `docs/aadil_docs/backend-startup-shutdown-guide.md`
- 🔧 Run `./scripts/troubleshoot-backend.sh` for diagnosis
- 🚀 GitHub Issues for persistent problems

---

**Note**: These scripts are designed to prevent the startup issues that were resolved in P3.5.FIX.01. Always use them for consistent backend management.