from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import query_router

app = FastAPI()  # ← FastAPI 앱 생성 (식당 오픈)

# CORS 설정 (Vue와 통신 가능하게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://3.39.42.231:8080/"],  # Vue 허용
    allow_methods=["*"],
)

# 라우터 등록 (메뉴판 가져다 붙이기)
app.include_router(query_router.router, prefix="/api")

# 이 파일을 실행하면 서버가 돌아감
# uvicorn main:app --reload