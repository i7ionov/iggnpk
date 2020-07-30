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
import ArrayStore from "devextreme/data/array_store";

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

  constructor(private authService: AuthService, public appInfo: AppInfoService, private router: Router, private orgService: OrganizationService) {

  }

  onRegisterClick(args) {
    if (!args.validationGroup.validate().isValid) {
      return;
    }
    this.authService.createUser(this.user).subscribe(res => {
      //localStorage.setItem('token', res.auth_token);
      //this.router.navigate(['/']);
      console.log(res)

    }, error => {
      this.errors = error.error;
    });

  }

  ngOnInit(): void {
    this.orgService.types().subscribe(res=>{
      this.orgTypes = res;
    });

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
