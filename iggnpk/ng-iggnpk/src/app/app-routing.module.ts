import {NgModule} from '@angular/core';
import {Routes, RouterModule, PreloadAllModules} from '@angular/router';
import {
  CreditOrganizationSelectModule,
  LoginFormComponent, OrganizationSelectModule,
} from './shared/components';
import {AuthGuardService} from './shared/services';

import {ProfileComponent} from './pages/profile/profile.component';
import {DisplayDataComponent} from './pages/display-data/display-data.component';
import {
  DxButtonModule,
  DxDataGridModule,
  DxFileUploaderModule,
  DxFormModule,
  DxSelectBoxModule,
  DxValidatorModule
} from 'devextreme-angular';
import {CapitalRepairNotifyComponent} from './pages/capital-repair-notify/capital-repair-notify.component';
import {HouseInputModule} from "./shared/components/house-input/house-input.component";
import {FormsModule} from "@angular/forms";
import {CommonModule} from "@angular/common";
import {FileSizePipe} from "./shared/pipes/filesize.pipe";
import {RegisterFormComponent} from "./shared/components/register-form/register-form.component";
import {AppComponent} from "./app.component";
import {SideNavOuterToolbarComponent, SingleCardComponent} from "./layouts";
import {RootLayoutComponent} from "./layouts/root-layout/root-layout.component";
import {HomeComponent} from "./pages/home/home.component";
import {CapitalRepairNotifiesComponent} from "./pages/capital-repair-notifies/capital-repair-notifies.component";
import {UsersComponent} from "./pages/users/users.component";


const routes: Routes = [
  {
    path: '',
    component: AppComponent,
    children: [
      {
        path: 'pages',
        component: SideNavOuterToolbarComponent,
        children: [
          {
            path: 'home',
            component: HomeComponent,
            canActivate: [AuthGuardService]

          },
          {
            path: 'capital-repair-notifies',
            component: CapitalRepairNotifiesComponent,
            canActivate: [AuthGuardService]

          },
          {
            path: 'capital-repair-notify/:id',
            component: CapitalRepairNotifyComponent,
            canActivate: [AuthGuardService]

          },
          {
            path: 'users',
            component: UsersComponent,
            canActivate: [AuthGuardService]

          },
          {
            path: '**',
            redirectTo: 'home',
            canActivate: [AuthGuardService]
          }
        ]
      },
      {
        path: 'auth',
        component: SingleCardComponent,
        children: [
          {
            path: 'login-form',
            component: LoginFormComponent
          },
          {
            path: 'register-form',
            component: RegisterFormComponent
          },
          {
            path: '**',
            redirectTo: 'login-form',
            canActivate: [AuthGuardService]
          }
        ]
      },

      {
        path: '**',
        redirectTo: 'pages/home',
        canActivate: [AuthGuardService]
      }
    ]
  },

];

@NgModule({
  imports: [RouterModule.forRoot(routes, {preloadingStrategy: PreloadAllModules}), DxDataGridModule, DxFormModule, DxButtonModule, DxValidatorModule, DxFileUploaderModule, HouseInputModule, FormsModule, CommonModule, OrganizationSelectModule, CreditOrganizationSelectModule],
  providers: [AuthGuardService],
  exports: [RouterModule],
  declarations: [ProfileComponent, DisplayDataComponent, RootLayoutComponent]
})
export class AppRoutingModule {
}
