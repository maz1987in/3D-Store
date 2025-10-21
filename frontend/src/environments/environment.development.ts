// Development environment configuration
export const environment = {
  production: false,
  
  // API Configuration
  apiUrl: 'http://localhost:5001/store3d/api/v1',
  wsUrl: 'ws://localhost:5001/ws',
  uploadUrl: 'http://localhost:5001/store3d/api/v1/upload',
  
  // File Upload Configuration
  maxFileSize: 104857600, // 100MB in bytes
  supportedFormats: ['.stl', '.obj', '.3mf'],
  
  // Storage Keys
  tokenKey: 'auth_token',
  refreshTokenKey: 'refresh_token',
  userKey: 'current_user',
  cartKey: 'shopping_cart',
  
  // Feature Flags
  enableGoogleAuth: true,
  enableAppleAuth: false,
  enableTwitterAuth: false,
  enablePWA: false,
  enableOfflineMode: false,
  enableWebSocket: true,
  
  // Analytics
  googleAnalyticsId: '',
  enableAnalytics: false,
  
  // Monitoring
  sentryDsn: '',
  enableSentry: false,
  
  // Cache Configuration
  cacheTimeout: 300000, // 5 minutes in milliseconds
  enableCache: true,
  
  // UI Configuration
  defaultLanguage: 'en',
  supportedLanguages: ['en', 'ar'],
  itemsPerPage: 20,
  defaultPageSize: 20,
  pageSizeOptions: [10, 20, 50, 100],
  
  // Payment Gateways
  thawaniPublicKey: '',
  ompayPublicKey: '',
  
  // WebSocket Configuration
  wsReconnectionDelay: 5000,
  wsMaxReconnectionAttempts: 5,
  
  // Image Configuration
  imageQuality: 0.8,
  thumbnailSize: 200,
  maxImageSize: 10485760, // 10MB
  
  // Debounce Times
  searchDebounce: 300,
  resizeDebounce: 250,
  
  // Timeouts
  requestTimeout: 30000, // 30 seconds
  longRequestTimeout: 120000, // 2 minutes for file uploads
};
