import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Input,
  NgModule,
  OnInit,
  Output
} from '@angular/core';
import {DxFormModule, DxSelectBoxModule} from 'devextreme-angular';
import CustomStore from 'devextreme/data/custom_store';
import {OrganizationService} from '../../services/organization.service';
import {CommonModule} from '@angular/common';
import {CustomStoreService} from '../../services/custom-store.service';
import {HttpClient} from '@angular/common/http';
import {Organization} from '../../interfaces/organization';

@Component({
  selector: 'app-organization-select',
  templateUrl: './organization-select.component.html',
  styleUrls: ['./organization-select.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,

})
export class OrganizationSelectComponent implements OnInit {
  @Input() value: Organization = new Organization();
  @Output() valueChange = new EventEmitter<Organization>();
  @Input() disabled  = false;
  dataSource: any = {};
  displayExpr(item) {
    // "item" can be null
    return item && `${item.name} ИНН: ${item.inn}`;
  }

  constructor(private organizationService: OrganizationService, private customStoreService: CustomStoreService) {

    this.dataSource = customStoreService.getSearchCustomStore(organizationService);

  }

  ngOnInit() {

  }



  organizationChange(org) {
    this.valueChange.emit(org)
  }
}

@NgModule({
  declarations: [OrganizationSelectComponent],
  exports: [OrganizationSelectComponent],
  imports: [DxSelectBoxModule, DxFormModule, CommonModule]
})
export class OrganizationSelectModule {
}
