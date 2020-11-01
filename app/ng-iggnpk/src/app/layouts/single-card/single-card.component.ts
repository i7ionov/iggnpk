import { Component, NgModule} from '@angular/core';
import { CommonModule } from '@angular/common';
import { DxScrollViewModule }  from 'devextreme-angular/ui/scroll-view';
import {RouterModule} from "@angular/router";

@Component({
  selector: 'app-single-card',
  templateUrl: './single-card.component.html',
  styleUrls: ['./single-card.component.scss']
})
export class SingleCardComponent {
  constructor() { }
}

@NgModule({
  imports: [ CommonModule, DxScrollViewModule, RouterModule ],
  exports: [ SingleCardComponent ],
  declarations: [ SingleCardComponent ]
})
export class SingleCardModule { }
