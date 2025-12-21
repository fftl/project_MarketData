<template>
  <div class="data-table">
    <div class="table-header">
      <h3>데이터 테이블</h3>
      <span v-if="data.length > 0" class="row-count">{{ data.length }}개 행 표시</span>
    </div>
    <p v-if="!data || data.length === 0" class="no-data">데이터가 없습니다</p>
    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th v-for="col in columns" :key="col">{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in data" :key="index">
            <td v-for="col in columns" :key="col">{{ row[col] }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataTable',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    columns: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style scoped>
.data-table {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.table-header h3 {
  margin: 0;
  color: #2c3e50;
}

.row-count {
  color: #6c757d;
  font-size: 14px;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 40px;
  font-style: italic;
}

.table-wrapper {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 600px;  /* 스크롤 최대 높이 */
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;  /* 최소 너비 보장 */
}

thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #f8f9fa;
}

th {
  border: 1px solid #dee2e6;
  padding: 12px 8px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  white-space: nowrap;
  background: #f8f9fa;
}

td {
  border: 1px solid #dee2e6;
  padding: 10px 8px;
  text-align: left;
  white-space: nowrap;
}

tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

tbody tr:hover {
  background-color: #e9ecef;
}

/* 스크롤바 스타일링 */
.table-wrapper::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
