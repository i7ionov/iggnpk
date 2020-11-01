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


import { confirm } from 'devextreme/ui/dialog';
import {HousesService} from "../../shared/services/house.service";


@Component({
  selector: 'app-users',
  templateUrl: './houses.component.html',
  styleUrls: ['./houses.component.scss']
})
export class HousesComponent implements OnInit {
  @ViewChild(DxDataGridComponent, { static: false }) dataGrid: DxDataGridComponent;
  dataSource: any = {};
  currentFilter: any;

  constructor(private houseService: HousesService, private router: Router) {
    function isNotEmpty(value) {
      return value !== undefined && value !== null && value !== "";
    }

    this.dataSource = new CustomStore({
      key: "id",
      totalCount: function () {
        return 6
      },
      load: function (loadOptions) {
        let params = "?";
        [
          "skip",
          "take",

          "sort",
          "filter",
          "totalSummary",
          "group",
          "groupSummary"
        ].forEach(function (i) {
          if (i in loadOptions && isNotEmpty(loadOptions[i]))
            params += `${i}=${JSON.stringify(loadOptions[i])}&`;
        });
        params = params.slice(0, -1);
        if (loadOptions.sort) {
          params += `&orderby=${loadOptions.sort[0].selector}`;
          if (loadOptions.sort[0].desc) {
            params += ' desc';
          }
        }
        return houseService.list(params).toPromise()
          .then((data: any) => {
            return {
              data: data.items,
              totalCount: data.totalCount
            };
          })
          .catch(error => {
            throw 'Data Loading Error'
          });
      }
    })

  }

  ngOnInit() {

  }

  refreshDataGrid(){
    this.dataGrid.instance.refresh();
  }

  onToolbarPreparing(e) {
    e.toolbarOptions.items.unshift( {
      location: 'after',
      widget: 'dxButton',
      options: {
        icon: 'refresh',
        onClick: this.refreshDataGrid.bind(this)
      }
    });
  }


}
const routes: Routes = [
  { path: '', component: HousesComponent}
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
  declarations: [HousesComponent],
  exports: [HousesComponent]
})
export class HousesModule {
}
