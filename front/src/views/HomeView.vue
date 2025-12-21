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
              @click="createFullTable"
              :disabled="isLoading"
              class="btn-primary"
            >
              전체 컬럼으로 테이블 생성 ({{ availableColumns.length }}개)
            </button>
            <button
              @click="createTableWithSelectedColumns"
              :disabled="isLoading || selectedColumns.length === 0"
              class="btn-secondary"
            >
              선택한 컬럼으로 테이블 생성 ({{ selectedColumns.length }}개)
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

    <!-- Step 2: 인덱스 설정 -->
    <div v-if="currentTable" class="control-panel">
      <h2>Step 2. 인덱스 설정</h2>

      <div class="step-content">
        <!-- 인덱스 타입 선택 -->
        <div class="index-type-selector">
          <label class="radio-option">
            <input type="radio" value="single" v-model="indexType" />
            <span>단일 컬럼 인덱스</span>
          </label>
          <label class="radio-option">
            <input type="radio" value="composite" v-model="indexType" />
            <span>복합 인덱스 (여러 컬럼)</span>
          </label>
        </div>

        <!-- 인덱스 생성 폼 -->
        <div class="index-create-section">
          <h3>🔧 새 인덱스 생성</h3>

          <!-- 단일 인덱스 폼 -->
          <div v-if="indexType === 'single'" class="index-create-form">
            <div class="form-group">
              <label>컬럼 선택:</label>
              <select v-model="singleIndexColumn" :disabled="isLoading">
                <option value="">컬럼 선택</option>
                <option v-for="col in tableColumns" :key="col" :value="col">
                  {{ col }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>인덱스 이름 (선택):</label>
              <input
                type="text"
                v-model="customIndexName"
                placeholder="미입력시 자동 생성"
                :disabled="isLoading"
              />
            </div>
            <button
              @click="createSingleIndex"
              :disabled="isLoading || !singleIndexColumn"
              class="btn-primary"
            >
              ➕ 단일 인덱스 추가
            </button>
          </div>

          <!-- 복합 인덱스 폼 -->
          <div v-else class="composite-index-form">
            <div class="composite-columns-section">
              <label>컬럼 선택 (순서 중요):</label>
              <div class="columns-selector">
                <div class="available-columns">
                  <h4>사용 가능한 컬럼</h4>
                  <div class="column-list">
                    <div
                      v-for="col in availableColumnsForComposite"
                      :key="col"
                      class="column-item"
                      @click="addToComposite(col)"
                    >
                      <span>{{ col }}</span>
                      <button class="btn-add">➕</button>
                    </div>
                  </div>
                </div>

                <div class="arrow">→</div>

                <div class="selected-columns">
                  <h4>선택된 컬럼 ({{ compositeColumns.length }}개)</h4>
                  <div class="column-list">
                    <div
                      v-for="(col, index) in compositeColumns"
                      :key="col"
                      class="column-item selected"
                    >
                      <span class="order-number">{{ index + 1 }}</span>
                      <span>{{ col }}</span>
                      <div class="item-actions">
                        <button
                          @click="moveUp(index)"
                          :disabled="index === 0"
                          class="btn-move"
                        >
                          ⬆️
                        </button>
                        <button
                          @click="moveDown(index)"
                          :disabled="index === compositeColumns.length - 1"
                          class="btn-move"
                        >
                          ⬇️
                        </button>
                        <button
                          @click="removeFromComposite(index)"
                          class="btn-remove"
                        >
                          ❌
                        </button>
                      </div>
                    </div>
                    <div v-if="compositeColumns.length === 0" class="empty-message">
                      왼쪽에서 컬럼을 선택하세요
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>복합 인덱스 이름 (선택):</label>
              <input
                type="text"
                v-model="customIndexName"
                :placeholder="`미입력시 자동 생성: idx_${compositeColumns.join('_')}`"
                :disabled="isLoading"
              />
            </div>

            <button
              @click="createCompositeIndex"
              :disabled="isLoading || compositeColumns.length < 2"
              class="btn-primary"
            >
              ➕ 복합 인덱스 추가 ({{ compositeColumns.length }}개 컬럼)
            </button>
          </div>
        </div>

        <!-- 현재 인덱스 목록 -->
        <div class="index-list-section">
          <h3>📋 현재 인덱스 목록</h3>
          <div v-if="indexList.length === 0" class="no-index">
            <p>생성된 인덱스가 없습니다</p>
          </div>
          <div v-else class="index-list">
            <div
              v-for="(index, idx) in indexList"
              :key="index.name"
              class="index-item"
            >
              <div class="index-info">
                <span class="index-number">{{ idx + 1 }}</span>
                <div class="index-details">
                  <span class="index-name">{{ index.name }}</span>
                  <span class="index-column">
                    <span v-if="index.columns.length === 1">
                      컬럼: {{ index.columns[0] }}
                    </span>
                    <span v-else class="composite-badge">
                      복합 ({{ index.columns.length }}개): {{ index.columns.join(' → ') }}
                    </span>
                  </span>
                </div>
              </div>
              <button
                @click="dropIndex(index.name)"
                :disabled="isLoading"
                class="btn-delete"
              >
                🗑️ 삭제
              </button>
            </div>
          </div>

          <!-- 전체 인덱스 삭제 -->
          <div v-if="indexList.length > 0" class="index-actions">
            <button
              @click="dropAllIndexes"
              :disabled="isLoading"
              class="btn-danger-outline"
            >
              전체 인덱스 삭제
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: 쿼리 실행 및 성능 비교 -->
    <div v-if="currentTable" class="control-panel">
      <h2>Step 3. 쿼리 실행 및 성능 비교</h2>

      <div class="step-content">
        <!-- 쿼리 모드 선택 -->
        <div class="query-mode-selector">
          <label class="radio-option">
            <input type="radio" value="simple" v-model="queryMode" />
            <span>간단 조회 (전체)</span>
          </label>
          <label class="radio-option">
            <input type="radio" value="custom" v-model="queryMode" />
            <span>직접 쿼리 작성</span>
          </label>
        </div>

        <!-- 간단 조회 모드 -->
        <div v-if="queryMode === 'simple'" class="simple-query-section">
          <div class="query-controls">
            <button @click="executeQuery" :disabled="isLoading" class="btn-primary">
              🔍 전체 조회 실행
            </button>
            <button @click="executeExplain" :disabled="isLoading" class="btn-primary">
              📊 EXPLAIN ANALYZE 실행
            </button>
          </div>
        </div>

        <!-- 직접 쿼리 작성 모드 -->
        <div v-else class="custom-query-section">
          <div class="query-editor">
            <div class="editor-header">
              <h4>🔧 SQL 쿼리 작성</h4>
              <div class="editor-actions">
                <button @click="insertTemplate('basic')" class="btn-small">기본 템플릿</button>
                <button @click="insertTemplate('where')" class="btn-small">WHERE 템플릿</button>
                <button @click="insertTemplate('join')" class="btn-small">JOIN 템플릿</button>
                <button @click="clearQuery" class="btn-small">초기화</button>
              </div>
            </div>

            <textarea
              v-model="customQuery"
              placeholder="SELECT * FROM full_table WHERE 컬럼명 = '값' LIMIT 100"
              class="query-textarea"
              :disabled="isLoading"
              rows="6"
            ></textarea>

            <div class="query-help">
              <p><strong>💡 팁:</strong></p>
              <ul>
                <li>테이블명: <code>{{ currentTable }}</code></li>
                <li>사용 가능한 컬럼: {{ tableColumns.slice(0, 5).join(', ') }}{{ tableColumns.length > 5 ? '...' : '' }}</li>
                <li>WHERE 절을 추가하여 인덱스 성능을 테스트하세요</li>
                <li>LIMIT을 추가하여 결과 수를 제한하는 것을 권장합니다</li>
              </ul>
            </div>

            <div class="query-controls">
              <button @click="executeCustomQuery" :disabled="isLoading || !customQuery" class="btn-primary">
                ▶️ 쿼리 실행
              </button>
              <button @click="executeCustomExplain" :disabled="isLoading || !customQuery" class="btn-primary">
                📊 EXPLAIN ANALYZE 실행
              </button>
            </div>
          </div>
        </div>

        <!-- 쿼리 정보 -->
        <div v-if="queryTime !== null" class="query-info-inline">
          <div class="info-item">
            <span class="label">실행 시간:</span>
            <span class="value highlight">{{ queryTime }}ms</span>
          </div>
          <div class="info-item">
            <span class="label">Row Type:</span>
            <span class="value">{{ rowType || 'N/A' }}</span>
          </div>
          <div class="info-item">
            <span class="label">예상 행 수:</span>
            <span class="value">{{ estimatedRows || 'N/A' }}</span>
          </div>
          <div class="info-item">
            <span class="label">실제 조회 수:</span>
            <span class="value">{{ rowCount }}개</span>
          </div>
          <div class="info-item" v-if="usedKey">
            <span class="label">사용된 인덱스:</span>
            <span class="value">{{ usedKey }}</span>
          </div>
        </div>

        <!-- 실행된 쿼리 표시 -->
        <div v-if="lastExecutedQuery" class="executed-query">
          <h4>실행된 쿼리:</h4>
          <pre>{{ lastExecutedQuery }}</pre>
        </div>
      </div>
    </div>


    <!-- 시작 안내 -->
    <div v-if="!currentTable" class="welcome-message">
      <h2>👆 Step 1에서 테이블을 먼저 생성해주세요</h2>
      <p>CSV 파일의 컬럼을 선택하거나 전체 컬럼으로 테이블을 생성하여 시작하세요.</p>
    </div>

    <!-- 조회 결과 -->
    <div v-if="tableData.length > 0" class="results-section">
      <h2>📈 조회 결과</h2>
      <DataTable :data="tableData" :columns="displayColumns" />
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
import QueryHistory from '@/components/QueryHistory.vue'

export default {
  components: { DataTable, QueryHistory },
  data() {
    return {
      availableColumns: [],
      selectedColumns: [],

      currentTable: null,
      tableRowCount: 0,
      tableColumns: [],        // 테이블의 전체 컬럼
      displayColumns: [],      // 실제 표시할 컬럼 (추가)

      // 인덱스 관련
      indexType: 'single',           // 'single' or 'composite'
      singleIndexColumn: '',         // 단일 인덱스용 컬럼
      compositeColumns: [],          // 복합 인덱스용 컬럼 배열
      customIndexName: '',
      indexList: [],

      // 쿼리 관련 (추가)
      queryMode: 'simple',           // 'simple' or 'custom'
      customQuery: '',               // 사용자 작성 쿼리
      lastExecutedQuery: '',         // 마지막 실행 쿼리

      tableData: [],
      queryTime: null,
      rowCount: 0,
      rowType: null,
      estimatedRows: null,
      usedKey: null,
      explainData: null,

      queryHistory: [],

      isLoading: false,
      loadingMessage: ''
    }
  },
  computed: {
    availableColumnsForComposite() {
      return this.tableColumns.filter(col => !this.compositeColumns.includes(col))
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
        this.selectedColumns = [...this.availableColumns]

        // 이미 존재했던 테이블인지 확인
        if (response.data.details.existed) {
          this.indexList = []  // 인덱스 목록 초기화하지 않음
          alert(`기존 테이블을 사용합니다.\n행 개수: ${this.tableRowCount}개`)
        } else {
          this.indexList = []  // 새 테이블이므로 초기화
          alert(`테이블 생성 완료!\n행 개수: ${this.tableRowCount}개`)
        }
      } catch (error) {
        alert('테이블 생성 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    // 복합 인덱스 컬럼 관리
    addToComposite(column) {
      this.compositeColumns.push(column)
    },

    removeFromComposite(index) {
      this.compositeColumns.splice(index, 1)
    },

    moveUp(index) {
      if (index > 0) {
        const temp = this.compositeColumns[index]
        this.compositeColumns[index] = this.compositeColumns[index - 1]
        this.compositeColumns[index - 1] = temp
      }
    },

    moveDown(index) {
      if (index < this.compositeColumns.length - 1) {
        const temp = this.compositeColumns[index]
        this.compositeColumns[index] = this.compositeColumns[index + 1]
        this.compositeColumns[index + 1] = temp
      }
    },

    // 단일 인덱스 생성
    async createSingleIndex() {
      this.isLoading = true
      this.loadingMessage = '단일 인덱스 생성 중...'
      try {
        const indexName = this.customIndexName || `idx_${this.singleIndexColumn}`

        if (this.indexList.some(idx => idx.name === indexName)) {
          alert('이미 존재하는 인덱스 이름입니다.')
          return
        }

        await api.createIndex(this.currentTable, this.singleIndexColumn, indexName)

        this.indexList.push({
          name: indexName,
          columns: [this.singleIndexColumn]
        })

        this.singleIndexColumn = ''
        this.customIndexName = ''

        alert('단일 인덱스 생성 완료!')
      } catch (error) {
        alert('인덱스 생성 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    // 복합 인덱스 생성
    async createCompositeIndex() {
      this.isLoading = true
      this.loadingMessage = '복합 인덱스 생성 중...'
      try {
        const indexName = this.customIndexName || `idx_${this.compositeColumns.join('_')}`

        if (this.indexList.some(idx => idx.name === indexName)) {
          alert('이미 존재하는 인덱스 이름입니다.')
          return
        }

        await api.createCompositeIndex(
          this.currentTable,
          this.compositeColumns,
          indexName
        )

        this.indexList.push({
          name: indexName,
          columns: [...this.compositeColumns]
        })

        this.compositeColumns = []
        this.customIndexName = ''

        alert('복합 인덱스 생성 완료!')
      } catch (error) {
        alert('복합 인덱스 생성 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    async dropIndex(indexName) {
      if (!confirm(`인덱스 '${indexName}'를 삭제하시겠습니까?`)) {
        return
      }

      this.isLoading = true
      this.loadingMessage = '인덱스 삭제 중...'
      try {
        await api.dropIndex(this.currentTable, indexName)
        this.indexList = this.indexList.filter(idx => idx.name !== indexName)
        alert('인덱스 삭제 완료!')
      } catch (error) {
        alert('인덱스 삭제 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    async dropAllIndexes() {
      if (!confirm(`모든 인덱스(${this.indexList.length}개)를 삭제하시겠습니까?`)) {
        return
      }

      this.isLoading = true
      this.loadingMessage = '모든 인덱스 삭제 중...'
      try {
        for (const index of this.indexList) {
          await api.dropIndex(this.currentTable, index.name)
        }
        this.indexList = []
        alert('모든 인덱스 삭제 완료!')
      } catch (error) {
        alert('인덱스 삭제 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },
    // 쿼리 템플릿 삽입
    insertTemplate(type) {
      const templates = {
        basic: `SELECT * FROM ${this.currentTable} LIMIT 100`,
        where: `SELECT * FROM ${this.currentTable}\nWHERE ${this.tableColumns[0]} = '값'\nLIMIT 100`,
        join: `SELECT * FROM ${this.currentTable} t1\nWHERE ${this.tableColumns[0]} = '값'\nLIMIT 100`
      }
      this.customQuery = templates[type] || templates.basic
    },

    clearQuery() {
      this.customQuery = ''
      this.lastExecutedQuery = ''
    },

    async createFullTable() {
      this.isLoading = true
      this.loadingMessage = '전체 컬럼 테이블 생성 중...'
      try {
        const response = await api.createFullTable()
        this.currentTable = 'full_table'
        this.tableColumns = response.data.details.columns
        this.displayColumns = response.data.details.columns  // 초기에는 전체 컬럼
        this.tableRowCount = response.data.details.rows_inserted
        this.selectedColumns = [...this.availableColumns]
        this.indexList = []
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

        // 서버에서 자동 생성된 테이블명 사용
        this.currentTable = response.data.details.table_name
        this.tableColumns = this.selectedColumns
        this.displayColumns = this.selectedColumns
        this.tableRowCount = response.data.details.rows_inserted

        // 재사용한 테이블인지 확인
        if (response.data.details.existed) {
          alert(`기존 테이블을 재사용합니다.\n테이블명: ${this.currentTable}\n행 개수: ${this.tableRowCount}개`)
        } else {
          this.indexList = []
          alert(`테이블 생성 완료!\n테이블명: ${this.currentTable}\n행 개수: ${this.tableRowCount}개`)
        }
      } catch (error) {
        alert('테이블 생성 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },
    // 결과 데이터에서 실제 컬럼 추출
    extractColumnsFromData(data) {
      if (data && data.length > 0) {
        return Object.keys(data[0])
      }
      return []
    },

    // 간단 조회
    async executeQuery() {
      this.isLoading = true
      this.loadingMessage = '쿼리 실행 중...'
      try {
        const response = await api.executeQuery(this.currentTable)
        this.tableData = response.data.data
        this.queryTime = response.data.query_time
        this.rowCount = response.data.count
        this.rowType = null
        this.estimatedRows = null
        this.usedKey = null
        this.lastExecutedQuery = `SELECT * FROM ${this.currentTable} LIMIT 100`

        // 실제 반환된 컬럼으로 설정
        this.displayColumns = this.extractColumnsFromData(this.tableData)

        this.addToHistory('SELECT', this.queryTime, null, this.lastExecutedQuery)
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
        this.rowType = explainData.type
        this.estimatedRows = explainData.rows
        this.usedKey = explainData.key
        this.explainData = explainData
        this.lastExecutedQuery = `SELECT * FROM ${this.currentTable} LIMIT 100`

        // 실제 반환된 컬럼으로 설정
        this.displayColumns = this.extractColumnsFromData(this.tableData)

        this.addToHistory('EXPLAIN ANALYZE', this.queryTime, explainData, this.lastExecutedQuery)
      } catch (error) {
        alert('EXPLAIN 실행 실패: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },

    // 커스텀 쿼리 실행
    async executeCustomQuery() {
      this.isLoading = true
      this.loadingMessage = '커스텀 쿼리 실행 중...'
      try {
        const response = await api.executeCustomQuery(this.customQuery)
        this.tableData = response.data.data
        this.queryTime = response.data.query_time
        this.rowCount = response.data.count
        this.rowType = null
        this.estimatedRows = null
        this.usedKey = null
        this.lastExecutedQuery = this.customQuery

        // 실제 반환된 컬럼으로 설정
        this.displayColumns = this.extractColumnsFromData(this.tableData)

        this.addToHistory('CUSTOM SELECT', this.queryTime, null, this.customQuery)
      } catch (error) {
        console.error('쿼리 실행 에러:', error)
        alert(`쿼리 실행 실패:\n${error.response?.data?.detail || error.message}`)
      } finally {
        this.isLoading = false
      }
    },

    async executeCustomExplain() {
      this.isLoading = true
      this.loadingMessage = '커스텀 EXPLAIN ANALYZE 실행 중...'
      try {
        const response = await api.explainCustomQuery(this.customQuery)
        this.tableData = response.data.data
        this.queryTime = response.data.query_time
        this.rowCount = response.data.count

        const explainData = response.data.explain_data
        this.rowType = explainData.type
        this.estimatedRows = explainData.rows
        this.usedKey = explainData.key
        this.explainData = explainData
        this.lastExecutedQuery = this.customQuery

        // 실제 반환된 컬럼으로 설정
        this.displayColumns = this.extractColumnsFromData(this.tableData)

        this.addToHistory('CUSTOM EXPLAIN', this.queryTime, explainData, this.customQuery)
      } catch (error) {
        console.error('EXPLAIN 실행 에러:', error)
        alert(`EXPLAIN 실행 실패:\n${error.response?.data?.detail || error.message}`)
      } finally {
        this.isLoading = false
      }
    },

    addToHistory(type, time, explainData, query) {
      this.queryHistory.push({
        timestamp: new Date().toLocaleString(),
        type,
        time,
        indexes: this.indexList.map(idx => idx.name).join(', ') || 'None',
        rowType: explainData?.type || 'N/A',
        tableName: this.currentTable,
        query: query  // 추가
      })
    }
  }
}
</script>

<style scoped>
@import '@/assets/styles/home-view.css';
</style>
