import time
from .database_service import DatabaseService

class QueryService:
    def __init__(self):
        self.db = DatabaseService()
    
    def execute_query_with_time(self, table_name: str, conditions=None):
        """쿼리 실행 + 시간 측정"""
        start_time = time.time()
        data = self.db.select_data(table_name, conditions)
        end_time = time.time()
        
        query_time = (end_time - start_time) * 1000  # ms로 변환
        
        return {
            "success": True,
            "data": data,
            "query_time": round(query_time, 2),
            "row_count": len(data)
        }
    
    def execute_explain_with_time(self, table_name: str, conditions=None):
        """EXPLAIN ANALYZE + 시간 측정"""
        explain_result = self.db.explain_analyze(table_name, conditions)
        
        start_time = time.time()
        data = self.db.select_data(table_name, conditions)
        end_time = time.time()
        
        return {
            "success": True,
            "explain_data": explain_result,
            "query_time": round((end_time - start_time) * 1000, 2),
            "row_count": len(data),
            "data": data[:100]  # 처음 100개만
        }