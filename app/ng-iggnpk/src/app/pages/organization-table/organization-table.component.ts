import {Component, NgModule, OnInit, ViewChild} from '@angular/core';
import {DxCheckBoxModule} from 'devextreme-angular/ui/check-box';
import {DxTextBoxModule} from 'devextreme-angular/ui/text-box';
import {Router, RouterModule, Routes} from '@angular/router';
import {CommonModule} from '@angular/common';
import {DxValidatorModule} from 'devextreme-angular/ui/validator';
import {DxValidationGroupModule} from 'devextreme-angular/ui/validation-group';
import {DxPopupModule, DxButtonModule, DxTemplateModule, DxDataGridComponent} from 'devextreme-angular';

import {DxDataGridModule} from 'devextreme-angular';
import {exportDataGrid} from 'devextreme/excel_exporter';
import CustomStore from 'devextreme/data/custom_store';
import {AuthService} from '../../shared/services';
import {CustomStoreService} from '../../shared/services/custom-store.service';

import {environment} from '../../../environments/environment';
import {OrganizationService} from '../../shared/services/organization.service';


@Component({
  selector: 'app-organization-table',
  templateUrl: './organization-table.component.html',
  styleUrls: ['./organization-table.component.scss']
})
export class OrganizationTableComponent implements OnInit {
  @ViewChild(DxDataGridComponent, {static: false}) dataGrid: DxDataGridComponent;
  dataSource: any = {};
  currentFilter: any;
  filter: any;
  popupVisible = false;

  get height() {
    if (this.popupVisible)
    {
      return window.innerHeight - 50;
    }
    else {
      return window.innerHeight - 170;
    }

  }

  constructor(private organizationService: OrganizationService, private router: Router, private authService: AuthService,
              private customStoreService: CustomStoreService) {

    function isNotEmpty(value) {
      return value !== undefined && value !== null && value !== '';
    }

    this.dataSource = customStoreService.getListCustomStore(organizationService);

  }

  ngOnInit() {

  }



  add() {
    this.router.navigate(['/pages/organizations/0']);
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


  showPopup($event: any) {
    this.popupVisible = !this.popupVisible;

  }

}

const routes: Routes = [
  {path: '', component: OrganizationTableComponent}
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
  declarations: [OrganizationTableComponent],
  exports: [OrganizationTableComponent]
})
export class OrganizationTableModule {
}
