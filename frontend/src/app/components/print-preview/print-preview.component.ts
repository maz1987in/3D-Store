import { Component, Input, Output, EventEmitter, ElementRef, ViewChild, OnInit, OnDestroy, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../shared/material.module';
import { ThreeService } from '../../services/three/three.service';
import { ModelLoaderService } from '../../services/three/model-loader.service';
import { LoadingComponent } from '../../shared/components/loading/loading.component';
import { ErrorComponent } from '../../shared/components/error/error.component';

@Component({
  selector: 'app-print-preview',
  standalone: true,
  imports: [CommonModule, MaterialModule, LoadingComponent, ErrorComponent],
  template: `
    <div class="print-preview-container">
      <!-- Loading State -->
      @if (loading) {
        <div class="preview-loading">
          <app-loading type="spinner" message="Loading 3D model..."></app-loading>
        </div>
      }

      <!-- Error State -->
      @if (error) {
        <div class="preview-error">
          <app-error [message]="error" (retry)="loadModel()"></app-error>
        </div>
      }

      <!-- 3D Viewer -->
      <div 
        #modelContainer 
        class="model-container"
        [class.hidden]="loading || error">
      </div>

      <!-- Controls -->
      @if (showControls && !loading && !error) {
        <div class="viewer-controls">
          <div class="control-group">
            <button 
              mat-icon-button 
              (click)="resetCamera()"
              matTooltip="Reset View">
              <mat-icon>3d_rotation</mat-icon>
            </button>
            
            <button 
              mat-icon-button 
              (click)="toggleWireframe()"
              matTooltip="Toggle Wireframe"
              [class.active]="wireframeMode">
              <mat-icon>grid_on</mat-icon>
            </button>
            
            <button 
              mat-icon-button 
              (click)="takeScreenshot()"
              matTooltip="Screenshot">
              <mat-icon>camera_alt</mat-icon>
            </button>
            
            <button 
              mat-icon-button 
              (click)="toggleFullscreen()"
              matTooltip="Fullscreen">
              <mat-icon>{{ isFullscreen ? 'fullscreen_exit' : 'fullscreen' }}</mat-icon>
            </button>
          </div>

          <!-- Model Info -->
          @if (modelMetadata) {
            <div class="model-info">
              <mat-chip-set>
                <mat-chip>
                  <mat-icon>grid_4x4</mat-icon>
                  {{ modelMetadata.vertices.toLocaleString() }} vertices
                </mat-chip>
                <mat-chip>
                  <mat-icon>change_history</mat-icon>
                  {{ modelMetadata.triangles.toLocaleString() }} triangles
                </mat-chip>
                @if (modelMetadata.dimensions) {
                  <mat-chip>
                    <mat-icon>straighten</mat-icon>
                    {{ modelMetadata.dimensions.width.toFixed(1) }} × 
                    {{ modelMetadata.dimensions.height.toFixed(1) }} × 
                    {{ modelMetadata.dimensions.depth.toFixed(1) }} mm
                  </mat-chip>
                }
              </mat-chip-set>
            </div>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .print-preview-container {
      position: relative;
      width: 100%;
      height: 100%;
      min-height: 400px;
      background: #f5f5f5;
      border-radius: 8px;
      overflow: hidden;
    }

    .preview-loading,
    .preview-error {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f5f5f5;
      z-index: 10;
    }

    .model-container {
      width: 100%;
      height: 100%;
      min-height: 400px;
      
      &.hidden {
        display: none;
      }
    }

    .viewer-controls {
      position: absolute;
      bottom: 1rem;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(255, 255, 255, 0.95);
      border-radius: 8px;
      padding: 0.5rem;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      z-index: 5;
      
      .control-group {
        display: flex;
        gap: 0.25rem;
        margin-bottom: 0.5rem;
        
        button {
          &.active {
            background: #e3f2fd;
            color: #3f51b5;
          }
        }
      }
      
      .model-info {
        padding: 0.5rem;
        border-top: 1px solid #e0e0e0;
        
        mat-chip-set {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        
        mat-chip {
          font-size: 0.75rem;
          height: 28px;
          
          mat-icon {
            font-size: 14px;
            width: 14px;
            height: 14px;
            margin-right: 0.25rem;
          }
        }
      }
    }
  `]
})
export class PrintPreviewComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('modelContainer', { static: false }) containerRef!: ElementRef;
  
  @Input() modelUrl: string = '';
  @Input() modelType: 'stl' | 'obj' | '3mf' = 'stl';
  @Input() showControls: boolean = true;
  @Input() backgroundColor: string = '#f0f0f0';
  
  @Output() modelLoaded = new EventEmitter<void>();
  @Output() loadError = new EventEmitter<string>();

  loading = false;
  error: string | null = null;
  wireframeMode = false;
  isFullscreen = false;
  modelMetadata: any = null;

  constructor(
    private threeService: ThreeService,
    private modelLoader: ModelLoaderService
  ) {}

  ngOnInit(): void {
    if (this.modelUrl) {
      // Will load after view init
    }
  }

  ngAfterViewInit(): void {
    if (this.containerRef) {
      // Initialize Three.js scene
      this.threeService.initScene(
        this.containerRef.nativeElement,
        this.backgroundColor
      );

      // Load model if URL provided
      if (this.modelUrl) {
        this.loadModel();
      }

      // Handle window resize
      window.addEventListener('resize', this.onWindowResize.bind(this));
    }
  }

  ngOnDestroy(): void {
    window.removeEventListener('resize', this.onWindowResize.bind(this));
    this.threeService.dispose();
  }

  loadModel(): void {
    if (!this.modelUrl) return;

    this.loading = true;
    this.error = null;

    this.modelLoader.loadModel(this.modelUrl, this.modelType).subscribe({
      next: (model) => {
        this.threeService.addObject(model);
        this.modelMetadata = this.modelLoader.getModelMetadata(model);
        this.loading = false;
        this.modelLoaded.emit();
      },
      error: (error) => {
        this.error = error.message;
        this.loading = false;
        this.loadError.emit(error.message);
      }
    });
  }

  resetCamera(): void {
    this.threeService.resetCamera();
  }

  toggleWireframe(): void {
    this.wireframeMode = !this.wireframeMode;
    this.threeService.toggleWireframe(this.wireframeMode);
  }

  takeScreenshot(): void {
    const dataUrl = this.threeService.takeScreenshot();
    
    if (dataUrl) {
      // Create download link
      const link = document.createElement('a');
      link.href = dataUrl;
      link.download = `model_screenshot_${Date.now()}.png`;
      link.click();
    }
  }

  toggleFullscreen(): void {
    if (!this.containerRef) return;

    if (!this.isFullscreen) {
      const element = this.containerRef.nativeElement;
      if (element.requestFullscreen) {
        element.requestFullscreen();
      }
      this.isFullscreen = true;
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
      this.isFullscreen = false;
    }
  }

  private onWindowResize(): void {
    if (this.containerRef) {
      const container = this.containerRef.nativeElement;
      this.threeService.onResize(container.clientWidth, container.clientHeight);
    }
  }
}

