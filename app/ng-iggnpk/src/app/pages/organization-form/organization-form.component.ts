import {Component, ElementRef, NgModule, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute, Params, Router, RouterModule, Routes} from '@angular/router';
import {CommonModule, Location} from '@angular/common';
import {
  DxAccordionModule,
  DxButtonModule,
  DxDataGridModule,
  DxFileUploaderModule,
  DxFormComponent, DxFormModule, DxNumberBoxModule,
  DxPopupModule, DxSelectBoxComponent, DxSelectBoxModule,
  DxTemplateModule, DxTextAreaModule
} from 'devextreme-angular';
import {getDifference} from '../../shared/diff';
import notify from 'devextreme/ui/notify';
import {AuthService, UserGroup} from '../../shared/services';
import {environment} from '../../../environments/environment';
import {confirm} from 'devextreme/ui/dialog';
import {DxValidationGroupModule} from 'devextreme-angular/ui/validation-group';
import {DxValidatorModule} from 'devextreme-angular/ui/validator';
import {DxCheckBoxModule} from 'devextreme-angular/ui/check-box';

import {DxTextBoxModule} from 'devextreme-angular/ui/text-box';
import {ApplicationPipesModule} from '../../shared/pipes/app-pipes.module';
import {CustomStoreService} from '../../shared/services/custom-store.service';
import {OrganizationService} from '../../shared/services/organization.service';


import {Organization, OrganizationType} from '../../shared/interfaces/organization';
import {OrganizationTypeService} from "../../shared/services/organization-type.service";

@Component({
  selector: 'app-contributions-information-form',
  templateUrl: './organization-form.component.html',
  styleUrls: ['./organization-form.component.scss']
})
export class OrganizationFormComponent implements OnInit {
  history: any = {};
  @ViewChild('form', {static: false}) form: DxFormComponent;
  id = '';
  org: Organization = new Organization();
  saveButtonVisibility = false;
  orgTypeDataSource: any = {};

  constructor(private route: ActivatedRoute,
              private router: Router,
              private organizationService: OrganizationService,
              private organizationTypeService: OrganizationTypeService,
              private _location: Location,
              public auth: AuthService,
              private customStoreService: CustomStoreService) {
    this.orgTypeDataSource = customStoreService.getSearchCustomStore(organizationTypeService);
  }

  ngOnInit() {
    this.route.params.subscribe((params: Params) => {
      this.id = params.id;
      if (this.id !== '0') {
        this.organizationService.retrieve(this.id).subscribe(res => {
            this.org = res;
          }
        );
      }
    });
  }

  displayExpr(item) {

    return item && `${item.text}`;


  }

  back() {
    if (this._location.getState()['navigationId'] > 1) {
      this._location.back();
    } else {
      this.router.navigate(['/pages/organizations']);
    }

  }


  onFormSubmit(e) {
    const isFormValid = this.form.instance.validate().isValid;

    if (isFormValid) {
      if (this.id != '0') {
        this.organizationService.update(this.id, this.org).subscribe(res => {
            notify({
              message: 'Форма сохранена',
              position: {
                my: 'center top',
                at: 'center top'
              }
            }, 'success', 3000);
          }, error1 => {
            console.log(error1);
            notify({
              message: 'Форма не сохранена. ' + error1.statusText,
              position: {
                my: 'center top',
                at: 'center top'
              }
            }, 'error', 3000);
          }
        );
      } else {
        this.organizationService.create(this.org).subscribe(res => {
          this.router.navigate([`/pages/organizations/${res.id}`]);
        });
      }


    } else {
      notify({
        message: "Форма не сохранена.",
        position: {
          my: "center top",
          at: "center top"
        }
      }, "error", 3000);
    }
  }
}


const routes: Routes = [
  {path: '', component: OrganizationFormComponent}
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    DxFileUploaderModule,
    DxButtonModule,
    DxCheckBoxModule,
    DxTextBoxModule,
    DxTextAreaModule,
    DxNumberBoxModule,
    DxValidatorModule,
    DxValidationGroupModule,
    DxPopupModule,
    DxTemplateModule,
    DxDataGridModule,
    DxFormModule,
    DxSelectBoxModule,
    DxAccordionModule,
    ApplicationPipesModule
  ],
  declarations: [OrganizationFormComponent],
  exports: [OrganizationFormComponent]
})
export class OrganizationFormModule {
}
