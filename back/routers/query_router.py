import time  # 시간 측정용
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
@router.post("/query/execute")
async def get_table_data(request: QueryRequest):
    try:
        data = db_service.select_data(request.table_name, limit=request.limit)
        return {
            "success": True,
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/query/explain")
async def explain_query(request: QueryRequest):
    try:
        start_time = time.time()
        
        # EXPLAIN + EXPLAIN ANALYZE 실행
        explain_result = db_service.explain_data(
            request.table_name,
            conditions=request.conditions,
            limit=request.limit
        )
        
        # 실제 데이터
        data = db_service.select_data(
            request.table_name,
            conditions=request.conditions,
            limit=request.limit
        )
        
        end_time = time.time()
        query_time = (end_time - start_time) * 1000
        
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "query_time": round(query_time, 2),
            "explain_data": {
                "type": explain_result['type'],
                "rows": explain_result['rows'],
                "key": explain_result['key'],
                "key_len": explain_result['key_len'],
                "extra": explain_result['Extra'],
                "analyze_text": explain_result['analyze_text']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))