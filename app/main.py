# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router
from app.config import STATIC_DIR

app = FastAPI(title="Bimatrix Solver")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router)