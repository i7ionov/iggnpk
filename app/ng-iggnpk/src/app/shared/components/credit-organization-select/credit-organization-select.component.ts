import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Input,
  NgModule,
  OnInit,
  Output, ViewChild
} from '@angular/core';

import {DxFormComponent, DxFormModule, DxSelectBoxModule, DxValidatorModule} from "devextreme-angular";
import {CommonModule} from "@angular/common";
import {
  CreditOrganization,
  CreditOrganizationService
} from "../../services/credit-organization.service";
import {CustomStoreService} from "../../services/custom-store.service";
import DevExpress from "devextreme";
import dxValidator = DevExpress.ui.dxValidator;


@Component({
  selector: 'app-credit-organization-select',
  templateUrl: './credit-organization-select.component.html',
  styleUrls: ['./credit-organization-select.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,

})

export class CreditOrganizationSelectComponent implements OnInit {
  @ViewChild("form", {static: false}) form: DxFormComponent;
  @Input() value: CreditOrganization = new CreditOrganization();
  @Output() valueChange = new EventEmitter<CreditOrganization>();
  creditOrganizations: any = {};
  @Input() required: boolean = true;


  creditOrganizationDisplayExpr(item) {
    // "item" can be null
    return item && `${item.name} ИНН: ${item.inn}`;
  }

  constructor(private creditOrganizationService: CreditOrganizationService, private customStoreService: CustomStoreService) {

    this.creditOrganizations = customStoreService.getSearchCustomStore(creditOrganizationService);

  }

  ngOnInit(): void {
  }


  creditOrganizationChange(val: any) {
    this.valueChange.emit(val)
  }

  public validate() {
    return (this.form.instance.validate());
  }

  isNotNull(e){
    return e.value && e.value.id > 0;
  }
}

@NgModule({
  declarations: [CreditOrganizationSelectComponent],
  exports: [CreditOrganizationSelectComponent],
  imports: [DxSelectBoxModule, DxFormModule, DxValidatorModule, CommonModule]
})
export class CreditOrganizationSelectModule {
}
