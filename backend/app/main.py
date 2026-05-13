from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from fastapi.staticfiles import StaticFiles

from app.routes.chat import router as chat_router
from app.routes.status import router as status_router

app = FastAPI(
    title="NEXUS AI IoT"
)

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# STATIC FILES
# =========================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# =========================
# ROOT ROUTE
# =========================

@app.get("/")
async def root():
    return FileResponse("templates/index.html")

# =========================
# ROUTES
# =========================

app.include_router(chat_router)
app.include_router(status_router)