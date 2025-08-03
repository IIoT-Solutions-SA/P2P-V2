# Story 2: Frontend Development Environment Setup

## Story Details
**Epic**: Epic 1 - Project Foundation & Development Environment  
**Story Points**: 5  
**Priority**: High  
**Dependencies**: Story 1 (Repository Initialization)

## User Story
**As a** frontend developer  
**I want** a configured React + Vite environment with all necessary libraries  
**So that** I can start building UI components immediately

## Acceptance Criteria
- [x] React + Vite project initialized with TypeScript support
- [x] Tailwind CSS configured with custom P2P Sandbox theme
- [x] shadcn/ui component library integrated and configured
- [x] i18n setup for Arabic/English support with RTL handling
- [x] React Router configured with basic route structure
- [x] ESLint and Prettier configured with team standards
- [x] Interactive Saudi Arabia map with Leaflet.js for use case display
- [x] Sample pages demonstrating all integrations working
- [x] Development server runs without errors

## Technical Specifications

### 1. Project Initialization

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
```

### 2. Dependencies Installation

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "react-i18next": "^14.0.0",
    "i18next": "^23.8.0",
    "i18next-browser-languagedetector": "^7.2.0",
    "i18next-http-backend": "^2.4.0",
    "axios": "^1.6.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "class-variance-authority": "^0.7.0",
    "lucide-react": "^0.312.0",
    "@radix-ui/react-slot": "^1.0.2",
    "leaflet": "^1.9.4",
    "react-leaflet": "^4.2.1"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/node": "^20.0.0",
    "@types/leaflet": "^1.9.8",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.56.0",
    "eslint-config-prettier": "^9.1.0",
    "eslint-plugin-react": "^7.33.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.0",
    "postcss": "^8.4.0",
    "prettier": "^3.2.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

### 3. Tailwind CSS Configuration

#### tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["Inter", "Noto Sans Arabic", "system-ui", "sans-serif"],
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

#### src/index.css
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

[dir="rtl"] {
  direction: rtl;
}
```

### 4. i18n Configuration

#### src/i18n/config.ts
```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpApi from 'i18next-http-backend';

i18n
  .use(HttpApi)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    debug: import.meta.env.DEV,
    
    interpolation: {
      escapeValue: false,
    },

    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },

    detection: {
      order: ['querystring', 'cookie', 'localStorage', 'navigator'],
      caches: ['localStorage', 'cookie'],
    },
  });

export default i18n;
```

#### public/locales/en/translation.json
```json
{
  "app": {
    "title": "P2P Sandbox for SMEs",
    "tagline": "Empowering Saudi Industries Through Collaboration"
  },
  "nav": {
    "home": "Home",
    "forum": "Forum",
    "useCases": "Use Cases",
    "training": "Training",
    "about": "About",
    "login": "Login",
    "register": "Register"
  },
  "home": {
    "welcome": "Welcome to P2P Sandbox",
    "description": "Connect with fellow factory owners, share insights, and accelerate your digital transformation journey."
  }
}
```

#### public/locales/ar/translation.json
```json
{
  "app": {
    "title": "منصة P2P للمؤسسات الصغيرة والمتوسطة",
    "tagline": "تمكين الصناعات السعودية من خلال التعاون"
  },
  "nav": {
    "home": "الرئيسية",
    "forum": "المنتدى",
    "useCases": "دراسات الحالة",
    "training": "التدريب",
    "about": "عن المنصة",
    "login": "تسجيل الدخول",
    "register": "إنشاء حساب"
  },
  "home": {
    "welcome": "مرحباً بكم في منصة P2P",
    "description": "تواصل مع أصحاب المصانع الآخرين، شارك الأفكار، وسرّع رحلة التحول الرقمي لمؤسستك."
  }
}
```

### 5. shadcn/ui Setup

#### src/lib/utils.ts
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

#### src/components/ui/button.tsx
```typescript
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline:
          "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

### 6. Router Configuration

#### src/App.tsx
```typescript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useEffect } from 'react';
import Layout from './components/Layout';
import Home from './pages/Home';
import Forum from './pages/Forum';
import UseCases from './pages/UseCases';
import NotFound from './pages/NotFound';

function App() {
  const { i18n } = useTranslation();

  useEffect(() => {
    document.dir = i18n.language === 'ar' ? 'rtl' : 'ltr';
  }, [i18n.language]);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="forum" element={<Forum />} />
          <Route path="use-cases" element={<UseCases />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
```

### 7. ESLint Configuration

#### .eslintrc.cjs
```javascript
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'plugin:react/recommended',
    'prettier'
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
```

### 8. Prettier Configuration

#### .prettierrc
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "endOfLine": "lf"
}
```

### 9. Sample Components

#### src/pages/Home.tsx
```typescript
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import SaudiUseCaseMap from '@/components/SaudiUseCaseMap';

export default function Home() {
  const { t } = useTranslation();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-4">{t('home.welcome')}</h1>
      <p className="text-lg text-muted-foreground mb-8">
        {t('home.description')}
      </p>
      
      {/* Saudi Arabia Use Case Map */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">{t('home.useCaseMap')}</h2>
        <SaudiUseCaseMap />
      </div>
      
      <div className="flex gap-4">
        <Button>{t('nav.register')}</Button>
        <Button variant="outline">{t('nav.forum')}</Button>
      </div>
    </div>
  );
}
```

#### src/components/SaudiUseCaseMap.tsx
```typescript
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Mock use case data with Saudi Arabia locations
const mockUseCases = [
  {
    id: 1,
    title: 'Smart Manufacturing - Riyadh',
    location: [24.7136, 46.6753] as [number, number],
    industry: 'Manufacturing',
    description: 'IoT-enabled production line optimization'
  },
  {
    id: 2,
    title: 'Oil & Gas Automation - Dammam',
    location: [26.4207, 50.0888] as [number, number],
    industry: 'Oil & Gas',
    description: 'Automated pipeline monitoring system'
  },
  {
    id: 3,
    title: 'Smart Logistics - Jeddah',
    location: [21.4858, 39.1925] as [number, number],
    industry: 'Logistics',
    description: 'RFID-based warehouse management'
  },
  {
    id: 4,
    title: 'Food Processing Innovation - Khobar',
    location: [26.2791, 50.2080] as [number, number],
    industry: 'Food Processing',
    description: 'Automated quality control system'
  }
];

export default function SaudiUseCaseMap() {
  // Saudi Arabia center coordinates
  const saudiCenter: [number, number] = [23.8859, 45.0792];

  return (
    <div className="h-96 w-full rounded-lg overflow-hidden border">
      <MapContainer
        center={saudiCenter}
        zoom={6}
        className="h-full w-full"
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {mockUseCases.map((useCase) => (
          <Marker key={useCase.id} position={useCase.location}>
            <Popup>
              <div className="p-2">
                <h3 className="font-semibold text-sm">{useCase.title}</h3>
                <p className="text-xs text-gray-600 mb-1">{useCase.industry}</p>
                <p className="text-xs">{useCase.description}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
```

## Implementation Steps

1. **Initialize Vite Project**
   ```bash
   cd frontend
   npm create vite@latest . -- --template react-ts
   ```

2. **Install All Dependencies**
   ```bash
   npm install [all dependencies listed above]
   ```

3. **Install Map Dependencies**
   ```bash
   npm install leaflet react-leaflet
   npm install -D @types/leaflet
   ```

4. **Configure Build Tools**
   - Set up Tailwind CSS
   - Configure PostCSS
   - Set up path aliases in tsconfig.json

5. **Set Up i18n**
   - Create translation files
   - Configure language detection
   - Implement RTL support

6. **Create Component Library**
   - Set up shadcn/ui components
   - Create base UI components

7. **Configure Development Environment**
   - ESLint and Prettier setup
   - VS Code settings
   - Git hooks for linting

## Testing Checklist
- [ ] Development server starts without errors
- [ ] Language switching works (English/Arabic)
- [ ] RTL layout activates for Arabic
- [ ] All routes load correctly
- [ ] shadcn/ui components render properly
- [ ] Saudi Arabia map loads with use case markers
- [ ] Map markers show correct popup information
- [ ] ESLint and Prettier run without errors
- [ ] TypeScript compilation succeeds

## Dependencies
- Story 1 must be completed (repository structure exists)

## Notes
- Ensure all team members have the same Node.js version
- Document any additional UI components as they're added
- Keep translation files updated as features are added