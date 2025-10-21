import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'filter',
  standalone: true
})
export class FilterPipe implements PipeTransform {
  transform<T>(items: T[], searchText: string, key?: keyof T): T[] {
    if (!items || !searchText) {
      return items;
    }

    searchText = searchText.toLowerCase();

    return items.filter(item => {
      if (key) {
        const value = item[key];
        return String(value).toLowerCase().includes(searchText);
      } else {
        return JSON.stringify(item).toLowerCase().includes(searchText);
      }
    });
  }
}

