import {AfterContentInit, AfterViewInit, Component, NgModule, OnInit, ViewChild} from '@angular/core';
import {DxCheckBoxModule} from "devextreme-angular/ui/check-box";
import {DxTextBoxModule} from "devextreme-angular/ui/text-box";
import {Router, RouterModule, Routes} from "@angular/router";
import {CommonModule} from "@angular/common";
import {DxValidatorModule} from "devextreme-angular/ui/validator";
import {DxValidationGroupModule} from "devextreme-angular/ui/validation-group";
import {DxPopupModule, DxButtonModule, DxTemplateModule, DxDataGridComponent} from 'devextreme-angular';

import {DxDataGridModule} from 'devextreme-angular';

import CustomStore from 'devextreme/data/custom_store';


import {confirm} from 'devextreme/ui/dialog';
import {HousesService} from "../../shared/services/house.service";
import {CustomStoreService} from "../../shared/services/custom-store.service";


@Component({
  selector: 'app-house_table',
  templateUrl: './house-table.component.html',
  styleUrls: ['./house-table.component.scss']
})
export class HouseTableComponent implements OnInit {
  @ViewChild(DxDataGridComponent, {static: false}) dataGrid: DxDataGridComponent;

  dataSource: any = {};
  currentFilter: any;
  filter: any;
  popupVisible = false;

  get height() {
    if (this.popupVisible) {
      return window.innerHeight - 50;
    } else {
      return window.innerHeight - 170;
    }

  }

  constructor(private houseService: HousesService, private router: Router, private customStoreService: CustomStoreService) {
    this.dataSource = customStoreService.getListCustomStore(houseService);


  }

  ngOnInit() {

  }

  refreshDataGrid() {
    this.dataGrid.instance.refresh();
  }

  onToolbarPreparing(e) {
    e.toolbarOptions.items.unshift({
      location: 'before',
      widget: 'dxButton',
      options: {
        width: 200,
        text: 'Новая запись',
        onClick: this.add.bind(this)
      }
    })

    e.toolbarOptions.items.unshift({
      location: 'after',
      widget: 'dxButton',
      options: {
        icon: 'refresh',
        onClick: this.refreshDataGrid.bind(this)
      }
    })

    e.toolbarOptions.items.unshift({
      location: 'after',
      widget: 'dxButton',
      options: {
        icon: 'fullscreen',
        onClick: this.showPopup.bind(this)
      }
    })
  }

  add() {
    this.router.navigate(['/pages/houses/0']);
  }

  showPopup($event: any) {
    this.popupVisible = !this.popupVisible;

  }
}

const routes: Routes = [
  {path: '', component: HouseTableComponent}
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    DxButtonModule,
    DxCheckBoxModule,
    DxTextBoxModule,
    DxValidatorModule,
    DxValidationGroupModule,
    DxPopupModule,
    DxTemplateModule,
    DxDataGridModule
  ],
  declarations: [HouseTableComponent],
  exports: [HouseTableComponent]
})
export class HouseTableModule {
}
