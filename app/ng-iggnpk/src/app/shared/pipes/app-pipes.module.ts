import {NgModule} from "@angular/core";
import {FileSizePipe} from "./filesize.pipe";
import {BooleanPipe} from "./boolean.pipe";

@NgModule({
  imports: [
    // dep modules
  ],
  declarations: [
    FileSizePipe,
    BooleanPipe
  ],
  exports: [
    FileSizePipe,
    BooleanPipe
  ]
})
export class ApplicationPipesModule {}
