from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import get_pois, route_optim, ors_proxy, download_plan, cache_routes, user_auth, db_routes
from contextlib import asynccontextmanager
from db.client import plans_collection

@asynccontextmanager
async def lifespan(app: FastAPI):
    await plans_collection.create_index("user_id")
    print("user_id index created")
    yield

# ✅ lifespan 포함
app = FastAPI(lifespan=lifespan)

# ✅ CORS 적용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API 라우터 등록
backend_route_prefix = '/api'
app.include_router(get_pois.router, prefix=backend_route_prefix)
app.include_router(route_optim.router, prefix=backend_route_prefix)
app.include_router(ors_proxy.router, prefix=backend_route_prefix)
app.include_router(download_plan.router, prefix=backend_route_prefix)
app.include_router(cache_routes.router, prefix=backend_route_prefix)
app.include_router(user_auth.router, prefix=backend_route_prefix)
app.include_router(db_routes.router, prefix=backend_route_prefix)
