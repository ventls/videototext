<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElButton } from 'element-plus' // 引入 Element Plus Button

const title = ref('市场情绪')
const marketTrend = ref([])

const fetchData = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/market-trend');
    console.log('市场涨跌幅数据:', response.data);
    marketTrend.value = response.data
    renderChart();
  } catch (error) {
    console.error('获取市场涨跌幅数据失败:', error);
  }
}

onMounted(fetchData) // 初始加载数据

const renderChart = () => {
  const chartDom = document.getElementById('marketTrendChart');
  const myChart = echarts.init(chartDom);
  
  const xAxisData = [
    '跌停', '-10', '-9', '-8', '-7', '-6', '-5', '-4', '-3', '-2', '-1', 
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '涨停'
  ];
  
  const seriesData = new Array(xAxisData.length).fill(0);

  marketTrend.value.forEach(item => {
    const key = Object.keys(item)[0];
    const value = item[key];
    const index = xAxisData.indexOf(key);
    if (index !== -1) {
      seriesData[index] = value; // 更新对应的值
    }
  });

  // 显式设置涨停和跌停的值
  seriesData[xAxisData.indexOf('涨停')] = marketTrend.value.find(item => '11' in item) ? marketTrend.value.find(item => '11' in item)['11'] : 0;
  seriesData[xAxisData.indexOf('跌停')] = marketTrend.value.find(item => '-11' in item) ? marketTrend.value.find(item => '-11' in item)['-11'] : 0;

  const option = {
    title: {
      text: '市场涨跌分布'
    },
    tooltip: {},
    xAxis: {
      type: 'category',
      data: xAxisData,
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: '涨跌幅',
      type: 'bar',
      data: seriesData,
      itemStyle: {
        color: function(params) {
          const name = params.name;

          if (name === '0') {
            return '#cccccc'; // 背景色为灰色
          } else if (name === '涨停') {
            return '#ff0000'; // 涨停深红
          } else if (name === '跌停') {
            return '#005500'; // 跌停深绿
          } else if (parseInt(name) < 0) {
            const greenIntensity = Math.abs(parseInt(name)) / 11; 
            return `rgba(0, 255, 0, ${greenIntensity})`; 
          } else {
            const redIntensity = parseInt(name) / 10; 
            return `rgba(255, 0, 0, ${redIntensity})`; 
          }
        }
      }
    }]
  };

  myChart.setOption(option);
}

// 计算上涨和下跌家数
const upCount = computed(() => {
  return marketTrend.value.reduce((count, item) => {
    const key = Object.keys(item)[0];
    return count + (parseInt(key) > 0 ? item[key] : 0);
  }, 0);
});

const downCount = computed(() => {
  return marketTrend.value.reduce((count, item) => {
    const key = Object.keys(item)[0];
    return count + (parseInt(key) < 0 ? item[key] : 0);
  }, 0);
});

// 上涨状态
const upBarWidth = computed(() => {
  const totalCount = upCount.value + Math.abs(downCount.value);
  return totalCount > 0 ? `${(upCount.value / totalCount) * 100}%` : '0px';
});

// 下跌状态
const downBarWidth = computed(() => {
  const totalCount = upCount.value + Math.abs(downCount.value);
  return totalCount > 0 ? `${(Math.abs(downCount.value) / totalCount) * 100}%` : '0px';
});


// 标签显示
const upCountLabel = computed(() => `上涨家数: ${upCount.value}`);
const downCountLabel = computed(() => `下跌家数: ${Math.abs(downCount.value)}`);
</script>




<template>
  <div class="market-sentiment">
    <h1 class="text-2xl font-bold mb-4">{{ title }}</h1>
    <el-button type="primary" @click="fetchData">刷新数据</el-button>
    <div id="marketTrendChart" style="width: 600px; height: 300px;"></div>
    
    <div class="status-container">
      <div class="status-bar" >
        <div :style="{ width: downBarWidth }" class="downbar"></div>
        <div :style="{ width: upBarWidth }" class="upbar"></div>
      </div>


      <div class="status_foot">
          <span class="label down-count-label">{{ downCountLabel }}</span> 
          <span class="label up-count-label">{{ upCountLabel }}</span>
      </div>
    </div>
  </div>
</template>




<style scoped>
.market-sentiment {
  padding: 20px;
}
.status-container {
    display: flex;
    /* align-items: center; */
    margin-top: 20px;
    flex-direction: column;
    width: 400px;
}
.status_foot{
  width: 550px;
  display: flex;
  justify-content: space-between;
}


.status-bar {
  display: flex;
  width: 550px;
  height: 20px;
}
.upbar{
  background-color: rgb(255, 39, 39);
  height: 20px;
  
}
.downbar{
  background-color: rgb(66, 230, 66);
  height: 20px;
  
}


.label {
  font-size: 14px;
  margin: 0 10px;
}
.up-count-label {
  color: red;
  margin: 0px;
}
.down-count-label {
  color: green;
  margin: 0px;
}
</style>