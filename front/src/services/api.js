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

  // 기존 함수들...
  createTable(columns) {
    return axios.post(`${API_BASE_URL}/table/create`, { columns })
  },

  createIndex(tableName, columnName, indexName = null) {
    return axios.post(`${API_BASE_URL}/index/create`, {
      table_name: tableName,
      column_name: columnName,
      index_name: indexName
    })
  },

  dropIndex(tableName, indexName) {
    return axios.delete(`${API_BASE_URL}/index/drop`, {
      params: { table_name: tableName, index_name: indexName }
    })
  },

  executeQuery(tableName, conditions = null) {
    return axios.post(`${API_BASE_URL}/query/execute`, {
      table_name: tableName,
      conditions
    })
  },

  explainQuery(tableName, conditions = null) {
    return axios.post(`${API_BASE_URL}/query/explain`, {
      table_name: tableName,
      conditions
    })
  }
}
