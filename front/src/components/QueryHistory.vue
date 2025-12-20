<template>
  <div class="query-history">
    <h3>쿼리 히스토리</h3>
    <div v-if="history && history.length > 0" class="history-list">
      <div
        v-for="(item, index) in history"
        :key="index"
        class="history-item"
      >
        <div class="history-header">
          <span class="history-type">{{ item.type }}</span>
          <span class="history-timestamp">{{ item.timestamp }}</span>
        </div>
        <div class="history-details">
          <span class="detail">시간: {{ item.time }}ms</span>
          <span class="detail">인덱스: {{ item.index || 'None' }}</span>
          <span class="detail">Row Type: {{ item.rowType }}</span>
        </div>
      </div>
    </div>
    <p v-else class="no-history">히스토리가 없습니다</p>
  </div>
</template>

<script>
export default {
  name: 'QueryHistory',
  props: {
    history: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style scoped>
.query-history {
  border: 2px solid black;
  padding: 20px;
}

.history-list {
  margin-top: 15px;
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-left: 4px solid #0066cc;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.history-item:hover {
  background-color: #f1f1f1;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.history-type {
  font-weight: bold;
  color: #0066cc;
  font-size: 14px;
}

.history-timestamp {
  color: #666;
  font-size: 12px;
}

.history-details {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.detail {
  font-size: 13px;
  color: #333;
  background-color: white;
  padding: 4px 8px;
  border-radius: 3px;
  border: 1px solid #e0e0e0;
}

.no-history {
  color: #999;
  text-align: center;
  padding: 20px;
  font-style: italic;
}

/* 스크롤바 스타일링 */
.history-list::-webkit-scrollbar {
  width: 8px;
}

.history-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.history-list::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.history-list::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
```

## 파일 위치 확인
```
src/
├── components/
│   ├── DataTable.vue      ← 이미 만드신 것
│   ├── QueryInfo.vue      ← 이 파일 생성
│   └── QueryHistory.vue   ← 이 파일 생성
└── views/
    └── HomeView.vue
