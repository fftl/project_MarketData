from pydantic import BaseModel
from typing import List, Optional, Dict

class TableCreateRequest(BaseModel):
    columns: List[str]

class FullTableCreateRequest(BaseModel):
    csv_path: str = "data/소상공인시장진흥공단_상가(상권)정보_서울_202510.csv"
    table_name: str = "full_table"

class IndexRequest(BaseModel):
    table_name: str
    column_name: str
    index_name: Optional[str] = None

class QueryRequest(BaseModel):
    table_name: str
    conditions: Optional[Dict] = None