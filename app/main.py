from fastapi import FastAPI
from app.routers import nodes
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许 React 前端的来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有的 HTTP 方法
    allow_headers=["*"],  # 允许所有的 Headers
)

# 初始化数据库并创建表
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(nodes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Social Network Simulation API"}