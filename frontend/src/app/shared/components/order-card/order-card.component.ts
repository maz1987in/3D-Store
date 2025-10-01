import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-order-card',
  standalone: true,
  imports: [],
  template: `
    <p>
      order-card works!
    </p>
  `,
  styles: ``,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class OrderCardComponent {

}
