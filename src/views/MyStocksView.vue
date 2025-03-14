<template>
    <div>
      <table border="1" cellspacing="0" cellpadding="5">
        <thead>
          <tr>
            <th>序号</th>
            <th>股票代码</th>
            <th>股票名称</th>
            <th>日K线</th>
            <th>分时图</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(stock, index) in mystocks" :key="stock.code">
            <td>{{ index + 1 }}</td>
            <td>{{ stock.code }}</td>
            <td>{{ stock.name }}</td>
            <td style="background-color: white; width: 565px; text-align: center;">
              <img 
                v-if="loadedImages.has(stock.code)"
                :src="getDailyKUrl(stock.code)" 
                class="chart" 
                alt="日K线"
                style="width: 545px;"
                
              >
            </td>
            <td style="background-color: white; width: 280px; text-align: center;">
              <img 
                v-if="loadedImages.has(stock.code)"
                :src="getChartUrl(stock.code)" 
                alt="分时图"
                style="width: 250px;"
              >
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  
  const mystocks = ref([
    { code: "600036", name: "招商银行" },
    { code: "000333", name: "美的集团" },
    { code: "000063", name: "中兴通讯" },
    { code: "601728", name: "中国电信" },
    { code: "601633", name: "长城汽车" },
    { code: "601318", name: "中国平安" },
    { code: "002241", name: "歌尔股份" },
    { code: "600584", name: "长电科技" },
    { code: "603501", name: "韦尔股份" },
    { code: "600276", name: "恒瑞医药" },
    { code: "002415", name: "海康威视" },
    { code: "603127", name: "招衍新药" },
    { code: "002709", name: "天赐材料" },
    { code: "601857", name: "中国石油" },
    { code: "159740", name: "恒生科技ETF" },
    { code: "513050", name: "中概互联网ETF" },
    { code: "513090", name: "香港证券ETF" },
    { code: "512170", name: "医疗ETF" },
    { code: "588200", name: "科创芯片ETF" },
    { code: "511090", name: "30年国债ETF" },

  ]);
  
  const loadedImages = ref(new Set());
  
  const getChartUrl = (code) => {
    const market = code.startsWith('6') || code.startsWith('5') ? 'sh' : 'sz';
    return `https://image.sinajs.cn/newchart/small/n${market}${code}.gif`;
  };
  
  const getDailyKUrl = (code) => {
    const market = code.startsWith('6') || code.startsWith('5') ? 'sh' : 'sz';
    return `https://image.sinajs.cn/newchart/daily/n/${market}${code}.gif`;
  };
  
  onMounted(() => {
    mystocks.value.forEach(stock => {
      loadedImages.value.add(stock.code);
    });
  });
  </script>
  
  <style>
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    border: 1px solid black;
    padding: 8px;
    text-align: left;
  }
  th {
    background-color: #f4f4f4;
  }
  td img {
    height: auto;
  }
  </style>
  