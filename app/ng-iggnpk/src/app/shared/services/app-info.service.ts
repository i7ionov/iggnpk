import { Injectable } from '@angular/core';

@Injectable()
export class AppInfoService {
  constructor() {}

  public get title() {
    return 'Электронная форма предоставления информации Инспекции государственного жилищного надзора Пермского края';
  }
}
