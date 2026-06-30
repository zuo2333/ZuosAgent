import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  // 从 .env 文件加载环境变量
  const env = loadEnv(mode, process.cwd(), '')

  // 后端 API 地址，从环境变量读取，默认值兼容未配置情况
  const apiBaseUrl = env.VITE_API_BASE_URL || 'http://localhost:8001'

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: parseInt(env.FRONTEND_PORT || '5173'),
      proxy: {
        '/api': {
          target: apiBaseUrl,
          changeOrigin: true,
        },
      },
    },
  }
})
