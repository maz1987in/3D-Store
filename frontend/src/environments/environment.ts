// Development environment configuration (default)
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
  enableAppleAuth: true,
  enableTwitterAuth: true,
  enablePWA: true,
  enableOfflineMode: true,
  enableWebSocket: true,
  
  // Analytics
  googleAnalyticsId: 'UA-XXXXXXXXX-X',
  enableAnalytics: true,
  
  // Monitoring
  sentryDsn: 'https://xxxxx@sentry.io/xxxxx',
  enableSentry: true,
  
  // Cache Configuration
  cacheTimeout: 600000, // 10 minutes in milliseconds
  enableCache: true,
  
  // UI Configuration
  defaultLanguage: 'en',
  supportedLanguages: ['en', 'ar'],
  itemsPerPage: 20,
  defaultPageSize: 20,
  pageSizeOptions: [10, 20, 50, 100],
  
  // Payment Gateways
  thawaniPublicKey: 'HGvTMLDssJghr9tlN9gr4DVYt0qyBy',
  ompayPublicKey: 'your_ompay_public_key',
  
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
