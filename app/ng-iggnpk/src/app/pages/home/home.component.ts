import {Component, NgModule, OnInit} from '@angular/core';
import {AuthService} from "../../shared/services";
import {DxBoxModule, DxDataGridModule, DxDateBoxModule, DxPivotGridModule, DxTreeViewModule} from "devextreme-angular";
import {CommonModule} from "@angular/common";
import {SideNavigationMenuComponent} from "../../shared/components";
import {CustomStoreService} from '../../shared/services/custom-store.service';
import {CrReportService} from "../../shared/services/cr_dashboard";
import {DxiColumnModule} from "devextreme-angular/ui/nested";
import DevExpress from "devextreme";
import {registerLocaleData} from '@angular/common';
import localeRu from '@angular/common/locales/ru'

registerLocaleData(localeRu, 'ru');
import data = DevExpress.data;
import {DxButtonModule} from "devextreme-angular/ui/button";


@Component({
  templateUrl: 'home.component.html',
  styleUrls: ['./home.component.scss']
})

export class HomeComponent implements OnInit {
  constructor(private auth: AuthService, private customStoreService: CustomStoreService, private crReportService: CrReportService) {

  }

  date_start = '2021-01-01';
  date_end = '2021-04-01';
  dataSource = this.crReportService.default_report();

  tableToExcel(table, name, filename) {
    let uri = 'data:application/vnd.ms-excel;base64,',
      template = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"><title></title><head><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet><x:Name>{worksheet}</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--><meta http-equiv="content-type" content="text/plain; charset=UTF-8"/></head><body><table>{table}</table></body></html>',
      base64 = function (s) {
        return window.btoa(unescape(encodeURIComponent(s)))
      }, format = function (s, c) {
        return s.replace(/{(\w+)}/g, function (m, p) {
          return c[p];
        })
      }

    if (!table.nodeType) table = document.getElementById(table)
    var ctx = {worksheet: name || 'Worksheet', table: table.innerHTML}

    var link = document.createElement('a');
    link.download = filename;
    link.href = uri + base64(format(template, ctx));
    link.click();
  }


  update() {
    this.crReportService.get(`?date_start=${this.date_start}&date_end=${this.date_end}`).subscribe(res => {
      console.log(res)
      this.dataSource = res

    }, error => {

    });
  }

  ngOnInit(): void {
    this.update()
  }
}

@NgModule({
  imports: [DxTreeViewModule, CommonModule,
    DxBoxModule,
    DxDateBoxModule,
    DxButtonModule,
    DxiColumnModule],
  declarations: [HomeComponent],
  exports: [HomeComponent]
})
export class HomeComponentModule {
}
