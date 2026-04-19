import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
	server: {
		host: '0.0.0.0',
		allowedHosts: true,
		proxy: {
			'/auth': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true,
			},
			'/users': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true,
			},
			'/friends': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true,
			},
			'/items': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true,
			},
			'/game': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true,
			},
			'/ws': {
				target: 'ws://127.0.0.1:8000',
				ws: true,
				changeOrigin: true,
			},
		},
	},
	plugins: [
		vue(),
		vueJsx(),
		vueDevTools(),
	],
	resolve: {
		alias: {
			'@': fileURLToPath(new URL('./src', import.meta.url))
		},
	},

})
