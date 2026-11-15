import {defineConfig} from 'vite';
import {viteSingleFile} from 'vite-plugin-singlefile';
export default defineConfig({plugins:[viteSingleFile()],build:{outDir:'dist-mcp',rollupOptions:{input:'mcp-app.html'}}});
