from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import os
from dotenv import load_dotenv
from .api import router as api_router
from .database.config import get_db
from .services.auth import get_current_user

load_dotenv()

app = FastAPI(
    title="Alt Data Dashboard API",
    description="API for unified analytics and visualization of public and alternative data",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit(request, call_next):
    # TODO: Implement rate limiting logic (2 requests per second)
    response = await call_next(request)
    return response

async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user = get_current_user(db, token)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

# Include API routes
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Alt Data Dashboard API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
