import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../material.module';
import { PageEvent } from '@angular/material/paginator';

@Component({
  selector: 'app-pagination',
  standalone: true,
  imports: [CommonModule, MaterialModule],
  template: `
    <mat-paginator
      [length]="totalItems"
      [pageSize]="pageSize"
      [pageIndex]="currentPage - 1"
      [pageSizeOptions]="pageSizeOptions"
      (page)="onPageChange($event)"
      showFirstLastButtons>
    </mat-paginator>
  `,
  styles: [`
    :host {
      display: block;
      margin-top: 1rem;
    }
  `]
})
export class PaginationComponent implements OnInit {
  @Input() totalItems: number = 0;
  @Input() currentPage: number = 1;
  @Input() pageSize: number = 10;
  @Input() pageSizeOptions: number[] = [10, 20, 50, 100];
  
  @Output() pageChange = new EventEmitter<number>();
  @Output() pageSizeChange = new EventEmitter<number>();
  
  ngOnInit(): void {
    // Ensure currentPage is at least 1
    if (this.currentPage < 1) {
      this.currentPage = 1;
    }
  }
  
  onPageChange(event: PageEvent): void {
    const newPage = event.pageIndex + 1; // Convert from 0-based to 1-based
    const newPageSize = event.pageSize;
    
    if (newPageSize !== this.pageSize) {
      this.pageSizeChange.emit(newPageSize);
    }
    
    if (newPage !== this.currentPage) {
      this.pageChange.emit(newPage);
    }
  }
}

