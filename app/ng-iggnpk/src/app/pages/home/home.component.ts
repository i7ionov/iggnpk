import {Component, NgModule, OnInit} from '@angular/core';
import {AuthService} from "../../shared/services";
import {DxTreeViewModule} from "devextreme-angular";
import {CommonModule} from "@angular/common";
import {SideNavigationMenuComponent} from "../../shared/components";


@Component({
  templateUrl: 'home.component.html',
  styleUrls: [ './home.component.scss' ]
})

export class HomeComponent implements OnInit{
  constructor(private auth: AuthService) {}

  click() {

  }

  ngOnInit(): void {

  }
}
@NgModule({
  imports: [ DxTreeViewModule,CommonModule ],
  declarations: [ HomeComponent ],
  exports: [ HomeComponent ]
})
export class HomeComponentModule { }
