from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.routes import auth, websocket

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(websocket.router)

@app.get("/")
async def get():
    import os
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(file_path) as f:
        return HTMLResponse(content=f.read())

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)