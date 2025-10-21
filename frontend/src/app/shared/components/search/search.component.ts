import { Component, Input, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormControl } from '@angular/forms';
import { MaterialModule } from '../../material.module';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';
import { SearchFilter } from '../../../models/common.model';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, MaterialModule],
  template: `
    <div class="search-container">
      <mat-form-field class="search-field" appearance="outline">
        <mat-label>{{ placeholder }}</mat-label>
        <input matInput [formControl]="searchControl" type="text">
        <mat-icon matPrefix>search</mat-icon>
        @if (searchControl.value) {
          <button mat-icon-button matSuffix (click)="clearSearch()">
            <mat-icon>close</mat-icon>
          </button>
        }
      </mat-form-field>
      
      @if (showFilters && filters.length > 0) {
        <button mat-icon-button (click)="toggleFilters()">
          <mat-icon [matBadge]="activeFiltersCount" [matBadgeHidden]="activeFiltersCount === 0">
            filter_list
          </mat-icon>
        </button>
      }
    </div>
    
    @if (showFilters && filtersExpanded) {
      <div class="filters-panel">
        @for (filter of filters; track filter.field) {
          <mat-form-field appearance="outline">
            <mat-label>{{ filter.label }}</mat-label>
            
            @if (filter.type === 'text') {
              <input matInput [(ngModel)]="filter.value" (ngModelChange)="onFilterChange()">
            } @else if (filter.type === 'number') {
              <input matInput type="number" [(ngModel)]="filter.value" (ngModelChange)="onFilterChange()">
            } @else if (filter.type === 'select' && filter.options) {
              <mat-select [(ngModel)]="filter.value" (ngModelChange)="onFilterChange()">
                @for (option of filter.options; track option.value) {
                  <mat-option [value]="option.value" [disabled]="option.disabled">
                    {{ option.label }}
                  </mat-option>
                }
              </mat-select>
            } @else if (filter.type === 'checkbox') {
              <mat-checkbox [(ngModel)]="filter.value" (ngModelChange)="onFilterChange()">
                {{ filter.label }}
              </mat-checkbox>
            }
          </mat-form-field>
        }
        
        <div class="filter-actions">
          <button mat-button (click)="clearFilters()">Clear Filters</button>
          <button mat-raised-button color="primary" (click)="applyFilters()">Apply</button>
        </div>
      </div>
    }
  `,
  styles: [`
    .search-container {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    
    .search-field {
      flex: 1;
      min-width: 200px;
    }
    
    .filters-panel {
      margin-top: 1rem;
      padding: 1rem;
      background: #f5f5f5;
      border-radius: 4px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
    }
    
    .filter-actions {
      grid-column: 1 / -1;
      display: flex;
      justify-content: flex-end;
      gap: 0.5rem;
      margin-top: 0.5rem;
    }
  `]
})
export class SearchComponent implements OnInit, OnDestroy {
  @Input() placeholder: string = 'Search...';
  @Input() debounceTime: number = 300;
  @Input() showFilters: boolean = false;
  @Input() filters: SearchFilter[] = [];
  
  @Output() search = new EventEmitter<string>();
  @Output() filterChange = new EventEmitter<any>();
  
  searchControl = new FormControl('');
  filtersExpanded = false;
  private destroy$ = new Subject<void>();
  
  ngOnInit(): void {
    this.searchControl.valueChanges
      .pipe(
        debounceTime(this.debounceTime),
        distinctUntilChanged(),
        takeUntil(this.destroy$)
      )
      .subscribe(value => {
        this.search.emit(value || '');
      });
  }
  
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
  
  clearSearch(): void {
    this.searchControl.setValue('');
  }
  
  toggleFilters(): void {
    this.filtersExpanded = !this.filtersExpanded;
  }
  
  onFilterChange(): void {
    const filterValues: any = {};
    this.filters.forEach(filter => {
      if (filter.value !== null && filter.value !== undefined && filter.value !== '') {
        filterValues[filter.field] = filter.value;
      }
    });
    this.filterChange.emit(filterValues);
  }
  
  clearFilters(): void {
    this.filters.forEach(filter => {
      filter.value = filter.type === 'checkbox' ? false : undefined;
    });
    this.onFilterChange();
  }
  
  applyFilters(): void {
    this.onFilterChange();
    this.filtersExpanded = false;
  }
  
  get activeFiltersCount(): number {
    return this.filters.filter(f => f.value !== null && f.value !== undefined && f.value !== '').length;
  }
}

