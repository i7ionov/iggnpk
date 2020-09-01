import {Component, NgModule, OnInit, ViewChild} from '@angular/core';
import {DxCheckBoxModule} from "devextreme-angular/ui/check-box";
import {DxTextBoxModule} from "devextreme-angular/ui/text-box";
import {Router, RouterModule, Routes} from "@angular/router";
import {CommonModule} from "@angular/common";
import {DxValidatorModule} from "devextreme-angular/ui/validator";
import {DxValidationGroupModule} from "devextreme-angular/ui/validation-group";
import {DxPopupModule, DxButtonModule, DxTemplateModule, DxDataGridComponent} from 'devextreme-angular';

import {CapitalRepairNotifyService, Notifies, Notify} from "../../shared/services/capital-repair-notify.service";

import {DxDataGridModule} from 'devextreme-angular';
import {exportDataGrid} from 'devextreme/excel_exporter';
import CustomStore from 'devextreme/data/custom_store';
import ExcelJS from 'exceljs';
import saveAs from 'file-saver';
import {AuthService} from "../../shared/services";
import {ContributionsInformationService} from "../../shared/services/contributions-information.service";

@Component({
  selector: 'app-contributions-information-table',
  templateUrl: './contributions-information-table.component.html',
  styleUrls: ['./contributions-information-table.component.scss']
})
export class ContributionsInformationTableComponent implements OnInit {
  @ViewChild(DxDataGridComponent, {static: false}) dataGrid: DxDataGridComponent;
  dataSource: any = {};
  currentFilter: any;
  get height() {
    return window.innerHeight / 1.35;
}
  get comment_visibility() {
    return this.authService.current_user.permissions.findIndex(p=> p.codename=='view_comment2')>0
  }

  constructor(private contribInfoService: ContributionsInformationService, private router: Router, private authService: AuthService) {

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
        return contribInfoService.list(params).toPromise()
          .then((data: any) => {
            return {
              data: data.items,
              totalCount: data.totalCount,
              summary: data.summary
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

  add() {
    this.router.navigate(['/pages/contrib-info/0']);
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
    }, {
      location: 'after',
      widget: 'dxButton',
      options: {
        icon: 'refresh',
        onClick: this.refreshDataGrid.bind(this)
      }
    });
  }

  onExporting(e) {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Sheet1');

    exportDataGrid({
      component: e.component,
      worksheet: worksheet,
      autoFilterEnabled: true
    }).then(function () {
      // https://github.com/exceljs/exceljs#writing-xlsx
      workbook.xlsx.writeBuffer().then(function (buffer) {
        saveAs(new Blob([buffer], {type: 'application/octet-stream'}), 'contributions.xlsx');
      });
    });
    e.cancel = true;
  }

}
const routes: Routes = [
  { path: '', component: ContributionsInformationTableComponent}
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
  declarations: [ContributionsInformationTableComponent],
  exports: [ContributionsInformationTableComponent]
})
export class ContributionsInformationTableModule {
}