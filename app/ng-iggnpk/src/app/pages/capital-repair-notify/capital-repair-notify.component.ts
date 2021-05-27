import {Component, ElementRef, NgModule, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute, Params, Router, RouterModule, Routes} from '@angular/router';
import {CapitalRepairNotifyService, Notify} from '../../shared/services/capital-repair-notify.service';
import {CommonModule, Location} from '@angular/common';
import {
  DxAccordionModule,
  DxButtonModule,
  DxDataGridModule,
  DxFileUploaderModule,
  DxFormComponent, DxFormModule,
  DxPopupModule,
  DxTemplateModule, DxTextAreaModule
} from 'devextreme-angular';
import {getDifference} from '../../shared/diff';
import notify from 'devextreme/ui/notify';
import {AuthService, UserGroup} from '../../shared/services';
import {History} from '../../shared/interfaces/history';
import {
  CreditOrganizationSelectComponent,
  CreditOrganizationSelectModule,
  OrganizationSelectComponent, OrganizationSelectModule
} from '../../shared/components';
import {HouseInputComponent, HouseInputModule} from '../../shared/components/house-input/house-input.component';
import {environment} from '../../../environments/environment';
import {confirm} from 'devextreme/ui/dialog';
import {DxValidationGroupModule} from 'devextreme-angular/ui/validation-group';
import {DxValidatorModule} from 'devextreme-angular/ui/validator';
import {DxCheckBoxModule} from 'devextreme-angular/ui/check-box';
import {CapitalRepairNotifiesComponent} from '../capital-repair-notifies/capital-repair-notifies.component';
import {DxTextBoxModule} from 'devextreme-angular/ui/text-box';
import {FileSizePipe} from '../../shared/pipes/filesize.pipe';
import {ApplicationPipesModule} from '../../shared/pipes/app-pipes.module';


@Component({
  selector: 'app-capital-repair-notify',
  templateUrl: './capital-repair-notify.component.html',
  styleUrls: ['./capital-repair-notify.component.scss']
})
export class CapitalRepairNotifyComponent implements OnInit {
  SubmitType = SubmitType;
  file_backend_url = environment.file_url
  history: any = {};
  @ViewChild('form', {static: false}) form: DxFormComponent;
  @ViewChild('credit_organization_select', {static: false}) credit_organization_select: CreditOrganizationSelectComponent;
  @ViewChild('house_input', {static: false}) house_input: HouseInputComponent;
  @ViewChild('organization_select', {static: false}) organization_select: OrganizationSelectComponent;

  get uploadAuthorization() {
    return 'Token ' + this.auth.token;
  }

  get uploadUrl() {
    return `${environment.file_url}create/`;
  }

  excludeButtonVisibility = false;

  id = '';
  notify: Notify = new Notify();
  clean_notify = new Notify();
  readOnly: any;
  acceptButtonVisibility = false;
  rejectButtonVisibility = false;
  sendForApprovalButtonVisibility = false;
  saveButtonVisibility = false;

  get comment_visibility() {
    return this.auth.current_user.permissions.findIndex(p => p.codename == 'view_comment2') > 0;
  }

  get skip_verification() {
    return this.auth.current_user.permissions.findIndex(p => p.codename == 'view_comment2') > 0;
  }

  get organizationSelectIsReadOnly() {
    if (this.auth.current_user) {
      return !this.auth.current_user.is_staff;
    } else {
      return false;
    }
  }

  constructor(private route: ActivatedRoute,
              private router: Router,
              private notifyService: CapitalRepairNotifyService,
              private _location: Location,
              public auth: AuthService) {
  }


  setPermissions(user) {

    if (this.notify.organization.id == this.auth.current_user.organization.id || this.auth.current_user.is_staff) {
      if (this.notify.status.id == NotifyStatus.Approving) {
        this.acceptButtonVisibility = false;
        this.sendForApprovalButtonVisibility = false;
        this.saveButtonVisibility = false;
        this.rejectButtonVisibility = true;
        this.excludeButtonVisibility = false;
        if (this.auth.current_user.is_staff) {
          this.acceptButtonVisibility = true;
        }
      } else if (this.notify.status.id == NotifyStatus.Editing) {
        this.saveButtonVisibility = true;
        this.sendForApprovalButtonVisibility = true;
        this.rejectButtonVisibility = false;
        this.acceptButtonVisibility = false;
        this.excludeButtonVisibility = false;
      } else if (this.notify.status.id == NotifyStatus.Approved) {
        this.saveButtonVisibility = false;
        this.sendForApprovalButtonVisibility = false;
        this.rejectButtonVisibility = false;
        this.acceptButtonVisibility = false;
        this.excludeButtonVisibility = false;
        if (this.auth.current_user.is_staff) {

          this.excludeButtonVisibility = true;
          this.saveButtonVisibility = true;
        }
      } else {
        this.sendForApprovalButtonVisibility = false;
        this.rejectButtonVisibility = false;
        this.acceptButtonVisibility = false;
        this.saveButtonVisibility = false;
        this.excludeButtonVisibility = false;
        if (this.auth.current_user.is_staff) {
          this.acceptButtonVisibility = true;
          this.saveButtonVisibility = true;
        }
      }
    }
  }

  ngOnInit() {

    this.route.params.subscribe((params: Params) => {

      this.id = params.id;
      if (this.id !== '0') {
        this.notifyService.retrieve(this.id).subscribe(res => {
            this.notify = res;
            this.clean_notify = JSON.parse(JSON.stringify(res));
            this.setPermissions(this.auth.current_user);
          }
        );
        if (this.auth.current_user.is_staff) {
          this.notifyService.getHistory(this.id).subscribe(res => {
            this.history = res;
          });
        }
      } else {
        const a = new Date();
        this.notify.date = `${a.getFullYear()}-${a.getMonth() + 1}-${a.getDate()}`;
        this.sendForApprovalButtonVisibility = true;
        this.saveButtonVisibility = true;
      }


    });
  }

  back() {
    if (this._location.getState()['navigationId'] > 1) {
      this._location.back();
    } else {
      this.router.navigate(['/pages/capital-repair-notifies']);
    }

  }

  onFormSubmit(e) {
    let is_form_valid = true;
    let is_credit_org_valid = true;
    let is_house_valid = true;
    if (e != SubmitType.Exclusion && !this.skip_verification) {
      is_form_valid = this.form.instance.validate().isValid;
      is_credit_org_valid = this.credit_organization_select.validate().isValid;
      is_house_valid = this.house_input.validate().isValid;
    }

    if (is_form_valid &&
      is_credit_org_valid &&
      is_house_valid) {
      switch (e) {
        case SubmitType.Sending: {
          this.notify.status.id = NotifyStatus.Approving;
          break;
        }
        case SubmitType.Rejecting: {
          this.notify.status.id = NotifyStatus.Editing;
          break;
        }
        case SubmitType.Accepting: {
          this.notify.status.id = NotifyStatus.Approved;
          break;
        }
        case SubmitType.Saving: {
          if (this.notify.status.id == 0) {
            this.notify.status.id = NotifyStatus.Editing;
          }
          break;
        }
        case SubmitType.Exclusion: {
          this.notify.status.id = NotifyStatus.Excluded;
          break;
        }
      }
      if (this.id != '0') {
        const n = getDifference(this.notify, this.clean_notify);
        if (n) {
          if (this.notify.files.length == 0) {
            n[0].files = 'empty';
          } else {
            n[0].files = this.notify.files;
          }
          this.notifyService.update(this.id, n[0]).subscribe(res => {
              notify({
                message: 'Форма сохранена',
                position: {
                  my: 'center top',
                  at: 'center top'
                }
              }, 'success', 3000);
              this.setPermissions(this.auth.current_user);
              this.clean_notify = JSON.parse(JSON.stringify(res));
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
        }
      } else {
        this.notifyService.create(this.notify).subscribe(res => {
            this.router.navigate([`/pages/capital-repair-notify/${res.id}`]);
          }
        );
      }
    } else {
      notify({
        message: 'Форма не сохранена.',
        position: {
          my: 'center top',
          at: 'center top'
        }
      }, 'error', 3000);
    }


  }

  onUploaded(e) {
    if (e.request.status == 201) {
      if (!this.notify.files) {
        this.notify.files = [];
      }
      const file = JSON.parse(e.request.response);
      console.log(file);
      this.notify.files.push(file);
    }
  }

  fileDelete(file) {
    const result = confirm('<i>Удалить файл?</i>', 'Подтверждение');
    result.then((dialogResult) => {
      if (dialogResult) {
        const index = this.notify.files.findIndex(f => f.id == file.id);
        if (index > -1) {
          this.notify.files.splice(index, 1);

        }
      }
    });

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
  {path: '', component: CapitalRepairNotifyComponent}
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    DxFileUploaderModule,
    HouseInputModule,
    OrganizationSelectModule,
    CreditOrganizationSelectModule,
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
    DxAccordionModule,
    ApplicationPipesModule
  ],
  declarations: [CapitalRepairNotifyComponent],
  exports: [CapitalRepairNotifyComponent]
})
export class CapitalRepairNotifyModule {
}
