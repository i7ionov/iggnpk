import {Component, NgModule, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Router, RouterModule} from '@angular/router';

import {AuthService, AppInfoService, FormResponse, User} from '../../services';
import {DxButtonModule} from 'devextreme-angular/ui/button';
import {DxCheckBoxModule} from 'devextreme-angular/ui/check-box';
import {DxTextBoxModule} from 'devextreme-angular/ui/text-box';
import {DxValidatorModule} from 'devextreme-angular/ui/validator';
import {DxValidationGroupModule} from 'devextreme-angular/ui/validation-group';
import {Organization} from "../../interfaces/organization";
import {OrganizationService} from "../../services/organization.service";
import {DxSelectBoxModule} from "devextreme-angular";
import {alert} from "devextreme/ui/dialog";
import {OrganizationTypeService} from "../../services/organization-type.service";
import {CustomStoreService} from "../../services/custom-store.service";
import {UserService} from "../../services/user.service";



@Component({
  selector: 'app-register-form',
  templateUrl: './register-form.component.html',
  styleUrls: ['./register-form.component.scss']
})
export class RegisterFormComponent implements OnInit {
  user: User = new class implements User {
    email: string;
    groups: number[];
    organization: Organization = new Organization();
    password: string;
    re_password: string;
    username: string;
  };
  orgTypes;
  orgTypesStore;
  errors;

  passwordComparison = () => {
    return this.user.password;
  };


  orgUsersCount(params) {
    return new Promise((resolve, reject) => {

      this.userService.getOrgUserCount(params.value)
        .toPromise()
        .then((res: any) => {
          resolve(res.count < 1);
        })
        .catch(error => {
          console.error("Server-side validation error", error);

          reject("Cannot contact validation server");
        });
    })
  }

  isEmailUsed(params) {
    return new Promise((resolve, reject) => {
      this.userService.getEmailIsUsed(params.value)
        .toPromise()
        .then((res: any) => {
          resolve(!res.result);
        })
        .catch(error => {
          console.error("Server-side validation error", error);

          reject("Cannot contact validation server");
        });
    })
  }

  constructor(private authService: AuthService, public appInfo: AppInfoService, private router: Router,
              private orgService: OrganizationService,
              private userService: UserService,
              private organizationTypeService: OrganizationTypeService,
              private customStoreService: CustomStoreService) {
    this.orgUsersCount = this.orgUsersCount.bind(this);
    this.isEmailUsed = this.isEmailUsed.bind(this);
    this.orgTypes = customStoreService.getSearchCustomStore(organizationTypeService);
  }

  onRegisterClick(args) {

    if (!args.validationGroup.validate().isValid) {
      return;
    }
    this.userService.create(this.user).subscribe(res => {

      let result = alert("<i>Регистрация учетной записи произведена успешно.<br>" +
        "Ожидайте активации учетной записи сотрудником Инспекции.<br>" +
        "Уведомление об активации вы получите на указанную электронную почту.</i>", "Регистрация завершена успешно");
      result.then((dialogResult) => {
        this.router.navigate(['auth//login-page']);
      });

    }, error => {
      this.errors = error.error;
    });

  }

  ngOnInit(): void {




  }


}

@NgModule({
  imports: [
    CommonModule,
    RouterModule,
    DxButtonModule,
    DxCheckBoxModule,
    DxTextBoxModule,
    DxSelectBoxModule,
    DxValidatorModule,
    DxValidationGroupModule
  ],
  declarations: [RegisterFormComponent],
  exports: [RegisterFormComponent]
})
export class RegisterFormModule {
}
