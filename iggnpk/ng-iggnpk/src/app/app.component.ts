import {Component, HostBinding, OnInit} from '@angular/core';
import {AuthService, ScreenService, AppInfoService} from './shared/services';
import ruMessages from 'devextreme/localization/messages/ru.json';
import { locale, loadMessages } from "devextreme/localization";


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit{
  @HostBinding('class') get getClass() {
    return Object.keys(this.screen.sizes).filter(cl => this.screen.sizes[cl]).join(' ');
  }

  constructor(private authService: AuthService, private screen: ScreenService, public appInfo: AppInfoService) {

        loadMessages(ruMessages);
        locale(navigator.language);
  }
  ngOnInit() {
     this.authService.getUserInfo();
  }

  isAutorized() {
      return !!localStorage.getItem('token');
  }
}
