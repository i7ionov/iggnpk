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


import {Address, AddressService} from "../../shared/services/addresses.service";

@Component({
  selector: 'app-address-form',
  templateUrl: './address-form.component.html',
  styleUrls: ['./address-form.component.scss']
})
export class AddressFormComponent implements OnInit {
  history: any = {};
  @ViewChild('form', {static: false}) form: DxFormComponent;
  id = '';
  addr: Address = new Address();

  constructor(private route: ActivatedRoute,
              private router: Router,
              private addressService: AddressService,
              private _location: Location,
              public auth: AuthService,
              private customStoreService: CustomStoreService) {
  }

  ngOnInit() {
    this.route.params.subscribe((params: Params) => {
      this.id = params.id;
      if (this.id !== '0') {
        this.addressService.retrieve(this.id).subscribe(res => {
            this.addr = res;
          }
        );
      }
    });
  }


  back() {
    if (this._location.getState()['navigationId'] > 1) {
      this._location.back();
    } else {
      this.router.navigate(['/pages/addresses']);
    }

  }


  onFormSubmit(e) {
    const isFormValid = this.form.instance.validate().isValid;

    if (isFormValid) {
      if (this.id != '0') {
        this.addressService.update(this.id, this.addr).subscribe(res => {
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
        this.addressService.create(this.addr).subscribe(res => {
          this.router.navigate([`/pages/addresses/${res.id}`]);
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
  {path: '', component: AddressFormComponent}
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
  declarations: [AddressFormComponent],
  exports: [AddressFormComponent]
})
export class AddressFormModule {
}
