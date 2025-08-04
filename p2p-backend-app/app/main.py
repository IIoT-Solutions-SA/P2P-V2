"""
P2P Sandbox Backend API
A minimal FastAPI application to test our container setup
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI instance
app = FastAPI(
    title="P2P Sandbox API",
    description="Backend API for P2P Sandbox platform",
    version="0.1.0",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to P2P Sandbox API",
        "version": "0.1.0",
        "status": "Container setup complete! 🎉"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "p2p-backend",
        "checks": {
            "api": "operational",
            # We'll add database checks later
        }
    }


# This allows us to run the app directly with python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)