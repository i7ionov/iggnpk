import {Component, NgModule, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Router, RouterModule} from '@angular/router';

import {AuthService, AppInfoService, FormResponse} from '../../services';
import {DxButtonModule} from 'devextreme-angular/ui/button';
import {DxCheckBoxModule} from 'devextreme-angular/ui/check-box';
import {DxTextBoxModule} from 'devextreme-angular/ui/text-box';
import {DxValidatorModule} from 'devextreme-angular/ui/validator';
import {DxValidationGroupModule} from 'devextreme-angular/ui/validation-group';

@Component({
  selector: 'app-login-form',
  templateUrl: './login-form.component.html',
  styleUrls: ['./login-form.component.scss']
})
export class LoginFormComponent implements OnInit{
  login = '';
  password = '';
  errors;

  constructor(private authService: AuthService, public appInfo: AppInfoService, private router: Router) {
  }

  onLoginClick(args) {
    if (!args.validationGroup.validate().isValid) {
      return;
    }

    this.authService.getToken(this.login, this.password).subscribe(res => {
      localStorage.setItem('token', res.auth_token);
      this.router.navigate(['/']);

    }, error => {
      this.errors = error;
    });


    args.validationGroup.reset();
  }

  ngOnInit(): void {
    if (!!localStorage.getItem('token')){
      this.router.navigate(['/']);
    }
  }

  onRegisterClick($event: any) {
    this.router.navigate(['/register-form']);
  }
}

@NgModule({
  imports: [
    CommonModule,
    RouterModule,
    DxButtonModule,
    DxCheckBoxModule,
    DxTextBoxModule,
    DxValidatorModule,
    DxValidationGroupModule
  ],
  declarations: [LoginFormComponent],
  exports: [LoginFormComponent]
})
export class LoginFormModule {
}
