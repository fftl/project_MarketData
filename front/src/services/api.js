// services/api.js
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

export default {
  // CSV 컬럼 목록 가져오기
  getCsvColumns() {
    return axios.get(`${API_BASE_URL}/csv/columns`)
  },

  // 전체 테이블 생성
  createFullTable(csvPath = 'data/소상공인시장진흥공단_상가(상권)정보_서울_202510.csv', tableName = 'full_table') {
    return axios.post(`${API_BASE_URL}/table/create-full`, {
      csv_path: csvPath,
      table_name: tableName
    })
  },

  // 테이블 데이터 조회
  getTableData(tableName, limit = 100) {
    return axios.get(`${API_BASE_URL}/table/${tableName}/data`, {
      params: { limit }
    })
  },

  // 테이블 생성
  createTable(columns) {
    return axios.post(`${API_BASE_URL}/table/create`, { columns })
  },

  // 단일 인덱스 생성
  createIndex(tableName, columnName, indexName = null) {
    return axios.post(`${API_BASE_URL}/index/create`, {
      table_name: tableName,
      column_name: columnName,
      index_name: indexName
    })
  },

  // 복합 인덱스 생성 (추가)
  createCompositeIndex(tableName, columns, indexName = null) {
    return axios.post(`${API_BASE_URL}/index/create-composite`, {
      table_name: tableName,
      columns: columns,  // 배열 형태
      index_name: indexName
    })
  },

  // 인덱스 삭제
  dropIndex(tableName, indexName) {
    return axios.delete(`${API_BASE_URL}/index/drop`, {
      params: { table_name: tableName, index_name: indexName }
    })
  },

  // 쿼리 실행
  executeQuery(tableName, conditions = null) {
    return axios.post(`${API_BASE_URL}/query/execute`, {
      table_name: tableName,
      conditions
    })
  },

  // EXPLAIN 실행
  explainQuery(tableName, conditions = null) {
    return axios.post(`${API_BASE_URL}/query/explain`, {
      table_name: tableName,
      conditions
    })
  },

    // 커스텀 쿼리 실행
  executeCustomQuery(query) {
    return axios.post(`${API_BASE_URL}/query/execute-custom`, {
      query: query
    })
  },

  // 커스텀 EXPLAIN 실행
  explainCustomQuery(query) {
    return axios.post(`${API_BASE_URL}/query/explain-custom`, {
      query: query
    })
  }
}
