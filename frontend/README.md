# Gorilla Gate Landing Page

Modern, single-page React landing page for Gorilla Gate - a developer-native compliance scanning tool for LLM applications.

## Tech Stack

- **Framework:** Vite + React + TypeScript
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Fonts:** Inter (sans-serif), JetBrains Mono (monospace)

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

The site will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The optimized build will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/        # Navbar, Footer
│   │   ├── sections/      # Page sections (Hero, Features, Pricing, etc.)
│   │   ├── ui/            # Reusable UI components
│   │   └── icons/         # Logo and icons
│   ├── styles/            # Global CSS and Tailwind config
│   ├── App.tsx            # Main app component
│   └── main.tsx           # Entry point
├── index.html
├── package.json
└── vite.config.ts
```

## Features

- **Gradient Orbs** - Animated background decorations
- **Glassmorphism Cards** - Modern card designs with backdrop blur
- **Code Blocks** - Syntax-highlighted code examples with violation warnings
- **Responsive Design** - Mobile-first design that works on all devices
- **SEO Optimized** - Meta tags, Open Graph, and Twitter cards

## Deployment

The site can be deployed to any static hosting platform:

- **Vercel:** `npx vercel`
- **Netlify:** Drag and drop the `dist/` folder
- **GitHub Pages:** Use the build output from `npm run build`

## Design System

### Colors

- Background: Deep navy (#1a1a2e)
- Accent Blue: #4a90d9
- Accent Green: #00d4aa
- Accent Pink: #ff6b9d
- Accent Coral: #ff7b54

### Typography

- Headings: Inter (800 weight)
- Body: Inter (400 weight)
- Code: JetBrains Mono

### Spacing

Mobile-first with responsive breakpoints at 640px, 768px, 1024px, 1280px, and 1536px.
