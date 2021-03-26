import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'boolean'
})
export class BooleanPipe implements PipeTransform {
  transform(val?: boolean) {
    if (val){
      return "Да"
    }
    else {
      return "Нет"
    }
  }
}
