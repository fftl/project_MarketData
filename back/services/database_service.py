import pymysql
import pandas as pd
from typing import List, Optional, Dict
from sqlalchemy import create_engine, text
from urllib.parse import urlparse
import hashlib  
import os
import re
from dotenv import load_dotenv

load_dotenv()

class DatabaseService:
    def __init__(self):
        # DATABASE_URL 파싱
        db_url = os.getenv('DATABASE_URL')
        read_db_url = os.getenv('READ_DATABASE_URL')
        
        # 관리자용 엔진 (테이블 생성, 인덱스 관리 등)
        self.engine = create_engine(
            db_url,
            pool_size=5,           # 최대 5개 연결
            max_overflow=10,       # 추가 10개
            pool_recycle=3600,     # 1시간마다 재생성
            pool_pre_ping=True,    # 사용 전 연결 확인
        )
        
        # 읽기 전용 엔진 (커스텀 쿼리용)
        self.readonly_engine = create_engine(
            read_db_url,
            pool_size=3,           # 읽기 전용은 작게
            max_overflow=5,
            pool_recycle=3600,
            pool_pre_ping=True,
        )

    def _clean_query(self, query: str) -> str:
        """쿼리 정리 (주석 제거, 공백 정리)"""
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        query = ' '.join(query.split())
        return query.strip()

    def _is_safe_select(self, query: str) -> bool:
        """SELECT 문인지 확인"""
        query_upper = query.upper().strip()
        return query_upper.startswith('SELECT') or query_upper.startswith('WITH')
    
    def get_csv_columns(self, csv_path: str):
        """CSV 파일의 전체 컬럼 목록 반환"""
        df = pd.read_csv(csv_path, nrows=0)
        return df.columns.tolist()
    
    def create_full_table(self, csv_path: str, table_name: str = 'full_table'):
        """테이블이 이미 있으면 재사용, 없으면 생성"""
        
        # 1. 테이블 존재 확인
        if self._table_exists(table_name):
            columns = self._get_table_columns(table_name)
            row_count = self._get_row_count(table_name)
            
            return {
                "table_name": table_name,
                "rows_inserted": row_count,
                "columns": columns,
                "existed": True
            }
        
        # 2. 새로 생성
        df = pd.read_csv(csv_path)
        df = df.sample(frac=0.5)
        
        df.to_sql(
            name=table_name,
            con=self.engine,
            if_exists='fail',
            index=False,
            method='multi',
            chunksize=1000
        )
        
        return {
            "table_name": table_name,
            "rows_inserted": len(df),
            "columns": df.columns.tolist(),
            "existed": False
        }
    
    def _generate_table_name(self, columns: List[str], prefix: str = "custom") -> str:
        """컬럼 개수와 해시로 테이블명 생성"""
        sorted_columns = sorted(columns)
        columns_str = ",".join(sorted_columns)
        
        hash_obj = hashlib.md5(columns_str.encode())
        hash_str = hash_obj.hexdigest()[:8]
        
        return f"{prefix}_{len(columns)}cols_{hash_str}"

    def create_table_with_columns(self, csv_path: str, columns: List[str], table_name: str = None):
        """선택한 컬럼으로 테이블 생성 (자동 테이블명 생성 및 재사용)"""
        
        # 1. 테이블명이 없으면 자동 생성
        if not table_name:
            table_name = self._generate_table_name(columns, prefix="custom")
        
        # 2. 테이블 존재 확인
        if self._table_exists(table_name):
            existing_columns = self._get_table_columns(table_name)
            
            if set(existing_columns) == set(columns):
                row_count = self._get_row_count(table_name)
                return {
                    "table_name": table_name,
                    "rows_inserted": row_count,
                    "columns": columns,
                    "existed": True
                }
        
        # 3. 새로 생성
        df = pd.read_csv(csv_path)
        df = df.sample(frac=0.5)
        
        available_columns = df.columns.tolist()
        invalid_columns = [col for col in columns if col not in available_columns]
        
        if invalid_columns:
            raise ValueError(f"존재하지 않는 컬럼: {', '.join(invalid_columns)}")
        
        df_selected = df[columns]
        
        df_selected.to_sql(
            name=table_name,
            con=self.engine,
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000
        )
        
        return {
            "table_name": table_name,
            "rows_inserted": len(df_selected),
            "columns": columns,
            "existed": False
        }

    def _table_exists(self, table_name: str) -> bool:
        """테이블 존재 여부 확인"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) as cnt
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                AND table_name = :table_name
            """), {"table_name": table_name})
            row = result.fetchone()
            return row[0] > 0

    def _get_table_columns(self, table_name: str) -> list:
        """테이블 컬럼 목록 조회"""
        with self.engine.connect() as conn:
            result = conn.execute(text(f"SHOW COLUMNS FROM `{table_name}`"))
            return [row[0] for row in result]

    def _get_row_count(self, table_name: str) -> int:
        """테이블 행 개수 조회"""
        with self.engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) as cnt FROM `{table_name}`"))
            row = result.fetchone()
            return row[0]
    
    def select_data(self, table_name: str, conditions: Optional[Dict] = None, limit: int = 100):
        """데이터 조회"""
        with self.engine.connect() as conn:
            sql = f"SELECT * FROM `{table_name}`"
            params = {}
            
            if conditions:
                where_clauses = [f"`{k}` = :{k}" for k in conditions.keys()]
                sql += " WHERE " + " AND ".join(where_clauses)
                params.update(conditions)
            
            sql += " LIMIT :limit"
            params['limit'] = limit
            
            result = conn.execute(text(sql), params)
            # 딕셔너리 형태로 변환
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result]
    
    def explain_data(self, table_name: str, conditions: Optional[Dict] = None, limit: int = 100):
        """EXPLAIN과 EXPLAIN ANALYZE 모두 실행"""
        with self.engine.connect() as conn:
            sql = f"SELECT * FROM `{table_name}`"
            params = {}
            
            if conditions:
                where_clauses = [f"`{k}` = :{k}" for k in conditions.keys()]
                sql += " WHERE " + " AND ".join(where_clauses)
                params.update(conditions)
            
            sql += " LIMIT :limit"
            params['limit'] = limit
            
            # 1. EXPLAIN 실행
            explain_sql = "EXPLAIN " + sql
            explain_result = conn.execute(text(explain_sql), params)
            explain_row = explain_result.fetchone()
            
            # 2. EXPLAIN ANALYZE 실행
            analyze_sql = "EXPLAIN ANALYZE " + sql
            analyze_result = conn.execute(text(analyze_sql), params)
            analyze_row = analyze_result.fetchone()
            
            # 결과 정리
            if explain_row:
                columns = explain_result.keys()
                explain_info = dict(zip(columns, explain_row))
            else:
                explain_info = {}
            
            analyze_text = analyze_row[0] if analyze_row else ''
            
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
        with self.engine.connect() as conn:
            sql = text(f"CREATE INDEX `{index_name}` ON `{table_name}`(`{column_name}`(50))")
            conn.execute(sql)
            conn.commit()
        return {"index_created": index_name, "column": column_name}
    
    def create_composite_index(self, table_name: str, columns: List[str], index_name: str):
        """복합 인덱스 생성"""
        with self.engine.connect() as conn:
            columns_str = ', '.join([f"`{col}`(50)" for col in columns])
            sql = text(f"CREATE INDEX `{index_name}` ON `{table_name}`({columns_str})")
            conn.execute(sql)
            conn.commit()
        return {"index_created": index_name, "columns": columns}
    
    def drop_index(self, table_name: str, index_name: str):
        """인덱스 삭제"""
        with self.engine.connect() as conn:
            sql = text(f"DROP INDEX `{index_name}` ON `{table_name}`")
            conn.execute(sql)
            conn.commit()
        return {"index_dropped": index_name}
    
    def execute_raw_query(self, query: str):
        """커스텀 쿼리 실행 (읽기 전용 엔진 사용)"""
        cleaned_query = self._clean_query(query)
        if not self._is_safe_select(cleaned_query):
            raise ValueError("SELECT 쿼리만 실행 가능합니다.")
        
        # ✅ 읽기 전용 엔진 사용
        with self.readonly_engine.connect() as conn:
            result = conn.execute(text(query))
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result]

    def execute_explain_raw(self, query: str):
        """커스텀 쿼리 EXPLAIN 실행 (읽기 전용 엔진 사용)"""
        cleaned_query = self._clean_query(query)
        if not self._is_safe_select(cleaned_query):
            raise ValueError("SELECT 쿼리만 실행 가능합니다.")
        
        # ✅ 읽기 전용 엔진 사용
        with self.readonly_engine.connect() as conn:
            explain_query = f"EXPLAIN {query}"
            result = conn.execute(text(explain_query))
            row = result.fetchone()
            
            if row:
                columns = result.keys()
                explain_info = dict(zip(columns, row))
            else:
                explain_info = {}
            
            return {
                'type': explain_info.get('type', 'N/A'),
                'rows': explain_info.get('rows', 0),
                'key': explain_info.get('key', None),
                'key_len': explain_info.get('key_len', None),
                'Extra': explain_info.get('Extra', '')
            }