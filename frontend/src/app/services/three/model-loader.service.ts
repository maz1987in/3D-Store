import { Injectable } from '@angular/core';
import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { Observable, Subject } from 'rxjs';

export interface LoadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

@Injectable({
  providedIn: 'root'
})
export class ModelLoaderService {
  private stlLoader: STLLoader;
  private objLoader: OBJLoader;

  constructor() {
    this.stlLoader = new STLLoader();
    this.objLoader = new OBJLoader();
  }

  /**
   * Load STL file
   */
  loadSTL(url: string): Observable<THREE.Mesh> {
    const subject = new Subject<THREE.Mesh>();

    this.stlLoader.load(
      url,
      (geometry) => {
        const material = new THREE.MeshPhongMaterial({
          color: 0x00a8ff,
          specular: 0x111111,
          shininess: 200
        });

        const mesh = new THREE.Mesh(geometry, material);
        
        // Center the geometry
        geometry.computeBoundingBox();
        const center = new THREE.Vector3();
        geometry.boundingBox!.getCenter(center);
        geometry.translate(-center.x, -center.y, -center.z);

        // Compute normals for proper lighting
        geometry.computeVertexNormals();

        subject.next(mesh);
        subject.complete();
      },
      (progress) => {
        // Progress callback if needed
      },
      (error: any) => {
        subject.error(new Error(`Failed to load STL file: ${error?.message || 'Unknown error'}`));
      }
    );

    return subject.asObservable();
  }

  /**
   * Load OBJ file
   */
  loadOBJ(url: string): Observable<THREE.Group> {
    const subject = new Subject<THREE.Group>();

    this.objLoader.load(
      url,
      (object) => {
        // Apply material to all meshes
        object.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            child.material = new THREE.MeshPhongMaterial({
              color: 0x00a8ff,
              specular: 0x111111,
              shininess: 200
            });
          }
        });

        // Center the object
        const box = new THREE.Box3().setFromObject(object);
        const center = box.getCenter(new THREE.Vector3());
        object.position.sub(center);

        subject.next(object);
        subject.complete();
      },
      (progress) => {
        // Progress callback if needed
      },
      (error: any) => {
        subject.error(new Error(`Failed to load OBJ file: ${error?.message || 'Unknown error'}`));
      }
    );

    return subject.asObservable();
  }

  /**
   * Load 3D model file based on type
   */
  loadModel(url: string, type: 'stl' | 'obj' | '3mf'): Observable<THREE.Object3D> {
    switch (type) {
      case 'stl':
        return this.loadSTL(url);
      case 'obj':
        return this.loadOBJ(url);
      case '3mf':
        // 3MF loader would be implemented here
        return new Observable(observer => {
          observer.error(new Error('3MF format not yet supported'));
        });
      default:
        return new Observable(observer => {
          observer.error(new Error(`Unsupported file type: ${type}`));
        });
    }
  }

  /**
   * Load model from File object
   */
  loadModelFromFile(file: File): Observable<THREE.Object3D> {
    const subject = new Subject<THREE.Object3D>();

    const reader = new FileReader();
    reader.onload = (event) => {
      const arrayBuffer = event.target?.result as ArrayBuffer;
      
      if (!arrayBuffer) {
        subject.error(new Error('Failed to read file'));
        return;
      }

      const extension = file.name.split('.').pop()?.toLowerCase();
      
      try {
        if (extension === 'stl') {
          const geometry = this.stlLoader.parse(arrayBuffer);
          const material = new THREE.MeshPhongMaterial({
            color: 0x00a8ff,
            specular: 0x111111,
            shininess: 200
          });
          
          const mesh = new THREE.Mesh(geometry, material);
          
          // Center the geometry
          geometry.computeBoundingBox();
          const center = new THREE.Vector3();
          geometry.boundingBox!.getCenter(center);
          geometry.translate(-center.x, -center.y, -center.z);
          
          // Compute normals
          geometry.computeVertexNormals();
          
          subject.next(mesh);
          subject.complete();
        } else if (extension === 'obj') {
          const text = new TextDecoder().decode(arrayBuffer);
          const object = this.objLoader.parse(text);
          
          // Apply material
          object.traverse((child) => {
            if (child instanceof THREE.Mesh) {
              child.material = new THREE.MeshPhongMaterial({
                color: 0x00a8ff,
                specular: 0x111111,
                shininess: 200
              });
            }
          });
          
          // Center the object
          const box = new THREE.Box3().setFromObject(object);
          const center = box.getCenter(new THREE.Vector3());
          object.position.sub(center);
          
          subject.next(object);
          subject.complete();
        } else {
          subject.error(new Error(`Unsupported file extension: ${extension}`));
        }
      } catch (error: any) {
        subject.error(new Error(`Failed to parse file: ${error.message}`));
      }
    };

    reader.onerror = () => {
      subject.error(new Error('File read error'));
    };

    reader.readAsArrayBuffer(file);

    return subject.asObservable();
  }

  /**
   * Get model metadata
   */
  getModelMetadata(object: THREE.Object3D): any {
    const box = new THREE.Box3().setFromObject(object);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());

    let vertices = 0;
    let triangles = 0;

    object.traverse((child) => {
      if (child instanceof THREE.Mesh && child.geometry) {
        const geometry = child.geometry;
        if (geometry.attributes.position) {
          vertices += geometry.attributes.position.count;
        }
        if (geometry.index) {
          triangles += geometry.index.count / 3;
        }
      }
    });

    return {
      vertices,
      triangles,
      dimensions: {
        width: size.x,
        height: size.y,
        depth: size.z,
        unit: 'mm'
      },
      center: {
        x: center.x,
        y: center.y,
        z: center.z
      },
      boundingBox: {
        min: { x: box.min.x, y: box.min.y, z: box.min.z },
        max: { x: box.max.x, y: box.max.y, z: box.max.z }
      }
    };
  }
}

