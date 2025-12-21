import time
from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import (
    FullTableCreateRequest,
    IndexRequest, 
    QueryRequest,
    CompositeIndexRequest,
    CustomQueryRequest
)
from services.database_service import DatabaseService

router = APIRouter()
db_service = DatabaseService()

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

# 일반 쿼리 실행
@router.post("/query/execute")
async def execute_query(request: QueryRequest):
    try:
        start_time = time.time()
        
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
            "query_time": round(query_time, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# EXPLAIN ANALYZE 실행
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

# 단일 인덱스 생성
@router.post("/index/create")
async def create_single_index(request: IndexRequest):
    # 받은 데이터 확인
    print("="*50)
    print("받은 요청 데이터:")
    print(f"  table_name: {request.table_name}")
    print(f"  column_name: {request.column_name}")
    print(f"  index_name: {request.index_name}")
    print("="*50)
    
    try:
        index_name = request.index_name or f"idx_{request.column_name}"
        
        result = db_service.create_index(
            request.table_name,
            request.column_name,
            index_name
        )
        
        return {
            "success": True,
            "index_name": index_name,
            "column": request.column_name,
            "details": result
        }
    except Exception as e:
        import traceback
        print("\n에러 발생!")
        print(f"에러 타입: {type(e).__name__}")
        print(f"에러 메시지: {str(e)}")
        print("\n전체 스택 트레이스:")
        traceback.print_exc()
        print("="*50 + "\n")
        
        raise HTTPException(status_code=500, detail=str(e))

# 복합 인덱스 생성
@router.post("/index/create-composite")
async def create_composite_index(request: CompositeIndexRequest):
    try:
        index_name = request.index_name or f"idx_{'_'.join(request.columns)}"
        
        result = db_service.create_composite_index(
            request.table_name,
            request.columns,
            index_name
        )
        
        return {
            "success": True,
            "index_name": index_name,
            "columns": request.columns,
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 인덱스 삭제
@router.delete("/index/drop")
async def drop_index(table_name: str, index_name: str):
    try:
        result = db_service.drop_index(table_name, index_name)
        return {
            "success": True,
            "message": f"Index {index_name} dropped",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 커스텀 쿼리 실행
@router.post("/query/execute-custom")
async def execute_custom_query(request: CustomQueryRequest):
    try:
        start_time = time.time()
        
        result = db_service.execute_raw_query(request.query)
        
        end_time = time.time()
        query_time = (end_time - start_time) * 1000
        
        return {
            "success": True,
            "data": result,
            "count": len(result),
            "query_time": round(query_time, 2)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# 커스텀 EXPLAIN 실행
@router.post("/query/explain-custom")
async def explain_custom_query(request: CustomQueryRequest):
    try:
        start_time = time.time()
        
        # EXPLAIN 실행
        explain_result = db_service.execute_explain_raw(request.query)
        
        # 실제 데이터 실행
        data = db_service.execute_raw_query(request.query)
        
        end_time = time.time()
        query_time = (end_time - start_time) * 1000
        
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "query_time": round(query_time, 2),
            "explain_data": explain_result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))