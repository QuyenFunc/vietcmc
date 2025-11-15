import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5000,
    strictPort: true,
    hmr: {
      clientPort: 5000
    },
    allowedHosts: [
      '.ngrok-free.app',
      '.ngrok-free.dev',
      '.ngrok.io',
      '.ngrok.app',
      '.trycloudflare.com',
      '.cloudflare.com',
      '.loca.lt',
      '.serveo.net',
      '.localhost.run',
      'localhost',
      '127.0.0.1'
    ],
    proxy: {
      '/backend': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/backend/, '')
      },
      '/webhooks': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})

