import { Injectable } from '@angular/core';
import { Observable, Subject, BehaviorSubject } from 'rxjs';
import { io, Socket } from 'socket.io-client';
import { environment } from '../../environments/environment';

export interface WebSocketEvent {
  type: string;
  data: any;
  timestamp: Date;
}

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: Socket | null = null;
  private wsUrl = environment.wsUrl;
  private reconnectionDelay = environment.wsReconnectionDelay;
  private maxReconnectionAttempts = environment.wsMaxReconnectionAttempts;
  private reconnectionAttempts = 0;

  private connectionStatusSubject = new BehaviorSubject<boolean>(false);
  public connectionStatus$ = this.connectionStatusSubject.asObservable();

  private eventsSubject = new Subject<WebSocketEvent>();
  public events$ = this.eventsSubject.asObservable();

  constructor() {
    if (environment.enableWebSocket) {
      this.connect();
    }
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.socket && this.socket.connected) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      this.socket = io(this.wsUrl, {
        transports: ['websocket'],
        autoConnect: true,
        reconnection: true,
        reconnectionDelay: this.reconnectionDelay,
        reconnectionAttempts: this.maxReconnectionAttempts
      });

      this.setupEventListeners();
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connectionStatusSubject.next(false);
    }
  }

  /**
   * Subscribe to specific event type
   */
  on(eventType: string): Observable<any> {
    const subject = new Subject<any>();

    if (this.socket) {
      this.socket.on(eventType, (data: any) => {
        subject.next(data);
        this.eventsSubject.next({
          type: eventType,
          data,
          timestamp: new Date()
        });
      });
    }

    return subject.asObservable();
  }

  /**
   * Emit event to server
   */
  emit(eventType: string, data?: any): void {
    if (this.socket && this.socket.connected) {
      this.socket.emit(eventType, data);
    } else {
      console.warn('WebSocket not connected. Cannot emit event:', eventType);
    }
  }

  /**
   * Subscribe to print job progress updates
   */
  subscribeToPrintJobUpdates(jobId: string): Observable<any> {
    return this.on(`print_job_${jobId}`);
  }

  /**
   * Subscribe to order status updates
   */
  subscribeToOrderUpdates(orderId: string): Observable<any> {
    return this.on(`order_${orderId}`);
  }

  /**
   * Subscribe to general notifications
   */
  subscribeToNotifications(): Observable<any> {
    return this.on('notification');
  }

  /**
   * Setup event listeners
   */
  private setupEventListeners(): void {
    if (!this.socket) return;

    // Connection established
    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.connectionStatusSubject.next(true);
      this.reconnectionAttempts = 0;
    });

    // Connection error
    this.socket.on('connect_error', (error: any) => {
      console.error('WebSocket connection error:', error);
      this.connectionStatusSubject.next(false);
    });

    // Disconnected
    this.socket.on('disconnect', (reason: any) => {
      console.log('WebSocket disconnected:', reason);
      this.connectionStatusSubject.next(false);

      // Attempt reconnection for certain reasons
      if (reason === 'io server disconnect') {
        // Server disconnected, manual reconnection needed
        this.attemptReconnection();
      }
    });

    // Reconnection attempt
    this.socket.on('reconnect_attempt', () => {
      this.reconnectionAttempts++;
      console.log(`WebSocket reconnection attempt ${this.reconnectionAttempts}`);
    });

    // Reconnected
    this.socket.on('reconnect', () => {
      console.log('WebSocket reconnected');
      this.connectionStatusSubject.next(true);
      this.reconnectionAttempts = 0;
    });

    // Reconnection failed
    this.socket.on('reconnect_failed', () => {
      console.error('WebSocket reconnection failed');
      this.connectionStatusSubject.next(false);
    });

    // Print job progress updates
    this.socket.on('print_progress', (data: any) => {
      this.eventsSubject.next({
        type: 'print_progress',
        data,
        timestamp: new Date()
      });
    });

    // Print job completed
    this.socket.on('print_completed', (data: any) => {
      this.eventsSubject.next({
        type: 'print_completed',
        data,
        timestamp: new Date()
      });
    });

    // Print job failed
    this.socket.on('print_failed', (data: any) => {
      this.eventsSubject.next({
        type: 'print_failed',
        data,
        timestamp: new Date()
      });
    });

    // Order status updates
    this.socket.on('order_status', (data: any) => {
      this.eventsSubject.next({
        type: 'order_status',
        data,
        timestamp: new Date()
      });
    });

    // General notifications
    this.socket.on('notification', (data: any) => {
      this.eventsSubject.next({
        type: 'notification',
        data,
        timestamp: new Date()
      });
    });
  }

  /**
   * Attempt manual reconnection
   */
  private attemptReconnection(): void {
    if (this.reconnectionAttempts < this.maxReconnectionAttempts) {
      setTimeout(() => {
        console.log('Attempting manual reconnection...');
        this.connect();
      }, this.reconnectionDelay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.connectionStatusSubject.value;
  }

  /**
   * Get connection status
   */
  getConnectionStatus(): Observable<boolean> {
    return this.connectionStatus$;
  }
}

