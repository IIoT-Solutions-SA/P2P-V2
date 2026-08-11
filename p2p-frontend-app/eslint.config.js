import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { globalIgnores } from 'eslint/config'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    rules: {
      // Leaflet marker-cluster and several API payloads are runtime-shaped and
      // do not publish complete TypeScript contracts in this application.
      '@typescript-eslint/no-explicit-any': 'off',
      // Shared component modules intentionally export hooks, variants, and
      // popup serializers alongside React components.
      'react-refresh/only-export-components': 'off',
      // Input validation intentionally detects NUL bytes.
      'no-control-regex': 'off',
    },
  },
])
