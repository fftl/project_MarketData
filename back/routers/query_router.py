from fastapi import APIRouter, HTTPException
from models.schemas import (
    TableCreateRequest, 
    FullTableCreateRequest,
    IndexRequest, 
    QueryRequest
)
from services.database_service import DatabaseService
from services.query_service import QueryService

router = APIRouter()

db_service = DatabaseService()
query_service = QueryService()

# CSV 컬럼 목록 가져오기
@router.get("/csv/columns")
async def get_csv_columns():
    try:
        columns = db_service.get_csv_columns("data/소상공인시장진흥공단_상가(상권)정보_서울_202510.csv")
        return {
            "success": True,
            "columns": columns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 전체 컬럼으로 테이블 생성
@router.post("/table/create-full")
async def create_full_table(request: FullTableCreateRequest):
    try:
        result = db_service.create_full_table(
            csv_path=request.csv_path,
            table_name=request.table_name
        )
        return {
            "success": True,
            "message": "Full table created",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 전체 데이터 조회
@router.get("/table/{table_name}/data")
async def get_table_data(table_name: str, limit: int = 100):
    try:
        data = db_service.select_data(table_name, limit=limit)
        return {
            "success": True,
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))