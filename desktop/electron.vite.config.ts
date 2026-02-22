import { resolve } from 'path'
import { defineConfig, loadEnv } from 'electron-vite'
import vue from '@vitejs/plugin-vue'

const env = loadEnv('', process.cwd())

export default defineConfig({
    main: {
        define: {
            'process.env.VITE_API_BASE_URL': JSON.stringify(
                env.VITE_API_BASE_URL || 'http://localhost:8000'
            ),
            'process.env.DATA_SECRET_KEY': JSON.stringify(env.DATA_SECRET_KEY || '')
        }
    },
    preload: {},
    renderer: {
        resolve: {
            alias: {
                '@renderer': resolve('src/renderer/src')
            }
        },
        plugins: [vue()]
    }
})
