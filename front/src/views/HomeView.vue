<template>
  <div class="container">
    <!-- 로딩 오버레이 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>{{ loadingMessage }}</p>
    </div>

    <h1>데이터베이스 성능 비교 데모</h1>

    <!-- Step 1: 테이블 준비 -->
    <div class="control-panel">
      <h2>Step 1. 테이블 준비</h2>

      <div class="step-content">
        <div class="option-group">
          <h3>📋 CSV 컬럼 선택</h3>
          <p class="description">테스트할 컬럼을 선택하세요</p>

          <div class="column-grid">
            <label v-for="col in availableColumns" :key="col" class="column-checkbox">
              <input type="checkbox" :value="col" v-model="selectedColumns" :disabled="isLoading">
              <span>{{ col }}</span>
            </label>
          </div>

          <div class="action-buttons">
            <button
              @click="createTableWithSelectedColumns"
              :disabled="isLoading || selectedColumns.length === 0"
              class="btn-primary"
            >
              선택한 컬럼으로 테이블 생성 ({{ selectedColumns.length }}개)
            </button>
            <button
              @click="createFullTable"
              :disabled="isLoading"
              class="btn-secondary"
            >
              전체 컬럼으로 테이블 생성 ({{ availableColumns.length }}개)
            </button>
          </div>
        </div>

        <!-- 테이블 상태 표시 -->
        <div v-if="currentTable" class="table-status">
          <h4>✅ 현재 테이블: {{ currentTable }}</h4>
          <p>컬럼: {{ tableColumns.join(', ') }}</p>
          <p>행 개수: {{ tableRowCount }}개</p>
        </div>
      </div>
    </div>

    <!-- Step 2: 인덱스 설정 (테이블 생성 후에만 표시) -->
    <div v-if="currentTable" class="control-panel">
      <h2>Step 2. 인덱스 설정</h2>

      <div class="step-content">
        <div class="index-controls">
          <div class="index-create">
            <label>인덱스를 생성할 컬럼:</label>
            <select v-model="indexColumn" :disabled="isLoading">
              <option value="">컬럼 선택</option>
              <option v-for="col in tableColumns" :key="col" :value="col">
                {{ col }}
              </option>
            </select>
            <button
              @click="createIndex"
              :disabled="isLoading || !indexColumn"
              class="btn-primary"
            >
              인덱스 생성
            </button>
          </div>

          <div v-if="currentIndex" class="index-status">
            <span class="status-badge">현재 인덱스: {{ currentIndex }}</span>
            <button @click="dropIndex" :disabled="isLoading" class="btn-danger">
              인덱스 삭제
            </button>
          </div>
          <div v-else class="index-status">
            <span class="status-badge-inactive">인덱스 없음</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: 쿼리 실행 및 성능 비교 (테이블 생성 후에만 표시) -->
    <div v-if="currentTable" class="control-panel">
      <h2>Step 3. 쿼리 실행 및 성능 비교</h2>

      <div class="step-content">
        <div class="query-controls">
          <button @click="executeQuery" :disabled="isLoading" class="btn-primary">
            🔍 일반 조회 실행
          </button>
          <button @click="executeExplain" :disabled="isLoading" class="btn-primary">
            📊 EXPLAIN ANALYZE 실행
          </button>
        </div>

        <!-- 실행 결과 즉시 표시 -->
        <div v-if="queryTime !== null" class="quick-result">
          <div class="result-item">
            <span class="label">실행 시간:</span>
            <span class="value highlight">{{ queryTime }}ms</span>
          </div>
          <div class="result-item" v-if="rowType">
            <span class="label">Row Type:</span>
            <span class="value">{{ rowType }}</span>
          </div>
          <div class="result-item">
            <span class="label">조회 행 수:</span>
            <span class="value">{{ rowCount }}개</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 시작 안내 (테이블 없을 때) -->
    <div v-if="!currentTable" class="welcome-message">
      <h2>👆 Step 1에서 테이블을 먼저 생성해주세요</h2>
      <p>CSV 파일의 컬럼을 선택하거나 전체 컬럼으로 테이블을 생성하여 시작하세요.</p>
    </div>

    <!-- 결과 표시 영역 -->
    <div v-if="tableData.length > 0" class="results-section">
      <h2>📈 조회 결과</h2>
      <div class="main-layout">
        <DataTable :data="tableData" :columns="tableColumns" />
        <QueryInfo
          :queryTime="queryTime"
          :rowType="rowType"
          :rowCount="rowCount"
        />
      </div>
    </div>

    <!-- 히스토리 -->
    <div v-if="queryHistory.length > 0">
      <QueryHistory :history="queryHistory" />
    </div>
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

      currentTable: null,      // 현재 생성된 테이블 이름
      tableRowCount: 0,        // 테이블 행 개수
      tableColumns: [],

      indexColumn: '',
      currentIndex: null,

      tableData: [],
      queryTime: null,
      rowCount: 0,
      rowType: null,
      explainData: null,

      queryHistory: [],

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
      this.loadingMessage = '전체 컬럼 테이블 생성 중...'
      try {
        const response = await api.createFullTable()
        this.currentTable = 'full_table'
        this.tableColumns = response.data.details.columns
        this.tableRowCount = response.data.details.rows_inserted
        this.selectedColumns = [...this.availableColumns] // 전체 선택 상태로
        alert(`테이블 생성 완료!\n행 개수: ${this.tableRowCount}개`)
      } catch (error) {
        alert('테이블 생성 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    async createTableWithSelectedColumns() {
      this.isLoading = true
      this.loadingMessage = '선택한 컬럼으로 테이블 생성 중...'
      try {
        const response = await api.createTable(this.selectedColumns)
        this.currentTable = 'test_table'
        this.tableColumns = this.selectedColumns
        this.tableRowCount = response.data.details?.rows_inserted || 0
        alert('테이블 생성 완료!')
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
        await api.createIndex(this.currentTable, this.indexColumn, indexName)
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
        await api.dropIndex(this.currentTable, this.currentIndex)
        this.currentIndex = null
        this.indexColumn = ''
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
        const response = await api.executeQuery(this.currentTable)
        this.tableData = response.data.data
        this.queryTime = response.data.query_time
        this.rowCount = response.data.row_count
        this.rowType = null

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
        const response = await api.explainQuery(this.currentTable)
        this.tableData = response.data.data
        this.queryTime = response.data.query_time
        this.rowCount = response.data.count

        const explainData = response.data.explain_data
        this.rowType = explainData.type  // ✅ 이제 type 있음
        this.explainData = explainData

        this.addToHistory('EXPLAIN ANALYZE', this.queryTime, explainData)
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
        rowType: explainData?.type || 'N/A',
        tableName: this.currentTable
      })
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
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

/* 컨트롤 패널 */
.control-panel {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.control-panel h2 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  border-bottom: 3px solid #3498db;
  padding-bottom: 10px;
}

.step-content {
  margin-top: 20px;
}

/* 옵션 그룹 */
.option-group h3 {
  color: #34495e;
  margin-bottom: 10px;
}

.description {
  color: #7f8c8d;
  margin-bottom: 15px;
  font-size: 14px;
}

/* 컬럼 그리드 */
.column-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.column-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.column-checkbox:hover {
  background: #e9ecef;
  border-color: #3498db;
}

.column-checkbox input[type="checkbox"] {
  cursor: pointer;
}

/* 버튼 스타일 */
.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

.btn-danger {
  background: #e74c3c;
  color: white;
  padding: 6px 12px;
  font-size: 13px;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* 테이블 상태 */
.table-status {
  margin-top: 20px;
  padding: 15px;
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
  border-left: 4px solid #28a745;
}

.table-status h4 {
  margin: 0 0 10px 0;
  color: #155724;
}

.table-status p {
  margin: 5px 0;
  color: #155724;
  font-size: 14px;
}

/* 인덱스 컨트롤 */
.index-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.index-create {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.index-create label {
  font-weight: 500;
  color: #34495e;
}

.index-create select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
}

.index-status {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-badge {
  padding: 6px 12px;
  background: #28a745;
  color: white;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
}

.status-badge-inactive {
  padding: 6px 12px;
  background: #6c757d;
  color: white;
  border-radius: 4px;
  font-size: 13px;
}

/* 쿼리 컨트롤 */
.query-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

/* 빠른 결과 */
.quick-result {
  display: flex;
  gap: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 4px solid #3498db;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.result-item .label {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
}

.result-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.result-item .value.highlight {
  color: #3498db;
  font-size: 24px;
}

/* 환영 메시지 */
.welcome-message {
  text-align: center;
  padding: 60px 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 20px 0;
}

.welcome-message h2 {
  color: #3498db;
  margin-bottom: 15px;
}

.welcome-message p {
  color: #6c757d;
  font-size: 16px;
}

/* 결과 섹션 */
.results-section {
  margin-top: 30px;
}

.results-section h2 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.main-layout {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }

  .column-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>
