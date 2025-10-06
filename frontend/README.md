# Proposal Bot Frontend

Modern React TypeScript frontend for the Proposal Bot application, built with Vite, Tailwind CSS, and Framer Motion.

## Features

- ⚡️ **Modern Stack**: React 18, TypeScript, Vite
- 🎨 **Beautiful UI**: Tailwind CSS with custom design system
- 🚀 **Smooth Animations**: Framer Motion for delightful interactions
- 📱 **Responsive Design**: Mobile-first approach
- 🔧 **Developer Experience**: Hot reload, TypeScript support, ESLint
- 🎯 **Interactive Elements**: Drag & drop file uploads, progress indicators
- 🌈 **Gradient Design**: Modern gradient-based color scheme

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

### Backend Integration

The frontend is configured to proxy API requests to the FastAPI backend running on `http://localhost:8000`. Make sure your backend is running before testing the frontend.

Start the backend:
```bash
# From the project root
cd .. 
python -m uvicorn web.app:app --reload --port 8000
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Header.tsx       # Navigation header
│   │   └── Footer.tsx       # Site footer
│   ├── pages/               # Page components
│   │   ├── HomePage.tsx     # Main landing/proposal page
│   │   ├── PlatformPage.tsx # Platform capabilities
│   │   └── OutputsPage.tsx  # Generated outputs
│   ├── services/            # API integration
│   │   └── api.ts           # FastAPI backend integration
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts         # Shared interfaces
│   ├── utils/               # Utility functions
│   │   └── index.ts         # Helper functions
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # App entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── index.html               # HTML template
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── package.json             # Dependencies and scripts
```

## Key Features

### 🎨 Modern Design System

- **Custom Tailwind Theme**: Extended color palette with primary, secondary, and accent colors
- **Responsive Components**: Mobile-first design with smooth breakpoints
- **Interactive Elements**: Hover effects, transitions, and micro-animations
- **Glass Morphism**: Modern glass effects for overlay elements

### 📁 File Upload System

- **Drag & Drop Interface**: Intuitive file upload with visual feedback
- **Multiple File Support**: PWS/SoW and RFP document uploads
- **File Type Validation**: Supports PDF, DOCX, MD, TXT, YAML
- **Progress Tracking**: Real-time upload and processing progress

### 🔄 API Integration

- **FastAPI Backend**: Seamless integration with existing Python backend
- **File Processing**: Document upload and proposal generation
- **Download Management**: Secure file downloads with proper MIME types
- **Error Handling**: Graceful error states and user feedback

### 📊 Interactive Dashboard

- **Platform Capabilities**: Visual capability cards with status indicators
- **Output Management**: File listing, preview, and download functionality
- **Pricing Display**: Dynamic pricing tier visualization
- **Status Tracking**: Real-time processing status updates

## Technology Stack

### Core Framework
- **React 18**: Latest React with concurrent features
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server

### Styling & UI
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Production-ready motion library
- **Lucide React**: Beautiful icon set

### Development Tools
- **ESLint**: Code linting and quality
- **PostCSS**: CSS processing
- **Autoprefixer**: CSS vendor prefixing

### API & Data
- **Axios**: HTTP client for API requests
- **React Router**: Client-side routing
- **React Dropzone**: File upload handling

## Deployment

### Build for Production

```bash
npm run build
```

This creates a `dist` folder with optimized production files.

### Environment Variables

The frontend automatically detects the environment:
- **Development**: API requests go to `http://localhost:8000`
- **Production**: API requests use relative URLs

### Integration with Existing Backend

The React frontend can be served alongside the FastAPI backend by:

1. Building the frontend: `npm run build`
2. Copying `dist/*` to `web/static/react/`
3. Adding a new FastAPI route to serve the React app

Example FastAPI integration:
```python
@app.get("/react", response_class=HTMLResponse)
def react_app():
    return FileResponse("web/static/react/index.html")
```

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+

## Contributing

1. Follow TypeScript best practices
2. Use Tailwind utility classes
3. Add proper type definitions
4. Test on multiple screen sizes
5. Ensure accessibility compliance

## License

Same as the main Proposal Bot project.