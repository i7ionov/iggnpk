import {Component, NgModule, OnInit, ViewChild} from '@angular/core';
import {DxCheckBoxModule} from 'devextreme-angular/ui/check-box';
import {DxTextBoxModule} from 'devextreme-angular/ui/text-box';
import {Router, RouterModule, Routes} from '@angular/router';
import {CommonModule} from '@angular/common';
import {DxValidatorModule} from 'devextreme-angular/ui/validator';
import {DxValidationGroupModule} from 'devextreme-angular/ui/validation-group';
import {DxPopupModule, DxButtonModule, DxTemplateModule, DxDataGridComponent} from 'devextreme-angular';

import {CapitalRepairNotifyService, Notifies, Notify} from '../../shared/services/capital-repair-notify.service';
import * as JSZip from 'jszip';
import {DxDataGridModule} from 'devextreme-angular';
import {exportDataGrid} from 'devextreme/excel_exporter';
import CustomStore from 'devextreme/data/custom_store';
import ExcelJS from 'exceljs';
import saveAs from 'file-saver';
import {AuthService} from '../../shared/services';
import {getContent} from '../../shared/tools/contrib-info-act';
import {environment} from '../../../environments/environment';
import {generate} from '../../shared/tools/word';
import {ContributionsInformationMistakeService} from '../../shared/services/contributions-information-mistake.service';
import {alert} from 'devextreme/ui/dialog';

@Component({
  selector: 'app-capital-repair-notifies',
  templateUrl: './capital-repair-notifies.component.html',
  styleUrls: ['./capital-repair-notifies.component.scss']
})
export class CapitalRepairNotifiesComponent implements OnInit {
  @ViewChild(DxDataGridComponent, {static: false}) dataGrid: DxDataGridComponent;
  dataSource: any = {};
  currentFilter: any;

  get height() {
    return window.innerHeight - 185;
  }

  get comment_visibility() {
    return this.authService.current_user.permissions.findIndex(p => p.codename === 'view_comment2') > 0;
  }

  constructor(private notifyService: CapitalRepairNotifyService,
              private router: Router,
              private authService: AuthService,
              private mistakeService: ContributionsInformationMistakeService) {

    function isNotEmpty(value) {
      return value !== undefined && value !== null && value !== '';
    }

    this.dataSource = new CustomStore({
      key: 'id',
      totalCount() {
        return 6;
      },
      load(loadOptions) {
        let params = '?';
        [
          'skip',
          'take',
          'sort',
          'filter',
          'totalSummary',
          'group',
          'groupSummary'
        ].forEach(i => {
          if (i in loadOptions && isNotEmpty(loadOptions[i])) {
            params += `${i}=${JSON.stringify(loadOptions[i])}&`;
          }
        });
        params = params.slice(0, -1);
        if (loadOptions.sort) {
          params += `&orderby=${loadOptions.sort[0].selector}`;
          if (loadOptions.sort[0].desc) {
            params += ' desc';
          }
        }
        return notifyService.getNotifies(params).toPromise()
          .then((data: any) => {
            return {
              data: data.items,
              totalCount: data.totalCount,
              summary: data.summary
            };
          })
          .catch(error => {
            throw new Error('Data Loading Error');
          });
      }
    });

  }

  ngOnInit() {

  }

  add() {
    this.router.navigate(['/pages/capital-repair-notify/0']);
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
        stylingMode: 'contained',
        type: 'success',
        text: 'Новая запись',
        onClick: this.add.bind(this)
      }
    });

    e.toolbarOptions.items.unshift({
      location: 'after',
      widget: 'dxButton',
      options: {
        icon: 'xlsxfile',
        text: 'В Excel',
        onClick: this.exportToExcel.bind(this)
      }
    })

    e.toolbarOptions.items.unshift({
      location: 'after',
      widget: 'dxButton',
      options: {
        icon: 'refresh',
        onClick: this.refreshDataGrid.bind(this)
      }
    });
    if (this.comment_visibility) {
      e.toolbarOptions.items.unshift({
        location: 'after',
        widget: 'dxButton',
        options: {
          text: 'Акты',
          onClick: this.exportActs.bind(this)
        }
      });
    }

  }

  exportActs() {

    const params = '?filter=' + JSON.stringify(this.dataGrid.instance.getCombinedFilter());
    // window.location.href= environment.backend_url + `/api/v1/cr/notifies/generate_acts/${params}`;
    this.notifyService.generateActs(params).subscribe(res => {
      const result = alert('<i>Задача на формирование актов поставлена в обработку.<br>' +
        'Файл будет направлен по электронной почте.</i>', 'Формирование актов');
      result.then((dialogResult) => {

      });
    });
  }

  fullNameColumn_calculateCellValue(rowData) {
    let text = '';
    if (rowData.last_contrib) {
      rowData.last_contrib.mistakes.forEach(function (m) {
        text = text + m.text + '. '
      });
    }

    return text;
  }

  exportToExcel() {
    const params = '?filter=' + JSON.stringify(this.dataGrid.instance.getCombinedFilter());
    // window.location.href= environment.backend_url + `/api/v1/cr/notifies/export_to_excel/${params}`;
    this.notifyService.exportToExcel(params).subscribe(res => {
      const result = alert('<i>Задача на експорт в Эксель поставлена в обработку.<br>' +
        'Файл будет направлен по электронной почте.</i>', 'Формирование Эксель файла');
      result.then(() => {
      });
    }, error => {
      const result = alert('<i>Задача на експорт в Эксель завершилась ошибкой. <br>' +
        'Обратитесь к системному администратору.</i>', 'Ошибка');
      result.then(() => {
      });
    });

  }


}

const routes: Routes = [
  {path: '', component: CapitalRepairNotifiesComponent}
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
  declarations: [CapitalRepairNotifiesComponent],
  exports: [CapitalRepairNotifiesComponent]
})
export class CapitalRepairNotifiesModule {
}
