import {Component, NgModule, OnInit, ViewChild} from '@angular/core';

import {User} from "../../shared/interfaces/user";
import {
  DxAccordionModule,
  DxButtonModule, DxDataGridModule,
  DxFileUploaderModule,
  DxFormComponent, DxFormModule, DxListModule,
  DxNumberBoxModule, DxPopupModule, DxSelectBoxModule, DxTemplateModule,
  DxTextAreaModule
} from "devextreme-angular";
import {ActivatedRoute, Params, Router, RouterModule, Routes} from "@angular/router";
import {UserService} from "../../shared/services/user.service";
import {GroupService} from "../../shared/services/group.service";
import {CustomStoreService} from "../../shared/services/custom-store.service";
import {CommonModule, Location} from "@angular/common";
import notify from "devextreme/ui/notify";
import {OrganizationFormComponent} from "../organization-form/organization-form.component";
import {DxCheckBoxModule} from "devextreme-angular/ui/check-box";
import {DxTextBoxModule} from "devextreme-angular/ui/text-box";
import {DxValidatorModule} from "devextreme-angular/ui/validator";
import {DxValidationGroupModule} from "devextreme-angular/ui/validation-group";
import {ApplicationPipesModule} from "../../shared/pipes/app-pipes.module";
import {OrganizationSelectModule} from "../../shared/components";
import {DxiItemComponent, DxiItemModule} from "devextreme-angular/ui/nested";
import {confirm} from "devextreme/ui/dialog";

@Component({
  selector: 'app-profile',
  templateUrl: 'profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
  history: any = {};
  @ViewChild('form', {static: false}) form: DxFormComponent;
  user: User = new User();
  id = '';
  old_is_active;
  groupsDataSource: any = {};


  constructor(private route: ActivatedRoute,
              private router: Router,
              private userService: UserService,
              private groupService: GroupService,
              private customStoreService: CustomStoreService,
              private _location: Location,) {
    this.groupsDataSource = customStoreService.getSearchCustomStore(groupService);

  }

  ngOnInit() {
    this.route.params.subscribe((params: Params) => {
      this.id = params.id;
      if (this.id !== '0') {
        this.userService.retrieve(this.id).subscribe(res => {
            this.user = res;
            this.old_is_active = this.user.is_active
          }
        );
      }
      else {
        console.log(this.user)
        this.user.groups = []
        this.old_is_active = false
      }
    });
  }

  back() {
    if (this._location.getState()['navigationId'] > 1) {
      this._location.back();
    } else {
      this.router.navigate(['/pages/users']);
    }

  }

  onFormSubmit(e) {
    if (this.user.is_active !== this.old_is_active) {
      let result = confirm("<i>Отправить электронное письмо об активации/деактивации учетной записи?</i>", "Уведомление");
      result.then((dialogResult) => {
        this.save(dialogResult)
        this.old_is_active = this.user.is_active
      });
    } else {
      this.save(false)
    }
  }

  save(sendEmail) {
    const isFormValid = this.form.instance.validate().isValid;
    if (isFormValid) {
      if (this.id != '0') {
        this.user.sendmail = sendEmail
        this.userService.update(this.id, this.user).subscribe(res => {
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
        this.userService.create(this.user).subscribe(res => {
          this.router.navigate([`/pages/users/${res.id}`]);
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
  {path: '', component: ProfileComponent}
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
    OrganizationSelectModule,
    DxListModule,
    DxPopupModule,
    DxTemplateModule,
    DxDataGridModule,
    DxFormModule,
    DxSelectBoxModule,
    DxAccordionModule,
    ApplicationPipesModule
  ],
  declarations: [ProfileComponent],
  exports: [ProfileComponent]
})
export class ProfileModule {
}
