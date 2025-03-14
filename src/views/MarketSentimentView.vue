<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const title = ref('股市成交榜')
const stocks = ref([])
const showCharts = ref(false) // 控制图表显示的开关
const loadedImages = ref(new Set())

onMounted(async () => {
  try {
    const response = await axios.get('/api/stocks')
    stocks.value = response.data
  } catch (error) {
    console.error('获取股票数据失败:', error)
  }
})

// 监听开关变化，处理图片加载
function handleSwitchChange(value) {
  if (value) {
    // 开关打开时，每隔0.1秒加载一行图片
    stocks.value.forEach((stock, index) => {
      setTimeout(() => {
        loadedImages.value.add(stock.f12)
      }, index * 100) // 每100ms加载一行
    })
  } else {
    // 开关关闭时，清空已加载图片集合
    loadedImages.value.clear()
  }
}

function getChartUrl(code) {
  const market = code.startsWith('6') || code.startsWith('5') ? 'sh' : 'sz'
  return `https://image.sinajs.cn/newchart/small/n${market}${code}.gif`
}

function getDailyKUrl(code) {
  const market = code.startsWith('6') || code.startsWith('5') ? 'sh' : 'sz'
  return `https://image.sinajs.cn/newchart/daily/n/${market}${code}.gif`
}

function getZfColor(zf) {
  if (zf <= -9.5) return '#008000'
  if (zf <= -7.5) return '#229922'
  if (zf <= -5.5) return '#44bb44'
  if (zf <= -3.5) return '#66dd66'
  if (zf <= -1.5) return '#88ff88'
  if (zf < 1.5) return 'white'
  if (zf <= 3.5) return '#ffcccc'
  if (zf <= 5.5) return '#ff9999'
  if (zf <= 7.5) return '#ff6666'
  if (zf <= 9.5) return '#ff3333'
  return '#cc0000'
}
</script>

<template>
  <div class="market-trading">
    <div class="header-container">
      <h1 class="text-2xl font-bold mb-4">{{ title }}</h1>
      <div class="switch-container">
        <span>显示分时图和日K线</span>
        <el-switch
          v-model="showCharts"
          @change="handleSwitchChange"
          style="--el-switch-on-color: #13ce66;"
        />
      </div>
    </div>
    <div class="content">
      <table>
        <thead>
          <tr>
            <th>序号</th>
            <th>股票代码</th>
            <th>股票名称</th>
            <th>最新价</th>
            <th>涨跌幅</th>
            <th>成交金额</th>
            <th>市盈率(动态)</th>
            <th>日K线</th>
            <th>分时图</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(stock, index) in stocks" :key="stock.f12">
            <td>{{ index + 1 }}</td>
            <td>{{ stock.f12 }}</td>
            <td>{{ stock.f14 }}</td>
            <td>{{ (stock.f2 / 100).toFixed(2) }}</td>
            <td :style="{ backgroundColor: getZfColor(stock.f3 / 100) }">
              {{ (stock.f3 / 100).toFixed(2) }}%
            </td>
            <td>{{ (stock.f6 / 100000000).toFixed(2) }}亿元</td>
            <td>{{ (stock.f9 / 100).toFixed(2) }}</td>
            <td style="background-color: white; width: 565px; text-align: center;">
              <img 
                v-if="showCharts && loadedImages.has(stock.f12)"
                :src="getDailyKUrl(stock.f12)" 
                class="chart" 
                alt="日K线" 
                style="width: 545px;"
              >
            </td>
            <td style="background-color: white; width: 280px; text-align: center;">
              <img 
                v-if="showCharts && loadedImages.has(stock.f12)"
                :src="getChartUrl(stock.f12)" 
                alt="分时图" 
                style="width: 250px;"
              >
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.market-trading {
  height: calc(100vh - 100px);
}
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.switch-container {
  display: flex;
  align-items: center;
  gap: 10px;
}
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
  width: 100px;
  height: auto;
}
</style>