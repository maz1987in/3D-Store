# Angular 20 Frontend Documentation

This document provides comprehensive information about the Angular 20 frontend application for the 3D Store project.

## 🚀 Overview

The frontend is built with Angular 20 and provides a modern, responsive user interface for the 3D Store application. It includes features for 3D model upload, print job management, product catalog, and business administration.

## 🛠️ Technology Stack

- **Angular**: 20.x
- **TypeScript**: 5.x
- **Angular Material**: Latest version
- **NgRx**: State management
- **Three.js**: 3D visualization
- **RxJS**: Reactive programming
- **Angular CLI**: Development tools

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── file-upload/   # 3D model upload component
│   │   │   ├── print-preview/ # 3D model preview
│   │   │   ├── order-card/    # Order display component
│   │   │   ├── product-card/  # Product display component
│   │   │   └── shared/        # Shared components
│   │   ├── pages/             # Main page components
│   │   │   ├── home/          # Landing page
│   │   │   ├── products/      # Product catalog
│   │   │   ├── orders/        # Order management
│   │   │   ├── dashboard/     # User dashboard
│   │   │   ├── admin/         # Admin panel
│   │   │   └── seller/        # Seller portal
│   │   ├── services/          # API services
│   │   │   ├── api.service.ts # Main API service
│   │   │   ├── auth.service.ts # Authentication service
│   │   │   ├── upload.service.ts # File upload service
│   │   │   └── websocket.service.ts # Real-time updates
│   │   ├── models/            # TypeScript interfaces
│   │   │   ├── product.model.ts
│   │   │   ├── order.model.ts
│   │   │   ├── user.model.ts
│   │   │   └── print-job.model.ts
│   │   ├── guards/            # Route guards
│   │   │   ├── auth.guard.ts
│   │   │   └── role.guard.ts
│   │   ├── interceptors/      # HTTP interceptors
│   │   │   └── auth.interceptor.ts
│   │   └── shared/            # Shared modules
│   │       ├── material.module.ts
│   │       └── common.module.ts
│   ├── assets/                # Static assets
│   │   ├── images/           # Images and icons
│   │   ├── models/           # 3D model samples
│   │   └── i18n/             # Translation files
│   ├── environments/          # Environment configurations
│   │   ├── environment.ts    # Development
│   │   └── environment.prod.ts # Production
│   └── styles/               # Global styles
│       ├── styles.scss
│       └── themes/           # Material themes
├── angular.json              # Angular configuration
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript configuration
└── karma.conf.js             # Testing configuration
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Angular CLI 20
- Backend API running on localhost:5000

### Installation

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   # Copy environment template
   cp src/environments/environment.example.ts src/environments/environment.ts
   
   # Edit environment.ts with your API URL
   export const environment = {
     production: false,
     apiUrl: 'http://localhost:5000/3dstore/api/v1',
     wsUrl: 'ws://localhost:5000/ws'
   };
   ```

3. **Start development server**
   ```bash
   ng serve
   ```

4. **Open application**
   Navigate to `http://localhost:4200`

## 🎨 Key Features

### 3D Model Upload
- Drag-and-drop file upload interface
- Support for STL, OBJ, 3MF formats
- Real-time file validation
- 3D model preview with Three.js

### Print Job Management
- Real-time status tracking
- Progress monitoring
- Print queue visualization
- Quality control interface

### Product Catalog
- Browse custom services and ready-made products
- Advanced filtering and search
- Product comparison
- Shopping cart functionality

### User Dashboard
- Order history and tracking
- Print job status
- Account management
- Payment history

### Admin Panel
- Business analytics
- User management
- Print job monitoring
- Financial reporting

### Seller Portal
- Commission tracking
- Performance analytics
- Customer management
- Payment history

## 🔧 Development

### Available Scripts

```bash
# Development
ng serve                    # Start development server
ng build                    # Build for production
ng test                     # Run unit tests
ng e2e                      # Run e2e tests

# Code Generation
ng generate component <name> # Generate component
ng generate service <name>   # Generate service
ng generate module <name>    # Generate module

# Linting and Formatting
ng lint                     # Run ESLint
ng format                    # Format code
```

### Code Style

- Use TypeScript strict mode
- Follow Angular style guide
- Use Angular Material components
- Implement reactive forms
- Use NgRx for state management

### Testing

```bash
# Unit tests
ng test

# E2E tests
ng e2e

# Coverage report
ng test --code-coverage
```

## 🌐 Internationalization

The application supports multiple languages:

- **English** (default)
- **Arabic** (RTL support)

Translation files are located in `src/assets/i18n/`

## 📱 Responsive Design

- Mobile-first approach
- Angular Material responsive components
- Progressive Web App (PWA) capabilities
- Touch-friendly interfaces

## 🔐 Authentication

- JWT-based authentication
- Role-based access control
- Route guards for protection
- HTTP interceptors for token management

## 📊 State Management

Using NgRx for complex state management:

- **Actions**: Define actions for state changes
- **Reducers**: Handle state transitions
- **Effects**: Handle side effects
- **Selectors**: Query state data

## 🚀 Deployment

### Build for Production

```bash
ng build --prod
```

### Environment Configuration

Configure production environment in `src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.3dstore.com/3dstore/api/v1',
  wsUrl: 'wss://api.3dstore.com/ws'
};
```

## 🔗 API Integration

The frontend communicates with the backend through:

- **REST API**: HTTP requests for CRUD operations
- **WebSocket**: Real-time updates for print jobs
- **File Upload**: Multipart form data for 3D models

## 📚 Additional Resources

- [Angular Documentation](https://angular.io/docs)
- [Angular Material](https://material.angular.io/)
- [NgRx Documentation](https://ngrx.io/)
- [Three.js Documentation](https://threejs.org/docs/)

## 🤝 Contributing

1. Follow the coding standards
2. Write unit tests for new features
3. Update documentation
4. Submit pull requests

## 📞 Support

For frontend-specific questions:
- Check the Angular documentation
- Review the component documentation
- Create an issue in the repository
