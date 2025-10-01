import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [],
  template: `
    <p>
      file-upload works!
    </p>
  `,
  styles: ``,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FileUploadComponent {

}
