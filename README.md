# 3D Store - 3D Home Printing Service Management System

A comprehensive full-stack application designed for managing 3D home printing services, featuring a Flask-based REST API backend and Angular 20 frontend, including custom printing, ready-made products, seller management, and complete business operations.

## 🚀 Overview

3D Store is a complete full-stack business management solution for 3D printing services featuring:

- **Backend**: Flask-based REST API for business logic and data management
- **Frontend**: Angular 20 application for user interfaces and interactions
- **Database**: PostgreSQL/MySQL for data persistence
- **File Storage**: Support for 3D model files and media

The system supports both **custom 3D printing services** and **ready-made product sales**, with comprehensive cost tracking including printing, packaging, and finishing expenses.

## ✨ Key Features

### 🖨️ 3D Printing Services
- **Multi-Material Support**: PLA, ABS, PETG, TPU, Wood-filled, Metal-filled filaments
- **Print Quality Options**: Draft, Standard, High Quality, Ultra High Quality
- **File Format Support**: STL, OBJ, 3MF with automatic validation and repair
- **Real-time Print Monitoring**: Live status updates during printing process
- **Print Time Estimation**: Accurate time calculations based on model complexity

### 📦 Product Management
- **Custom 3D Printing**: Upload models and get instant quotes
- **Ready-Made Products**: Pre-printed inventory for immediate sale
- **Packaging Options**: Keychain, wrapper, tag, custom packaging solutions
- **Complete Cost Tracking**: Print + packaging + finishing + labor costs
- **Dynamic Pricing**: Based on material, complexity, print time, and packaging

### 💰 Business Management
- **Seller Management**: Commission-based seller program with flexible settlement
- **Expense Tracking**: Tools, printers, repairs, materials, and operational costs
- **Financial Reporting**: Revenue analysis, profit margins, and cost breakdown
- **Inventory Management**: Materials and ready-made product stock tracking
- **Multi-location Support**: Manage multiple printing facilities

### 🛒 Customer Experience
- **Easy Model Upload**: Simple 3D model file upload and validation
- **Instant Quoting**: Real-time pricing based on model analysis
- **Order Tracking**: Complete order and print job status updates
- **Print Gallery**: Showcase of completed prints and customer projects
- **Multi-language Support**: Arabic and English interface

## 🏗️ Architecture

### Core Technologies

#### Backend
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy ORM with support for SQLite, MySQL, and PostgreSQL
- **Migrations**: Alembic
- **Authentication**: JWT-based with role-based access control
- **File Storage**: Depot for 3D model files, print images, and documents
- **Caching**: Flask-Caching with Redis support
- **Task Scheduling**: APScheduler for print job queuing and notifications
- **API Documentation**: Swagger UI

#### Frontend
- **Framework**: Angular 20
- **UI Components**: Angular Material
- **State Management**: NgRx
- **HTTP Client**: Angular HttpClient
- **Routing**: Angular Router
- **Forms**: Reactive Forms
- **3D Visualization**: Three.js integration
- **File Upload**: Angular file upload components

### Project Structure
```
3d-store/
├── backend/                    # Flask API backend
│   ├── app/                   # Main application modules
│   │   ├── product/           # Product management (services + ready-made)
│   │   ├── order/             # Print job & order management
│   │   ├── inventory/         # Material & ready-product inventory
│   │   ├── users/             # User management
│   │   ├── seller/            # Seller management & commissions
│   │   ├── expense/           # Expense management
│   │   ├── financial/         # Financial operations
│   │   ├── payment/           # Payment processing
│   │   └── ...                # Other modules
│   ├── alembic/               # Database migrations
│   ├── requirements/          # Python dependencies
│   └── run.py                 # Application entry point
├── frontend/                  # Angular 20 frontend application
│   ├── src/                   # Source code
│   │   ├── app/               # Main application
│   │   │   ├── components/    # Reusable components
│   │   │   ├── pages/         # Page components
│   │   │   ├── services/      # API services
│   │   │   ├── models/        # TypeScript models
│   │   │   ├── guards/        # Route guards
│   │   │   └── shared/        # Shared modules
│   │   ├── assets/            # Static assets
│   │   └── environments/      # Environment configurations
│   ├── angular.json           # Angular configuration
│   ├── package.json           # Node.js dependencies
│   └── tsconfig.json          # TypeScript configuration
└── docs/                      # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+ and npm
- Angular CLI 20
- PostgreSQL/MySQL (or SQLite for development)
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/maz1987in/3D-Store.git
   cd 3d-store
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure the database**
   ```bash
   # Copy environment file
   cp env_development .env
   
   # Edit .env with your database settings
   # DATABASE_URL=postgresql://user:password@localhost/3dstore
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

6. **Start the applications**
   
   **Backend (Terminal 1):**
   ```bash
   cd backend
   python run.py
   ```
   
   **Frontend (Terminal 2):**
   ```bash
   cd frontend
   ng serve
   ```

- **Backend API**: `http://localhost:5000`
- **Frontend Application**: `http://localhost:4200`

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[📖 Complete Documentation](docs/README.md)** - Main documentation index
- **[🏗️ Backend Documentation](docs/backend/PROJECT_STRUCTURE.md)** - Backend architecture and modules
- **[🎨 Frontend Documentation](docs/frontend/README.md)** - Angular 20 frontend guide
- **[🔌 API Documentation](docs/api/README.md)** - Complete API reference
- **[🚀 Deployment Guide](docs/deployment/production.md)** - Production deployment

### Quick API Reference
- **Base URL**: `http://localhost:5000/3dstore/api/v1/`
- **Authentication**: JWT token in `x-access-tokens` header
- **Interactive Docs**: `http://localhost:5000/api/docs`

## 🎨 Frontend Features (Angular 20)

### Key Components
- **3D Model Upload**: Drag-and-drop file upload with preview
- **Print Job Dashboard**: Real-time status tracking and progress monitoring
- **Product Catalog**: Browse custom services and ready-made products
- **Shopping Cart**: Add products and services to cart
- **User Dashboard**: Profile management and order history
- **Seller Portal**: Commission tracking and performance analytics
- **Admin Panel**: Complete business management interface

### Angular Features
- **Responsive Design**: Mobile-first approach with Angular Material
- **3D Visualization**: Three.js integration for model preview
- **Real-time Updates**: WebSocket integration for live status updates
- **Multi-language Support**: i18n for Arabic and English
- **Progressive Web App**: PWA capabilities for mobile experience
- **State Management**: NgRx for complex state handling
- **Form Validation**: Reactive forms with custom validators
- **File Upload**: Advanced file handling with progress indicators

### Frontend Architecture
```
src/app/
├── components/           # Reusable UI components
│   ├── file-upload/     # 3D model upload component
│   ├── print-preview/   # 3D model preview
│   ├── order-card/      # Order display component
│   └── product-card/    # Product display component
├── pages/               # Main page components
│   ├── home/           # Landing page
│   ├── products/       # Product catalog
│   ├── orders/         # Order management
│   ├── dashboard/      # User dashboard
│   └── admin/          # Admin panel
├── services/           # API services
│   ├── api.service.ts  # Main API service
│   ├── auth.service.ts # Authentication service
│   └── upload.service.ts # File upload service
├── models/             # TypeScript interfaces
│   ├── product.model.ts
│   ├── order.model.ts
│   └── user.model.ts
└── shared/             # Shared modules and utilities
```

## 🏪 Business Models Supported

### 1. Custom 3D Printing Service
- Customers upload 3D models
- System calculates pricing and print time
- Print jobs are queued and processed
- Complete packaging and finishing workflow

### 2. Ready-Made Product Sales
- Pre-printed products in inventory
- Direct purchase and immediate fulfillment
- Stock management and reorder alerts
- Product performance analytics

### 3. Seller Marketplace
- Commission-based seller program
- Flexible settlement periods (weekly, monthly, quarterly)
- Performance tracking and analytics
- Multi-tier commission rates

## 💼 Key Business Features

### Cost Management
- **Complete Cost Tracking**: Print + packaging + finishing + labor + overhead
- **Dynamic Pricing**: Real-time cost calculation and pricing
- **Expense Management**: Track tools, printers, repairs, materials
- **Profit Margin Analysis**: Detailed profitability per product/service

### Inventory Management
- **Material Tracking**: Filament inventory across locations
- **Ready-Product Stock**: Pre-printed item inventory
- **Reorder Alerts**: Automated low-stock notifications
- **Multi-location Support**: Track inventory across facilities

### Financial Operations
- **Revenue Tracking**: Print service and product sales
- **Commission Management**: Seller payment processing
- **Expense Reporting**: Detailed cost analysis and reporting
- **Invoice Generation**: Automated invoice creation

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/3dstore

# JWT
JWT_SECRET_KEY=your_secret_key

# File Storage
UPLOAD_FOLDER=/path/to/uploads

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Payment Gateways
THAWANI_API_KEY=your_thawani_key
OMPAY_API_KEY=your_ompay_key
```

### Module Configuration
The system is modular and can be configured based on your business needs:

#### Core Modules (Essential)
- Product Management
- Order Management
- Inventory Management
- User Management
- Payment Processing
- Financial Operations

#### Optional Modules
- Seller Management
- Expense Tracking
- Rating System
- FAQ Management
- Labor Management

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production Considerations
- Use PostgreSQL or MySQL for production database
- Configure Redis for caching and session management
- Set up proper file storage (AWS S3, Google Cloud Storage)
- Configure SSL/TLS certificates
- Set up monitoring and logging

## 📊 Monitoring & Analytics

### Built-in Analytics
- Print job performance metrics
- Material usage tracking
- Revenue and profit analysis
- Seller performance monitoring
- Customer behavior analytics

### Logging
- Application logs
- Print job execution logs
- Printer status logs
- Error tracking and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository


## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Core 3D printing service management
- ✅ Product and inventory management
- ✅ Basic financial operations
- 🔄 Angular 20 frontend development
- 🔄 3D model upload and preview

### Phase 2 (Next)
- 📋 Complete Angular frontend implementation
- 📋 Advanced analytics and reporting
- 📋 Mobile responsive design
- 📋 Advanced packaging options
- 📋 Real-time print monitoring

### Phase 3 (Future)
- 📋 AI-powered print optimization
- 📋 Advanced seller tools
- 📋 Integration with 3D modeling software
- 📋 Progressive Web App (PWA) features
- 📋 Advanced 3D visualization tools

---

**Built with ❤️ for the 3D printing community**