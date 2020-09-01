import {Component, ElementRef, NgModule, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute, Params, Router, RouterModule, Routes} from "@angular/router";
import {CommonModule, Location} from '@angular/common';
import {
  DxButtonModule,
  DxDataGridModule,
  DxFileUploaderModule,
  DxFormComponent, DxFormModule,
  DxPopupModule, DxSelectBoxModule,
  DxTemplateModule, DxTextAreaModule
} from "devextreme-angular";
import {getDifference} from "../../shared/diff";
import notify from 'devextreme/ui/notify';
import {AuthService, UserGroup} from "../../shared/services";


import {environment} from "../../../environments/environment";
import {confirm} from 'devextreme/ui/dialog';
import {DxValidationGroupModule} from "devextreme-angular/ui/validation-group";
import {DxValidatorModule} from "devextreme-angular/ui/validator";
import {DxCheckBoxModule} from "devextreme-angular/ui/check-box";

import {DxTextBoxModule} from "devextreme-angular/ui/text-box";
import {FileSizePipe} from "../../shared/pipes/filesize.pipe";
import {
  ContributionsInformation,
  ContributionsInformationService
} from "../../shared/services/contributions-information.service";
import {ApplicationPipesModule} from "../../shared/pipes/app-pipes.module";
import {CustomStoreService} from "../../shared/services/custom-store.service";
import {CapitalRepairNotifyService} from "../../shared/services/capital-repair-notify.service";


@Component({
  selector: 'app-contributions-information-form',
  templateUrl: './contributions-information-form.component.html',
  styleUrls: ['./contributions-information-form.component.scss']
})
export class ContributionsInfromationFormComponent implements OnInit {
  SubmitType = SubmitType;
  @ViewChild("form", {static: false}) form: DxFormComponent;

  get uploadAuthorization() {
    return 'Token ' + this.auth.token;
  };

  get uploadUrl() {
    return `${environment.file_url}create/`
  }


  id = '';
  contrib_info: ContributionsInformation = new ContributionsInformation();
  clean_contrib_info = new ContributionsInformation();
  acceptButtonVisibility = false;
  rejectButtonVisibility = false;
  sendForApprovalButtonVisibility = false;
  saveButtonVisibility = false;
  contribInfoDataSource: any = {};

  get comment_visibility() {
    return this.auth.current_user.permissions.findIndex(p => p.codename == 'view_comment2') > 0
  }
  get skip_verification() {
    return this.auth.current_user.permissions.findIndex(p => p.codename == 'view_comment2') > 0
  }
  get dateIsReadOnly() {
    if (this.auth.current_user) {
      return this.auth.current_user.groups.indexOf(UserGroup.Admin) == -1
    }
    else {
      return false
    }
  };

  constructor(private route: ActivatedRoute,
              private router: Router,
              private contribInfoService: ContributionsInformationService,
              private notifyService:CapitalRepairNotifyService,
              private _location: Location,
              public auth: AuthService,
              private customStoreService: CustomStoreService) {
    this.contribInfoDataSource = customStoreService.getSearchCustomStore(notifyService)
  }


  setPermissions(user) {

    if (this.contrib_info.notify.organization.id == this.auth.current_user.organization.id || user.groups.indexOf(UserGroup.Admin) != -1) {
      if (this.contrib_info.status.id == NotifyStatus.Approving) {
        this.acceptButtonVisibility = false;
        this.sendForApprovalButtonVisibility = false;
        this.saveButtonVisibility = false;
        this.rejectButtonVisibility = true;
        if (user.groups.indexOf(UserGroup.Admin) != -1) {
          this.acceptButtonVisibility = true;
        }
      }
      else if (this.contrib_info.status.id == NotifyStatus.Editing) {
        this.saveButtonVisibility = true;
        this.sendForApprovalButtonVisibility = true;
        this.rejectButtonVisibility = false;
        this.acceptButtonVisibility = false;
      }
      else if (this.contrib_info.status.id == NotifyStatus.Approved) {
        this.saveButtonVisibility = false;
        this.sendForApprovalButtonVisibility = false;
        this.rejectButtonVisibility = false;
        this.acceptButtonVisibility = false;
        if (user.groups.indexOf(UserGroup.Admin) != -1) {
          this.saveButtonVisibility = true;
        }
      }
      else {
        this.sendForApprovalButtonVisibility = false;
        this.rejectButtonVisibility = false;
        this.acceptButtonVisibility = false;
        this.saveButtonVisibility = false;
      }
    }
  }

  ngOnInit() {

    this.route.params.subscribe((params: Params) => {

      this.id = params.id;
      if (this.id != '0') {
        this.contribInfoService.retrieve(this.id).subscribe(res => {
            this.contrib_info = res;
            this.contrib_info = JSON.parse(JSON.stringify(res));
            this.setPermissions(this.auth.current_user);
          }
        )
      }
      else {
        let a = new Date();
        a.getFullYear();
        this.contrib_info.date = `${a.getFullYear()}-${a.getMonth() + 1}-${a.getDate()}`;
        this.sendForApprovalButtonVisibility = true;
        this.saveButtonVisibility = true;
      }


    })
  }

  back() {
    if (this._location.getState()['navigationId'] > 1) {
      this._location.back();
    }
    else {
      this.router.navigate(['/pages/contrib-info']);
    }

  }

  onFormSubmit(e) {
    let is_form_valid = true;
    let is_credit_org_valid = true;
    let is_house_valid = true;
    if (e != SubmitType.Exclusion && !this.skip_verification) {
      is_form_valid = this.form.instance.validate().isValid;
    }

    if (is_form_valid &&
      is_credit_org_valid &&
      is_house_valid) {
      switch (e) {
        case SubmitType.Sending: {
          this.contrib_info.status.id = NotifyStatus.Approving;
          break;
        }
        case SubmitType.Rejecting: {
          this.contrib_info.status.id = NotifyStatus.Editing;
          break;
        }
        case SubmitType.Accepting: {
          this.contrib_info.status.id = NotifyStatus.Approved;
          break;
        }
        case SubmitType.Saving: {
          if (this.contrib_info.status.id==0){
            this.contrib_info.status.id = NotifyStatus.Editing;
          }
          break;
        }
        case SubmitType.Exclusion: {
          this.contrib_info.status.id = NotifyStatus.Excluded;
          break;
        }
      }
      if (this.id != '0') {
        let n = getDifference(this.contrib_info, this.clean_contrib_info);
        if (n) {
          if (this.contrib_info.files.length == 0) {
            n[0].files = 'empty'
          }
          else {
            n[0].files = this.contrib_info.files
          }
          this.contribInfoService.update(this.id, n[0]).subscribe(res => {
              notify({
                message: "Форма сохранена",
                position: {
                  my: "center top",
                  at: "center top"
                }
              }, "success", 3000);
              this.setPermissions(this.auth.current_user);
              this.clean_contrib_info = JSON.parse(JSON.stringify(res));
            }, error1 => {
            console.log(error1);
             notify({
                message: "Форма не сохранена. " + error1.statusText,
                position: {
                  my: "center top",
                  at: "center top"
                }
              }, "error", 3000);
            }
          );
        }
      }
      else {
        this.contribInfoService.create(this.contrib_info).subscribe(res => {
            this.router.navigate([`/pages/contrib-info/${res.id}`]);
          }
        );
      }
    }
    else {
      notify({
                message: "Форма не сохранена.",
                position: {
                  my: "center top",
                  at: "center top"
                }
              }, "error", 3000);
    }


  }

  onUploaded(e) {
    if (e.request.status == 201) {
      if (!this.contrib_info.files) {
        this.contrib_info.files = []
      }
      const file = JSON.parse(e.request.response);
      console.log(file);
      this.contrib_info.files.push(file);
    }
  }

  fileDelete(file) {
    let result = confirm("<i>Удалить файл?</i>", "Подтверждение");
    result.then((dialogResult) => {
      if (dialogResult) {
        const index = this.contrib_info.files.findIndex(f => f.id == file.id);
        if (index > -1) {
          this.contrib_info.files.splice(index, 1);

        }
      }
    });

  }

  displayExpr(item) {
    // "item" can be null
    return item && `№${item.id} от ${item.date}. Адрес: ${item.house.address.city}, ${item.house.address.street}, ${item.house.number}`;
  }


}

enum NotifyStatus {
  Editing = 1,
  Approving,
  Approved,
  Excluded
}

enum SubmitType {
  Saving = 1,
  Sending,
  Rejecting,
  Accepting,
  Exclusion
}

const routes: Routes = [
  {path: '', component: ContributionsInfromationFormComponent}
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
    DxValidatorModule,
    DxValidationGroupModule,
    DxPopupModule,
    DxTemplateModule,
    DxDataGridModule,
    DxFormModule,
    DxSelectBoxModule,
    ApplicationPipesModule
  ],
  declarations: [ContributionsInfromationFormComponent],
  exports: [ContributionsInfromationFormComponent]
})
export class ContributionsInfromationFormModule {
}
