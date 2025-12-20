<!-- QueryInfo.vue -->
<template>
  <div class="query-info">
    <h3>쿼리 정보</h3>
    <div class="info-content">
      <div class="info-item">
        <span class="label">실행 시간:</span>
        <span class="value highlight">{{ queryTime ? queryTime + 'ms' : 'N/A' }}</span>
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
        <span class="value">{{ rowCount || 0 }}개</span>
      </div>
      <div class="info-item" v-if="usedKey">
        <span class="label">사용된 인덱스:</span>
        <span class="value">{{ usedKey }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QueryInfo',
  props: {
    queryTime: Number,
    rowType: String,
    rowCount: Number,
    estimatedRows: Number,  // 추가
    usedKey: String  // 추가
  }
}
</script>
