import {defineConfig} from 'vite';
// Preserve the browser host (including its port) in fetched Agent Card URLs.
export default defineConfig({server:{proxy:{'/api':{
  target:process.env.MARKETPLACE_API_PROXY||'http://127.0.0.1:58000',changeOrigin:false,
}}}});
