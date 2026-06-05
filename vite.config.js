import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
    plugins: [vue()],
    build: {
        lib: {
            entry: resolve(__dirname, 'highspeed_pos/public/js/highspeed_pos.bundle.js'),
            name: 'highspeed_pos',
            fileName: 'highspeed_pos'
        },
        outDir: 'highspeed_pos/public/dist/js',
        emptyOutDir: false,
        rollupOptions: {
            external: ['socket.io-client'],
            output: {
                globals: {
                    'socket.io-client': 'io'
                }
            }
        }
    },
    resolve: {
        alias: {
            '@': resolve(__dirname, 'highspeed_pos/public/js')
        }
    }
})