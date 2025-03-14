<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeIndex = ref('1')

const handleSelect = (key) => {
  switch (key) {
    case '1':
      router.push('/')
      break
    case '2':
      router.push('/market-sentiment')
      break
    case '3':
      router.push('/market-trading')
      break
    case '4':
      router.push('/my-stocks')
      break
    case '5':
      router.push('/about')
      break
  }
}
</script>

<template>
  <div class="app-container">
    <el-menu
      :default-active="activeIndex"
      class="el-menu-demo"
      mode="horizontal"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#ffd04b"
      @select="handleSelect"
    >
      <el-menu-item index="1">视频STT文字提取</el-menu-item>
    </el-menu>

    <div class="main-content">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.app-container {
  width: 100vw;
  display: flex;
  flex-direction: column;
}

.el-menu-demo {
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
}

.main-content {
  flex: 1;
  padding: 20px;
  margin-top: 59px; /* 确保内容不会被菜单遮挡 */
  overflow: auto; /* 允许滚动 */
}
</style>