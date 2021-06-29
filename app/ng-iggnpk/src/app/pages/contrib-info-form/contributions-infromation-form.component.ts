import {Component, ElementRef, NgModule, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute, Params, Router, RouterModule, Routes} from "@angular/router";
import {CommonModule, Location} from '@angular/common';
import {
  DxAccordionModule,
  DxButtonModule,
  DxDataGridModule,
  DxFileUploaderModule,
  DxFormComponent, DxFormModule, DxNumberBoxModule,
  DxPopupModule, DxSelectBoxComponent, DxSelectBoxModule,
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
import {generate} from "../../shared/tools/word";
import {
  ContributionsInformation,
  ContributionsInformationService
} from "../../shared/services/contributions-information.service";
import {ApplicationPipesModule} from "../../shared/pipes/app-pipes.module";
import {CustomStoreService} from "../../shared/services/custom-store.service";
import {CapitalRepairNotifyService} from "../../shared/services/capital-repair-notify.service";
import {ContributionsInformationMistakeService} from "../../shared/services/contributions-information-mistake.service";
import {DxiGroupComponent, DxiGroupModule} from "devextreme-angular/ui/nested";
import {getContent} from "../../shared/tools/contrib-info-act";
import saveAs from "file-saver"

@Component({
  selector: 'app-contributions-information-form',
  templateUrl: './contributions-information-form.component.html',
  styleUrls: ['./contributions-information-form.component.scss']
})
export class ContributionsInfromationFormComponent implements OnInit {
  SubmitType = SubmitType;
  history: any = {};
  file_backend_url = environment.file_url
  @ViewChild("form", {static: false}) form: DxFormComponent;
  @ViewChild("mistakes", {static: false}) mistakes: DxSelectBoxComponent;

  get uploadAuthorization() {
    return 'Token ' + this.auth.token;
  };

  get uploadUrl() {
    return `${environment.file_url}create/`
  }

  get delta(): number {
    return Number((this.contrib_info.assessed_contributions_total - this.contrib_info.received_contributions_total).toFixed(2))
  }

  id = '';
  contrib_info: ContributionsInformation = new ContributionsInformation();
  clean_contrib_info = new ContributionsInformation();
  acceptButtonVisibility = false;
  rejectButtonVisibility = false;
  sendForApprovalButtonVisibility = false;
  saveButtonVisibility = false;
  contribInfoDataSource: any = {};
  mistakesDataSource: any = {};

  get comment_visibility() {
    return this.auth.current_user.permissions.findIndex(p => p.codename == 'view_comment2') > 0
  }

  get mistakes_visibility() {
    return this.comment_visibility || this.contrib_info.mistakes.length > 0
  }

  get skip_verification() {
    return this.auth.current_user.permissions.findIndex(p => p.codename == 'view_comment2') > 0
  }

  get dateIsReadOnly() {
    if (this.auth.current_user) {
      return !this.auth.current_user.is_staff
    } else {
      return false
    }
  };


  constructor(private route: ActivatedRoute,
              private router: Router,
              private contribInfoService: ContributionsInformationService,
              private notifyService: CapitalRepairNotifyService,
              private contribInfoMistakesService: ContributionsInformationMistakeService,
              private _location: Location,
              public auth: AuthService,
              private customStoreService: CustomStoreService) {
    this.contribInfoDataSource = customStoreService.getSearchCustomStore(notifyService);
    this.contribInfoDataSource.pageSize(10);
    //отображаются только согласованые уведомления, у которых не указана ороанизация Фонд кап. ремонта ПК(5902990563)
    this.contribInfoDataSource.filter([["status.id", "=", '3'],'and', ["organization.inn", "<>", '5902990563']]);
    this.mistakesDataSource = customStoreService.getSearchCustomStore(contribInfoMistakesService);
  }

  act() {
    const data = getContent(this.contrib_info.notify, this.contrib_info.mistakes)
    generate(`${environment.backend_url}/media/templates/act.docx`, data).then(a=>{
      saveAs(a, "file.docx")
    })

    //window.location.href=`/api/v1/cr/contrib_info/generate_act/${this.id}/`;
  }

  setPermissions(user) {

    if (this.contrib_info.notify.organization.id == this.auth.current_user.organization.id || user.is_staff) {
      if (this.contrib_info.status.id == NotifyStatus.Approving) {
        this.acceptButtonVisibility = false;
        this.sendForApprovalButtonVisibility = false;
        this.saveButtonVisibility = false;
        this.rejectButtonVisibility = true;
        if (user.is_staff) {
          this.acceptButtonVisibility = true;
        }
      } else if (this.contrib_info.status.id == NotifyStatus.Editing) {
        this.saveButtonVisibility = true;
        this.sendForApprovalButtonVisibility = true;
        this.rejectButtonVisibility = false;
        this.acceptButtonVisibility = false;
      } else if (this.contrib_info.status.id == NotifyStatus.Approved) {
        this.saveButtonVisibility = false;
        this.sendForApprovalButtonVisibility = false;
        this.rejectButtonVisibility = false;
        this.acceptButtonVisibility = false;
        if (user.is_staff) {
          this.saveButtonVisibility = true;
        }
      } else {
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
      if (this.id !== '0') {
        this.contribInfoService.retrieve(this.id).subscribe(res => {
            this.contrib_info = res;
            this.contrib_info = JSON.parse(JSON.stringify(res));
            this.setPermissions(this.auth.current_user);
          }
        );
        if (this.auth.current_user.is_staff) {
          this.contribInfoService.getHistory(this.id).subscribe(res => {
            this.history = res;
          });
        }
      } else {
        const a = new Date();
        this.contrib_info.date = `${a.getFullYear()}-${a.getMonth() + 1}-${a.getDate()}`;
        this.sendForApprovalButtonVisibility = true;
        this.saveButtonVisibility = true;
      }


    })
  }

  back() {
    if (this._location.getState()['navigationId'] > 1) {
      this._location.back();
    } else {
      this.router.navigate(['/pages/contrib-info']);
    }

  }

  onMistakeSelected(e) {
    if (e) {
      console.log(e);
      this.contrib_info.mistakes.push(e);
      this.mistakes.writeValue(undefined)
    }

  }

  mistakeDelete(mistake) {
    const index = this.contrib_info.mistakes.findIndex(f => f.id == mistake.id);
    if (index > -1) {
      this.contrib_info.mistakes.splice(index, 1);

    }

  }

  onFormSubmit(e) {
    let is_form_valid = true;
    let is_credit_org_valid = true;
    let is_house_valid = true;
    this.contrib_info.delta_total = this.delta;
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
          if (this.contrib_info.status.id == 0) {
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
          } else {
            n[0].files = this.contrib_info.files
          }
          if (this.contrib_info.mistakes.length == 0) {
            n[0].mistakes = 'empty'
          } else {
            n[0].mistakes = this.contrib_info.mistakes
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
      } else {
        this.contribInfoService.create(this.contrib_info).subscribe(res => {
            this.router.navigate([`/pages/contrib-info/${res.id}`]);
          }
        );
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

  onUploaded(e) {
    if (e.request.status == 201) {
      if (!this.contrib_info.files) {
        this.contrib_info.files = []
      }
      const file = JSON.parse(e.request.response);
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
    let latest_contrib_date = '';
    let address = '';
    if (item && item.last_contrib) {
      latest_contrib_date = `(${item.last_contrib.date})`
    }
    if (item && item.house)
    {
      address = `${item.house.address.city}, ${item.house.address.street}, ${item.house.number}`;
    }
    else
    {
      address = 'нет';
    }
    return item && `№${item.id}, ${item.account_number} Адрес: ${address} ${latest_contrib_date}`;


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
  declarations: [ContributionsInfromationFormComponent],
  exports: [ContributionsInfromationFormComponent]
})
export class ContributionsInfromationFormModule {
}
