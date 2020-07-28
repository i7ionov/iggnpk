import { Injectable } from '@angular/core';

@Injectable()
export class AppInfoService {
  constructor() {}

  public get title() {
    return 'Система обработки поступающей информации Инспекции государственного жилищного надзора Пермского края';
  }
}
