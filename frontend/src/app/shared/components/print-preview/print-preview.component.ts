import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-print-preview',
  standalone: true,
  imports: [],
  template: `
    <p>
      print-preview works!
    </p>
  `,
  styles: ``,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class PrintPreviewComponent {

}
