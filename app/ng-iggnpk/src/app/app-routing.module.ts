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
import {HouseInputModule} from "./shared/components/house-input/house-input.component";
import {FormsModule} from "@angular/forms";
import {CommonModule} from "@angular/common";
import {FileSizePipe} from "./shared/pipes/filesize.pipe";
import {RegisterFormComponent} from "./shared/components/register-form/register-form.component";
import {AppComponent} from "./app.component";
import {SideNavOuterToolbarComponent, SingleCardComponent} from "./layouts";
import {RootLayoutComponent} from "./layouts/root-layout/root-layout.component";
import {HomeComponent} from "./pages/home/home.component";

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
            loadChildren: () => import('./pages/capital-repair-notifies/capital-repair-notifies.component').then(m => m.CapitalRepairNotifiesModule),
            canLoad: [AuthGuardService]

          },
          {
            path: 'capital-repair-notify/:id',
            loadChildren: () => import('./pages/capital-repair-notify/capital-repair-notify.component').then(m => m.CapitalRepairNotifyModule),
            canLoad: [AuthGuardService]

          },
          {
            path: 'contrib-info',
            loadChildren: () => import('./pages/contrib-info-table/contributions-information-table.component').then(m => m.ContributionsInformationTableModule),
            canLoad: [AuthGuardService]

          },
          {
            path: 'contrib-info/:id',
            loadChildren: () => import('./pages/contrib-info-form/contributions-infromation-form.component').then(m => m.ContributionsInfromationFormModule),
            canLoad: [AuthGuardService]

          },
          {
            path: 'organizations',
            loadChildren: () => import('./pages/organization-table/organization-table.component').then(m => m.OrganizationTableModule),
            canLoad: [AuthGuardService]

          },
          {
            path: 'organizations/:id',
            loadChildren: () => import('./pages/organization-form/organization-form.component').then(m => m.OrganizationFormModule),
            canLoad: [AuthGuardService]

          },
          {
            path: 'users',
            loadChildren: () => import('./pages/users/users.component').then(m => m.UsersModule),
            canLoad: [AuthGuardService]

          },
          {
            path: 'houses',
            loadChildren: () => import('./pages/houses/houses.component').then(m => m.HousesModule),
            canLoad: [AuthGuardService]

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
