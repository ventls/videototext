<template>
  <div class="chart-container">
    <div id="k-line-chart" ref="chartRef"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { init, dispose } from 'klinecharts'
import axios from 'axios'

// 图表引用
const chartRef = ref(null)
const chart = ref(null)

// 数据处理函数，将字符串转换为K线图所需的数据格式
const formatKLineData = (dataArr) => {
  return dataArr.map(item => {
    const [
      time, 
      open, 
      close, 
      high, 
      low, 
      volume,
      amount,
      turnoverRate,
      indexChange,
      indexChangeAmount,
      amplitude
    ] = item.split(',')
    
    return {
      timestamp: new Date(time).getTime(),
      time,
      open: parseFloat(open),
      close: parseFloat(close),
      high: parseFloat(high),
      low: parseFloat(low),
      volume: parseFloat(volume),
      turnover: parseFloat(amount),
      turnoverRate: parseFloat(turnoverRate),
      change: parseFloat(indexChange),
      changeAmount: parseFloat(indexChangeAmount),
      amplitude: parseFloat(amplitude)
    }
  })
}

// 初始化图表
const initChart = async () => {
  try {
    // 获取数据
    const response = await axios.get('/api/composite-index')
    const kLineData = formatKLineData(response.data)
    
    // 创建图表实例
    chart.value = init(chartRef.value)
    
    // 配置图表样式 - 红涨绿跌
    chart.value.setStyles({
      grid: {
        show: true,
        horizontal: {
          show: true,
          size: 1,
          color: '#EDEDED',
          style: 'dashed',
          dashedValue: [2, 2]
        },
        vertical: {
          show: true,
          size: 1,
          color: '#EDEDED',
          style: 'dashed',
          dashedValue: [2, 2]
        }
      },
      candle: {
        type: 'candle_solid',
        bar: {
          compareRule: 'current_open',
          upColor: '#F44336',   // 上涨红色
          downColor: '#4CAF50', // 下跌绿色
          noChangeColor: '#888888',
          upBorderColor: '#F44336',
          downBorderColor: '#4CAF50',
          noChangeBorderColor: '#888888',
          upWickColor: '#F44336',
          downWickColor: '#4CAF50',
          noChangeWickColor: '#888888'
        },
        tooltip: {
          showRule: 'always',
          showType: 'standard',
          custom: [
            { title: '时间', value: '{time}' },
            { title: '开盘', value: '{open}' },
            { title: '最高', value: '{high}' },
            { title: '最低', value: '{low}' },
            { title: '收盘', value: '{close}' },
            { title: '成交量', value: '{volume}' },
            { title: '成交额', value: '{turnover}' }
          ]
        }
      },
      indicator: {
        lines: [
          { style: 'solid', size: 1, color: '#FF9600' }, // MA5
          { style: 'solid', size: 1, color: '#935EBD' }  // MA20
        ]
      },
      xAxis: {
        show: true,
        axisLine: {
          show: true,
          color: '#888888',
          size: 1
        },
        tickText: {
          show: true,
          color: '#666666',
          size: 12
        }
      },
      yAxis: {
        show: true,
        position: 'right',
        type: 'normal',
        axisLine: {
          show: true,
          color: '#888888',
          size: 1
        },
        tickText: {
          show: true,
          color: '#666666',
          size: 12
        }
      }
    })
    
    // 设置主图表数据
    chart.value.applyNewData(kLineData)
    
    // 添加MA指标
    chart.value.createTechnicalIndicator('MA', false, {
      id: 'candle_pane',
      series: [
        { name: 'MA5', size: 5 },
        { name: 'MA20', size: 20 }
      ]
    })

    // 添加成交额指标
    const volumePane = chart.value.createTechnicalIndicator({
      name: 'VOL',
      calcParams: [5, 10],
      figures: [
        { key: 'turnover' }
      ],
      styles: {
        bars: [{
          style: 'fill',
          borderStyle: 'solid',
          borderSize: 1,
          upColor: 'rgba(244, 67, 54, 0.7)',
          downColor: 'rgba(76, 175, 80, 0.7)',
          noChangeColor: '#888888'
        }]
      },
      calc: (kLineDataList) => {
        return kLineDataList.map(data => ({
          turnover: data.turnover,
          volume: data.volume
        }))
      }
    }, false, {
      id: 'volume-pane',
      height: 80
    })

    // 添加KDJ指标
    chart.value.createTechnicalIndicator('KDJ', false, {
      id: 'kdj-pane',
      height: 80,
      calcParams: [9, 3, 3]
    })

  } catch (error) {
    console.error('加载K线图数据失败:', error)
  }
}

// 组件挂载完成后初始化图表
onMounted(() => {
  initChart()
})

// 组件卸载前清理图表资源
onUnmounted(() => {
  if (chart.value) {
    dispose(chartRef.value)
  }
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 600px;
  margin: 0 auto;
  border: 1px solid #ddd;
}

#k-line-chart {
  width: 100%;
  height: 100%;
}
</style>