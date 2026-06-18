import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// https://vite.dev/config/
export default defineConfig(() => {
  const isDevelopmentMode = process.env.MODE === 'development'
  const reactPlugins = react()
  
  return {
    plugins: [...reactPlugins, tailwindcss()],
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
      minify: !isDevelopmentMode,
      sourcemap: isDevelopmentMode
    }
  }
})
