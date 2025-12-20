<template>
  <div class="query-info">
    <h3>쿼리 정보</h3>
    <div class="info-content">
      <div class="info-item">
        <span class="label">조회 시간:</span>
        <span class="value">{{ queryTime ? queryTime + 'ms' : 'N/A' }}</span>
      </div>
      <div class="info-item">
        <span class="label">Row Type:</span>
        <span class="value">{{ rowType || 'N/A' }}</span>
      </div>
      <div class="info-item">
        <span class="label">Row Count:</span>
        <span class="value">{{ rowCount || 0 }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QueryInfo',
  props: {
    queryTime: {
      type: Number,
      default: null
    },
    rowType: {
      type: String,
      default: null
    },
    rowCount: {
      type: Number,
      default: 0
    }
  }
}
</script>

<style scoped>
.query-info {
  flex: 1;
  border: 2px solid black;
  padding: 20px;
  min-width: 250px;
}

.info-content {
  margin-top: 15px;
}

.info-item {
  margin: 10px 0;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.label {
  font-weight: bold;
  color: #333;
  display: inline-block;
  width: 120px;
}

.value {
  color: #0066cc;
  font-size: 16px;
}
</style>
