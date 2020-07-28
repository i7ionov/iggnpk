import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {
  CreditOrganizationSelectModule,
  LoginFormComponent, OrganizationSelectModule,
} from './shared/components';
import { AuthGuardService } from './shared/services';
import { HomeComponent } from './pages/home/home.component';
import { ProfileComponent } from './pages/profile/profile.component';
import { DisplayDataComponent } from './pages/display-data/display-data.component';
import {
  DxButtonModule,
  DxDataGridModule,
  DxFileUploaderModule,
  DxFormModule,
  DxSelectBoxModule,
  DxValidatorModule
} from 'devextreme-angular';
import { CapitalRepairNotifiesComponent } from './pages/capital-repair-notifies/capital-repair-notifies.component';
import { CapitalRepairNotifyComponent } from './pages/capital-repair-notify/capital-repair-notify.component';
import {HouseInputModule} from "./shared/components/house-input/house-input.component";
import {FormsModule} from "@angular/forms";
import {CommonModule} from "@angular/common";
import {FileSizePipe} from "./shared/pipes/filesize.pipe";


const routes: Routes = [
  {
    path: 'pages/capital-repair-notify/:id',
    component: CapitalRepairNotifyComponent,
    canActivate: [ AuthGuardService ]
  },
  {
    path: 'pages/capital-repair-notifies',
    component: CapitalRepairNotifiesComponent,
    canActivate: [ AuthGuardService ]
  },
  {
    path: 'display-data',
    component: DisplayDataComponent,
    canActivate: [ AuthGuardService ]
  },
  {
    path: 'profile',
    component: ProfileComponent,
    canActivate: [ AuthGuardService ]
  },
  {
    path: 'home',
    component: HomeComponent,
    canActivate: [ AuthGuardService ]
  },
  {
    path: 'login-form',
    component: LoginFormComponent
  },
  {
    path: '**',
    redirectTo: 'home',
    canActivate: [ AuthGuardService ]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes), DxDataGridModule, DxFormModule,DxButtonModule, DxValidatorModule, DxFileUploaderModule, HouseInputModule, FormsModule, CommonModule, OrganizationSelectModule, CreditOrganizationSelectModule],
  providers: [AuthGuardService],
  exports: [RouterModule],
  declarations: [HomeComponent, ProfileComponent, DisplayDataComponent, CapitalRepairNotifyComponent, FileSizePipe]
})
export class AppRoutingModule { }
