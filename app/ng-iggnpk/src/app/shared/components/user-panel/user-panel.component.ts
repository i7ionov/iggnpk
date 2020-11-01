import {Component, NgModule, Input, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';

import {DxListModule} from 'devextreme-angular/ui/list';
import {DxContextMenuModule} from 'devextreme-angular/ui/context-menu';
import {AuthService} from "../../services";

@Component({
  selector: 'app-user-panel',
  templateUrl: 'user-panel.component.html',
  styleUrls: ['./user-panel.component.scss']
})

export class UserPanelComponent implements OnInit {
  @Input()
  menuItems: any;

  @Input()
  menuMode: string;

  constructor(public auth: AuthService) {
  }

  ngOnInit(): void {

  }
}

@NgModule({
  imports: [
    DxListModule,
    DxContextMenuModule,
    CommonModule
  ],
  declarations: [UserPanelComponent],
  exports: [UserPanelComponent]
})
export class UserPanelModule {
}
