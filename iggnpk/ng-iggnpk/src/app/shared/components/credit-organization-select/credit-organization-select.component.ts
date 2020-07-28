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
  Branch,
  BranchService
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
  @Input() value: Branch = new Branch();
  @Output() valueChange = new EventEmitter<Branch>();
  branches: any = {};
  @Input() required: boolean = true;


  branchDisplayExpr(item) {
    // "item" can be null
    return item && `${item.credit_organization.name} ИНН: ${item.credit_organization.inn} КПП: ${item.kpp} Адрес:${item.address}`;
  }

  constructor(private branchService: BranchService, private customStoreService: CustomStoreService) {

    this.branches = customStoreService.getSearchCustomStore(branchService);

  }

  ngOnInit(): void {
  }


  branchChange(val: any) {
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
