<template>
    <div class="container">
      <div class="index-grid">
        <div class="index-item">
          <h3>上证指数</h3>
          <img src="https://image.sinajs.cn/newchart/min/n/sh000001.gif" alt="上证指数" />
        </div>
        <div class="index-item">
          <h3>深证成指</h3>
          <img src="https://image.sinajs.cn/newchart/min/n/sz399001.gif" alt="深证成指" />
        </div>
        <div class="index-item">
          <h3>创业板指</h3>
          <img src="https://image.sinajs.cn/newchart/min/n/sz399006.gif" alt="创业板指" />
        </div>
        <div class="index-item">
          <h3>科创50</h3>
          <img src="https://image.sinajs.cn/newchart/min/n/sh000688.gif" alt="科创50" />
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  // No additional setup needed for this component
  </script>
  
  <style scoped>
  .container {
    padding: 20px;
  }
  
  .index-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
  }
  
  .index-item {
    flex: 1;
    min-width: 280px;
    text-align: center;
  }
  
  .index-item h3 {
    margin-bottom: 10px;
    color: #333;
    font-size: 16px;
  }
  
  .index-item img {
    width: 100%;
    max-width: 100%;
    height: auto;
    border: 1px solid #eee;
    border-radius: 4px;
  }
  
  @media (max-width: 1200px) {
    .index-item {
      flex: 0 1 calc(50% - 10px);
    }
  }
  
  @media (max-width: 640px) {
    .index-item {
      flex: 0 1 100%;
    }
  }
  </style>