import {NgModule} from "@angular/core";
import {FileSizePipe} from "./filesize.pipe";

@NgModule({
  imports: [
    // dep modules
  ],
  declarations: [
    FileSizePipe
  ],
  exports: [
    FileSizePipe
  ]
})
export class ApplicationPipesModule {}
