import pymysql
import pandas as pd
from typing import List, Optional, Dict
from sqlalchemy import create_engine
from urllib.parse import urlparse
import os
import re
from dotenv import load_dotenv

load_dotenv()

class DatabaseService:
    def __init__(self):
        # DATABASE_URL 파싱
        db_url = os.getenv('DATABASE_URL')
        parsed = urlparse(db_url)
        read_db_url = os.getenv('READ_DATABASE_URL')
        read_parsed = urlparse(read_db_url)
        
        # pymysql 연결 (EXPLAIN 등 raw query용)
        self.connection = pymysql.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:],  # 앞의 '/' 제거
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        self.readonly_connection = pymysql.connect(
            host=read_parsed.hostname,
            port=read_parsed.port or 3306,
            user=read_parsed.username,
            password=read_parsed.password,
            database=read_parsed.path[1:],  # 앞의 '/' 제거
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        self.engine = create_engine(db_url)

    def _clean_query(self, query: str) -> str:
        """쿼리 정리 (주석 제거, 공백 정리)"""
        # SQL 주석 제거
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)  # -- 주석
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)  # /* */ 주석
        # 공백 정리
        query = ' '.join(query.split())
        return query.strip()

    def _is_safe_select(self, query: str) -> bool:
        """SELECT 문인지 확인"""
        query_upper = query.upper().strip()
        # WITH 절을 사용한 CTE도 허용
        return query_upper.startswith('SELECT') or query_upper.startswith('WITH')
    
    def get_csv_columns(self, csv_path: str):
        """CSV 파일의 전체 컬럼 목록 반환"""
        df = pd.read_csv(csv_path, nrows=0)  # 헤더만 읽기
        return df.columns.tolist()
    
    def create_full_table(self, csv_path: str, table_name: str):
        """CSV 전체 컬럼으로 테이블 생성 (to_sql 사용)"""
        # CSV 전체 읽기
        df = pd.read_csv(csv_path)
        df = df.sample(frac=0.01)  # 1% 샘플링
        
        # 기존 테이블이 있으면 삭제하고 새로 생성
        df.to_sql(
            name=table_name,
            con=self.engine,
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000
        )
        
        return {
            "table_name": table_name,
            "rows_inserted": len(df),
            "columns": df.columns.tolist()
        }
    
    def select_data(self, table_name: str, conditions: Optional[Dict] = None, limit: int = 100):
        """데이터 조회"""
        with self.connection.cursor() as cursor:
            sql = f"SELECT * FROM {table_name}"
            
            if conditions:
                where_clauses = [f"{k} = %s" for k in conditions.keys()]
                sql += " WHERE " + " AND ".join(where_clauses)
            
            sql += f" LIMIT {limit}"
            
            if conditions:
                cursor.execute(sql, tuple(conditions.values()))
            else:
                cursor.execute(sql)
            
            return cursor.fetchall()
    
    def explain_data(self, table_name: str, conditions: Optional[Dict] = None, limit: int = 100):
        """EXPLAIN과 EXPLAIN ANALYZE 모두 실행"""
        with self.connection.cursor() as cursor:
            sql = f"SELECT * FROM {table_name}"
            
            if conditions:
                where_clauses = [f"{k} = %s" for k in conditions.keys()]
                sql += " WHERE " + " AND ".join(where_clauses)
            
            sql += f" LIMIT {limit}"
            
            params = tuple(conditions.values()) if conditions else None
            
            # 1. EXPLAIN 실행 (테이블 형식)
            explain_sql = "EXPLAIN " + sql
            cursor.execute(explain_sql, params) if params else cursor.execute(explain_sql)
            explain_result = cursor.fetchall()
            
            # 2. EXPLAIN ANALYZE 실행 (실제 실행)
            analyze_sql = "EXPLAIN ANALYZE " + sql
            cursor.execute(analyze_sql, params) if params else cursor.execute(analyze_sql)
            analyze_result = cursor.fetchall()
            
            # 결과 정리
            explain_info = explain_result[0] if explain_result else {}
            analyze_text = analyze_result[0].get('EXPLAIN', '') if analyze_result else ''
            
            return {
                'type': explain_info.get('type', 'N/A'),
                'rows': explain_info.get('rows', 0),
                'key': explain_info.get('key', None),
                'key_len': explain_info.get('key_len', None),
                'Extra': explain_info.get('Extra', ''),
                'analyze_text': analyze_text,
                'full_explain': explain_info
            }
    
    def create_index(self, table_name: str, column_name: str, index_name: str):
        """단일 인덱스 생성"""
        with self.connection.cursor() as cursor:
            sql = f"CREATE INDEX {index_name} ON {table_name}(`{column_name}`(50))"
            cursor.execute(sql)
        self.connection.commit()
        return {"index_created": index_name, "column": column_name}
    
    def create_composite_index(self, table_name: str, columns: List[str], index_name: str):
        """복합 인덱스 생성"""
        with self.connection.cursor() as cursor:
            # 여러 컬럼을 순서대로 결합
            columns_str = ', '.join([f"`{col}`" for col in columns])
            sql = f"CREATE INDEX {index_name} ON {table_name}({columns_str}(50))"
            cursor.execute(sql)
        self.connection.commit()
        return {"index_created": index_name, "columns": columns}
    
    def drop_index(self, table_name: str, index_name: str):
        """인덱스 삭제"""
        with self.connection.cursor() as cursor:
            sql = f"DROP INDEX {index_name} ON {table_name}"
            cursor.execute(sql)
        self.connection.commit()
        return {"index_dropped": index_name}
    
    def execute_raw_query(self, query: str):
        cleaned_query = self._clean_query(query)
        if not self._is_safe_select(cleaned_query):
            raise ValueError("SELECT 쿼리만 실행 가능합니다.")
        
        with self.readonly_connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def execute_explain_raw(self, query: str):
        cleaned_query = self._clean_query(query)
        if not self._is_safe_select(cleaned_query):
            raise ValueError("SELECT 쿼리만 실행 가능합니다.")
        
        with self.readonly_connection.cursor() as cursor:
            explain_query = f"EXPLAIN {query}"
            cursor.execute(explain_query)
            explain_result = cursor.fetchall()
            
            explain_info = explain_result[0] if explain_result else {}
            
            return {
                'type': explain_info.get('type', 'N/A'),
                'rows': explain_info.get('rows', 0),
                'key': explain_info.get('key', None),
                'key_len': explain_info.get('key_len', None),
                'Extra': explain_info.get('Extra', '')
            }