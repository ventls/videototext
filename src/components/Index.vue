<template>
  <div class="container">
    <h1>视频转文字工具</h1>
    
    <div class="upload-section">
      <input 
        type="file" 
        @change="handleFileChange" 
        accept="video/*"
        ref="fileInput"
      >
      <button 
        @click="uploadVideo" 
        :disabled="!selectedFile || isUploading"
        class="upload-btn"
      >
        {{ isUploading ? '上传中...' : '上传视频' }}
      </button>
    </div>

    <div v-if="currentFile" class="file-info">
      <p>当前文件: {{ currentFile }}</p>
      <button 
        @click="startConversion" 
        :disabled="isConverting"
        class="convert-btn"
      >
        {{ isConverting ? '转换中...' : '开始转换' }}
      </button>
    </div>

    <div class="output-section">
      <h2>转换进度</h2>
      <div class="progress-box" ref="progressBox">
        <div v-for="(message, index) in messages" :key="index" 
             :class="['message', message.type]">
          {{ message.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Index',
  data() {
    return {
      selectedFile: null,
      currentFile: null,
      isUploading: false,
      isConverting: false,
      messages: [],
      eventSource: null
    }
  },
  methods: {
    handleFileChange(event) {
      this.selectedFile = event.target.files[0]
    },
    async uploadVideo() {
      if (!this.selectedFile) return

      this.isUploading = true
      const formData = new FormData()
      formData.append('video', this.selectedFile)

      try {
        const response = await fetch('http://localhost:5000/upload', {
          method: 'POST',
          body: formData
        })
        const data = await response.json()
        
        if (response.ok) {
          this.currentFile = data.filename
          this.messages = []
          this.$refs.fileInput.value = ''
        } else {
          alert('上传失败: ' + data.error)
        }
      } catch (error) {
        alert('上传出错: ' + error.message)
      } finally {
        this.isUploading = false
      }
    },
    async startConversion() {
      if (!this.currentFile) return

      this.isConverting = true
      this.messages = []

      try {
        // 关闭之前的 SSE 连接
        if (this.eventSource) {
          this.eventSource.close()
        }

        // 建立新的 SSE 连接
        this.eventSource = new EventSource('http://localhost:5000/stream')
        
        this.eventSource.onmessage = (event) => {
          const data = JSON.parse(event.data)
          if (data.type === 'ping') return  // 忽略心跳消息
          
          this.messages.push(data)
          // 自动滚动到底部
          this.$nextTick(() => {
            const progressBox = this.$refs.progressBox
            progressBox.scrollTop = progressBox.scrollHeight
          })
        }

        this.eventSource.onerror = (error) => {
          console.error('SSE Error:', error)
          this.eventSource.close()
          this.isConverting = false
        }

        // 发送转换请求
        const response = await fetch('http://localhost:5000/convert', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ filename: this.currentFile })
        })

        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.error)
        }
      } catch (error) {
        alert('转换出错: ' + error.message)
        this.isConverting = false
      }
    }
  },
  beforeUnmount() {
    // 组件销毁前关闭 SSE 连接
    if (this.eventSource) {
      this.eventSource.close()
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.upload-section {
  margin: 20px 0;
  display: flex;
  gap: 10px;
  align-items: center;
}

.file-info {
  margin: 20px 0;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.output-section {
  margin-top: 30px;
}

.progress-box {
  height: 400px;
  overflow-y: auto;
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.message {
  margin: 5px 0;
  padding: 5px;
  border-bottom: 1px solid #eee;
}

.message.status {
  color: #2196F3;
  font-weight: bold;
}

.message.error {
  color: #f44336;
  font-weight: bold;
}

button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #4CAF50;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #45a049;
}

.convert-btn {
  background-color: #2196F3;
}

.convert-btn:hover:not(:disabled) {
  background-color: #1976D2;
}
</style>