import {defineConfig} from 'vite';
import {mcpMiddleware} from './mcp-app-server.mjs';
// Preserve the browser host (including its port) in fetched Agent Card URLs.
export default defineConfig({plugins:[{name:'marketplace-mcp-apps',configureServer(server){server.middlewares.use(mcpMiddleware())}}],server:{proxy:{'/api':{
  target:process.env.MARKETPLACE_API_PROXY||'http://127.0.0.1:58000',changeOrigin:false,
}}}});
