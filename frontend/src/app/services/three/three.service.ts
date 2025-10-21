import { Injectable } from '@angular/core';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

@Injectable({
  providedIn: 'root'
})
export class ThreeService {
  private scene: THREE.Scene | null = null;
  private camera: THREE.PerspectiveCamera | null = null;
  private renderer: THREE.WebGLRenderer | null = null;
  private controls: OrbitControls | null = null;
  private animationId: number | null = null;

  constructor() {}

  /**
   * Initialize Three.js scene
   */
  initScene(container: HTMLElement, backgroundColor: string = '#f0f0f0'): void {
    // Create scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(backgroundColor);

    // Create camera
    const aspect = container.clientWidth / container.clientHeight;
    this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
    this.camera.position.set(0, 0, 100);

    // Create renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(container.clientWidth, container.clientHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(this.renderer.domElement);

    // Add lights
    this.setupLights();

    // Add controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.screenSpacePanning = false;
    this.controls.minDistance = 10;
    this.controls.maxDistance = 500;

    // Start animation loop
    this.animate();
  }

  /**
   * Setup scene lighting
   */
  private setupLights(): void {
    if (!this.scene) return;

    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    this.scene.add(ambientLight);

    // Directional light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    this.scene.add(directionalLight);

    // Another directional light from opposite side
    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight2.position.set(-1, -1, -1);
    this.scene.add(directionalLight2);

    // Point light for highlights
    const pointLight = new THREE.PointLight(0xffffff, 0.5);
    pointLight.position.set(0, 50, 50);
    this.scene.add(pointLight);
  }

  /**
   * Add object to scene
   */
  addObject(object: THREE.Object3D): void {
    if (this.scene) {
      this.scene.add(object);
      this.centerCamera(object);
    }
  }

  /**
   * Remove object from scene
   */
  removeObject(object: THREE.Object3D): void {
    if (this.scene) {
      this.scene.remove(object);
    }
  }

  /**
   * Clear all objects from scene
   */
  clearScene(): void {
    if (!this.scene) return;

    while (this.scene.children.length > 0) {
      const object = this.scene.children[0];
      if (object.type !== 'AmbientLight' && object.type !== 'DirectionalLight' && object.type !== 'PointLight') {
        this.scene.remove(object);
      } else {
        break;
      }
    }
  }

  /**
   * Center camera on object
   */
  centerCamera(object: THREE.Object3D): void {
    if (!this.camera || !this.controls) return;

    const box = new THREE.Box3().setFromObject(object);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());

    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = this.camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));

    cameraZ *= 1.5; // Add some padding

    this.camera.position.set(center.x, center.y, center.z + cameraZ);
    this.camera.lookAt(center);
    this.controls.target.copy(center);
    this.controls.update();
  }

  /**
   * Reset camera to default position
   */
  resetCamera(): void {
    if (!this.camera || !this.controls) return;

    this.camera.position.set(0, 0, 100);
    this.camera.lookAt(0, 0, 0);
    this.controls.target.set(0, 0, 0);
    this.controls.update();
  }

  /**
   * Animation loop
   */
  private animate = (): void => {
    this.animationId = requestAnimationFrame(this.animate);

    if (this.controls) {
      this.controls.update();
    }

    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  };

  /**
   * Resize renderer
   */
  onResize(width: number, height: number): void {
    if (this.camera && this.renderer) {
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height);
    }
  }

  /**
   * Take screenshot
   */
  takeScreenshot(): string {
    if (!this.renderer) return '';
    return this.renderer.domElement.toDataURL('image/png');
  }

  /**
   * Toggle wireframe mode
   */
  toggleWireframe(enable: boolean): void {
    if (!this.scene) return;

    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        if (object.material instanceof THREE.Material) {
          (object.material as any).wireframe = enable;
        }
      }
    });
  }

  /**
   * Set background color
   */
  setBackgroundColor(color: string): void {
    if (this.scene) {
      this.scene.background = new THREE.Color(color);
    }
  }

  /**
   * Get scene
   */
  getScene(): THREE.Scene | null {
    return this.scene;
  }

  /**
   * Get camera
   */
  getCamera(): THREE.PerspectiveCamera | null {
    return this.camera;
  }

  /**
   * Get renderer
   */
  getRenderer(): THREE.WebGLRenderer | null {
    return this.renderer;
  }

  /**
   * Dispose and cleanup
   */
  dispose(): void {
    if (this.animationId !== null) {
      cancelAnimationFrame(this.animationId);
    }

    if (this.controls) {
      this.controls.dispose();
    }

    if (this.renderer) {
      this.renderer.dispose();
      if (this.renderer.domElement.parentNode) {
        this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
      }
    }

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
  }
}

