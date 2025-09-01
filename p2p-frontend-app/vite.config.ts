import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// https://vite.dev/config/
export default defineConfig(() => {
  const isDevelopmentMode = process.env.MODE === 'development'
  
  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      host: true,
      port: 5173,
      watch: {
        usePolling: true
      }
    },
    build: {
      target: isDevelopmentMode ? 'esnext' : 'es2015',
      minify: isDevelopmentMode ? false : 'esbuild' as const,
      sourcemap: isDevelopmentMode
    },
    esbuild: {
      target: isDevelopmentMode ? 'esnext' : 'es2015'
    }
  }
})
