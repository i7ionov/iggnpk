import {Component, ElementRef, NgModule, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute, Params, Router, RouterModule, Routes} from '@angular/router';
import {CommonModule, Location} from '@angular/common';
import {
  DxAccordionModule,
  DxButtonModule,
  DxDataGridModule, DxDateBoxModule,
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
import {HousesService} from '../../shared/services/house.service';
import {OrganizationService} from '../../shared/services/organization.service';

import {AddressService} from "../../shared/services/addresses.service";
import {House} from "../../shared/services/house.service";

@Component({
  selector: 'app-organization-form',
  templateUrl: './house-form.component.html',
  styleUrls: ['./house-form.component.scss']
})
export class HouseFormComponent implements OnInit {
  history: any = {};
  @ViewChild('form', {static: false}) form: DxFormComponent;
  id = '';
  house: House = new House();
  addressDataSource: any = {};
  organizationDataSource: any = {};

  constructor(private route: ActivatedRoute,
              private router: Router,
              private houseService: HousesService,
              private organizationService: OrganizationService,
              private addressService: AddressService,
              private _location: Location,
              public auth: AuthService,
              private customStoreService: CustomStoreService) {
    this.addressDataSource = customStoreService.getSearchCustomStore(addressService);
    this.organizationDataSource = customStoreService.getSearchCustomStore(organizationService);
  }

  ngOnInit() {
    this.route.params.subscribe((params: Params) => {
      this.id = params.id;
      if (this.id !== '0') {
        this.houseService.retrieve(this.id).subscribe(res => {
            this.house = res;
          }
        );
      }
    });
  }

  addressDisplayExpr(item) {
    return item && `${item.area}, ${item.city}, ${item.street}`;
  }

  orgDisplayExpr(item) {
    return item && `${item.name}, ИНН: ${item.inn}`;
  }

  back() {
    if (this._location.getState()['navigationId'] > 1) {
      this._location.back();
    } else {
      this.router.navigate(['/pages/houses']);
    }

  }


  onFormSubmit(e) {
    const isFormValid = this.form.instance.validate().isValid;

    if (isFormValid) {
      if (this.id != '0') {
        this.houseService.update(this.id, this.house).subscribe(res => {
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
        this.houseService.create(this.house).subscribe(res => {
          this.router.navigate([`/pages/houses/${res.id}`]);
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
  {path: '', component: HouseFormComponent}
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    DxFileUploaderModule,
    DxButtonModule,
    DxCheckBoxModule,
    DxTextBoxModule,
    DxDateBoxModule,
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
  declarations: [HouseFormComponent],
  exports: [HouseFormComponent]
})
export class HouseFormModule {
}
