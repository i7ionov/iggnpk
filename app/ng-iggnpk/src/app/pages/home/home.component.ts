import {Component, NgModule, OnInit} from '@angular/core';
import {AuthService} from "../../shared/services";
import {DxDataGridModule, DxDateBoxModule, DxPivotGridModule, DxTreeViewModule} from "devextreme-angular";
import {CommonModule} from "@angular/common";
import {SideNavigationMenuComponent} from "../../shared/components";
import {CustomStoreService} from '../../shared/services/custom-store.service';
import {CrReportService} from "../../shared/services/cr_dashboard";
import {DxiColumnModule} from "devextreme-angular/ui/nested";
import DevExpress from "devextreme";
import { registerLocaleData } from '@angular/common';
import localeRu from '@angular/common/locales/ru'
registerLocaleData(localeRu, 'ru');
import data = DevExpress.data;


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

  update(){
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
    DxPivotGridModule,
    DxDataGridModule,
    DxDateBoxModule,
    DxiColumnModule],
  declarations: [HomeComponent],
  exports: [HomeComponent]
})
export class HomeComponentModule {
}
