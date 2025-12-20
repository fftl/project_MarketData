import pymysql
import pandas as pd
from typing import List, Optional, Dict
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseService:
    def __init__(self):
        # pymysql 연결 (EXPLAIN 등 raw query용)
        self.connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # SQLAlchemy 엔진 (to_sql용)
        db_url = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
        self.engine = create_engine(db_url)
    
    def get_csv_columns(self, csv_path: str):
        """CSV 파일의 전체 컬럼 목록 반환"""
        df = pd.read_csv(csv_path, nrows=0)  # 헤더만 읽기
        return df.columns.tolist()
    
    def create_full_table(self, csv_path: str, table_name: str):
        """CSV 전체 컬럼으로 테이블 생성 (to_sql 사용)"""
        # CSV 전체 읽기
        df = pd.read_csv(csv_path)
        df = df.sample(frac=0.1)
        
        # 기존 테이블이 있으면 삭제하고 새로 생성
        df.to_sql(
            name=table_name,
            con=self.engine,
            if_exists='replace',  # 기존 테이블 삭제 후 재생성
            index=False,          # 인덱스 컬럼 제외
            method='multi',       # 빠른 삽입
            chunksize=1000        # 1000개씩 나눠서 삽입
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