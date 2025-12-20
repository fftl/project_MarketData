<template>
  <div class="container">
    <!-- 로딩 오버레이 추가 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>{{ loadingMessage }}</p>
    </div>

    <!-- 컨트롤 패널 -->
    <div class="control-panel">
      <h2>데이터베이스 컨트롤</h2>

      <!-- 0. 전체 테이블 생성 -->
      <div class="section">
        <h3>0. 전체 컬럼 테이블 생성</h3>
        <p>CSV의 모든 컬럼: {{ availableColumns.join(', ') }}</p>
        <button @click="createFullTable" :disabled="isLoading">
          전체 테이블 생성 (to_sql)
        </button>
        <button @click="loadTableData" v-if="tableCreated" :disabled="isLoading">
          데이터 조회
        </button>
      </div>

      <!-- 1. 테이블 생성 -->
      <div class="section">
        <h3>1. 특정 컬럼만 선택해서 테이블 생성</h3>
        <div>
          <label v-for="col in availableColumns" :key="col">
            <input type="checkbox" :value="col" v-model="selectedColumns" :disabled="isLoading">
            {{ col }}
          </label>
        </div>
        <button @click="createTable" :disabled="isLoading">
          선택한 컬럼으로 테이블 생성
        </button>
      </div>

      <!-- 2. 인덱스 관리 -->
      <div class="section">
        <h3>2. 인덱스 관리</h3>
        <select v-model="indexColumn" :disabled="isLoading">
          <option v-for="col in selectedColumns" :key="col" :value="col">
            {{ col }}
          </option>
        </select>
        <button @click="createIndex" :disabled="isLoading">인덱스 생성</button>
        <button @click="dropIndex" v-if="currentIndex" :disabled="isLoading">
          인덱스 삭제
        </button>
        <p v-if="currentIndex">현재 인덱스: {{ currentIndex }}</p>
      </div>

      <!-- 3. 쿼리 실행 -->
      <div class="section">
        <h3>3. 쿼리 실행</h3>
        <button @click="executeQuery" :disabled="isLoading">데이터 조회</button>
        <button @click="executeExplain" :disabled="isLoading">EXPLAIN ANALYZE</button>
      </div>
    </div>

    <!-- 메인 레이아웃 -->
    <div class="main-layout">
      <DataTable :data="tableData" :columns="tableColumns" />
      <QueryInfo
        :queryTime="queryTime"
        :rowType="explainData?.type"
        :rowCount="rowCount"
      />
    </div>

    <QueryHistory :history="queryHistory" />
  </div>
</template>

<script>
import api from '@/services/api'
import DataTable from '@/components/DataTable.vue'
import QueryInfo from '@/components/QueryInfo.vue'
import QueryHistory from '@/components/QueryHistory.vue'

export default {
  components: { DataTable, QueryInfo, QueryHistory },
  data() {
    return {
      availableColumns: [],
      selectedColumns: [],
      tableCreated: false,

      indexColumn: '',
      currentIndex: null,

      tableData: [],
      tableColumns: [],
      queryTime: null,
      rowCount: 0,
      explainData: null,

      queryHistory: [],

      // 로딩 상태 추가
      isLoading: false,
      loadingMessage: ''
    }
  },
  async mounted() {
    await this.loadCsvColumns()
  },
  methods: {
    async loadCsvColumns() {
      this.isLoading = true
      this.loadingMessage = 'CSV 컬럼 로딩 중...'
      try {
        const response = await api.getCsvColumns()
        this.availableColumns = response.data.columns
      } catch (error) {
        alert('CSV 컬럼 로딩 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    async createFullTable() {
      this.isLoading = true
      this.loadingMessage = '전체 테이블 생성 중... (시간이 걸릴 수 있습니다)'
      try {
        const response = await api.createFullTable()
        alert(`테이블 생성 완료!\n행 개수: ${response.data.details.rows_inserted}`)
        this.tableCreated = true
        this.tableColumns = response.data.details.columns
      } catch (error) {
        alert('테이블 생성 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    async loadTableData() {
      this.isLoading = true
      this.loadingMessage = '데이터 조회 중...'
      try {
        const response = await api.getTableData('full_table')
        this.tableData = response.data.data
        this.rowCount = response.data.count
      } catch (error) {
        alert('데이터 조회 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    async createTable() {
      this.isLoading = true
      this.loadingMessage = '선택한 컬럼으로 테이블 생성 중...'
      try {
        const response = await api.createTable(this.selectedColumns)
        alert('테이블 생성 완료!')
        this.tableColumns = this.selectedColumns
      } catch (error) {
        alert('테이블 생성 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    async createIndex() {
      this.isLoading = true
      this.loadingMessage = '인덱스 생성 중...'
      try {
        const indexName = `idx_${this.indexColumn}`
        const response = await api.createIndex('test_table', this.indexColumn, indexName)
        this.currentIndex = indexName
        alert('인덱스 생성 완료!')
      } catch (error) {
        alert('인덱스 생성 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    async dropIndex() {
      this.isLoading = true
      this.loadingMessage = '인덱스 삭제 중...'
      try {
        await api.dropIndex('test_table', this.currentIndex)
        this.currentIndex = null
        alert('인덱스 삭제 완료!')
      } catch (error) {
        alert('인덱스 삭제 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    async executeQuery() {
      this.isLoading = true
      this.loadingMessage = '쿼리 실행 중...'
      try {
        const response = await api.executeQuery('test_table')
        this.tableData = response.data.data
        this.queryTime = response.data.query_time
        this.rowCount = response.data.row_count

        this.addToHistory('SELECT', this.queryTime, null)
      } catch (error) {
        alert('쿼리 실행 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    async executeExplain() {
      this.isLoading = true
      this.loadingMessage = 'EXPLAIN ANALYZE 실행 중...'
      try {
        const response = await api.explainQuery('test_table')
        this.tableData = response.data.data
        this.queryTime = response.data.query_time
        this.rowCount = response.data.row_count
        this.explainData = response.data.explain_data[0]

        this.addToHistory('EXPLAIN ANALYZE', this.queryTime, this.explainData)
      } catch (error) {
        alert('EXPLAIN 실행 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    addToHistory(type, time, explainData) {
      this.queryHistory.push({
        timestamp: new Date().toLocaleString(),
        type,
        time,
        index: this.currentIndex,
        rowType: explainData?.type || 'N/A'
      })
    }
  }
}
</script>

<style scoped>
.container {
  padding: 20px;
  position: relative;
}

/* 로딩 오버레이 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  color: white;
}

/* 로딩 스피너 */
.loading-spinner {
  border: 8px solid #f3f3f3;
  border-top: 8px solid #3498db;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-overlay p {
  font-size: 18px;
  font-weight: bold;
}

.control-panel {
  border: 2px solid black;
  padding: 20px;
  margin-bottom: 20px;
}

.section {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ccc;
}

.main-layout {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

button {
  margin: 5px;
  padding: 8px 16px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

label {
  margin-right: 15px;
}
</style>
