import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute, Params, Router} from "@angular/router";
import {CapitalRepairNotifyService, Notify} from "../../shared/services/capital-repair-notify.service";
import {Location} from '@angular/common';
import {DxFormComponent} from "devextreme-angular";
import {getDifference} from "../../shared/diff";
import notify from 'devextreme/ui/notify';
import {AuthService, UserGroup} from "../../shared/services";
import {CreditOrganizationSelectComponent, OrganizationSelectComponent} from "../../shared/components";
import {HouseInputComponent} from "../../shared/components/house-input/house-input.component";
import {environment} from "../../../environments/environment";
import {confirm} from 'devextreme/ui/dialog';

@Component({
  selector: 'app-capital-repair-notify',
  templateUrl: './capital-repair-notify.component.html',
  styleUrls: ['./capital-repair-notify.component.scss']
})
export class CapitalRepairNotifyComponent implements OnInit {
  SubmitType = SubmitType;
  @ViewChild("form", {static: false}) form: DxFormComponent;
  @ViewChild("credit_organization_select", {static: false}) credit_organization_select: CreditOrganizationSelectComponent;
  @ViewChild("house_input", {static: false}) house_input: HouseInputComponent;
  @ViewChild("organization_select", {static: false}) organization_select: OrganizationSelectComponent;

  get uploadAuthorization() {
    return 'Token ' + this.auth.token;
  };

  get uploadUrl() {
    return `${environment.file_url}create/`
  }

  id = '';
  notify: Notify = new Notify();
  clean_notify = new Notify();
  readOnly: any;
  acceptButtonVisibility = false;
  rejectButtonVisibility = false;
  sendForApprovalButtonVisibility = false;
  saveButtonVisibility = false;
  organizationSelectIsReadOnly = true;

  constructor(private route: ActivatedRoute,
              private router: Router,
              private notifyService: CapitalRepairNotifyService,
              private _location: Location,
              public auth: AuthService) {
  }


  setPermissions(user) {

    this.organizationSelectIsReadOnly = user.groups.indexOf(UserGroup.Admin) == -1;

    if (this.notify.organization.id == this.auth.current_user.organization.id || user.groups.indexOf(UserGroup.Admin) != -1) {
      if (this.notify.status.id == NotifyStatus.Approving) {
        this.acceptButtonVisibility = false;
        this.sendForApprovalButtonVisibility = false;
        this.saveButtonVisibility = false;
        this.rejectButtonVisibility = true;
        if (user.groups.indexOf(UserGroup.Admin) != -1) {
          this.acceptButtonVisibility = true;
        }
      }
      else if (this.notify.status.id == NotifyStatus.Editing) {
        this.saveButtonVisibility = true;
        this.sendForApprovalButtonVisibility = true;
        this.rejectButtonVisibility = false;
        this.acceptButtonVisibility = false;
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
        this.notifyService.retrieve(this.id).subscribe(res => {
            this.notify = res;
            this.clean_notify = JSON.parse(JSON.stringify(res));
            this.setPermissions(this.auth.current_user);
          }
        )
      }
      else {

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
      this.router.navigate(['/pages/capital-repair-notifies']);
    }

  }

  onFormSubmit(e) {
    const is_form_valid = this.form.instance.validate().isValid;
    const is_credit_org_valid = this.credit_organization_select.validate().isValid;
    const is_house_valid = this.house_input.validate().isValid;
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
          this.notify.status.id = NotifyStatus.Editing;
          break;
        }
      }
      if (this.id != '0') {
        let n = getDifference(this.notify, this.clean_notify);
        if (n) {
          if (this.notify.files.length==0){
            n[0].files = 'empty'
          }
          else {
            n[0].files = this.notify.files
          }
          this.notifyService.update(this.id, n[0]).subscribe(res => {
              notify({
                message: "Форма сохранена",
                position: {
                  my: "center top",
                  at: "center top"
                }
              }, "success", 3000);
              this.setPermissions(this.auth.current_user);
              this.clean_notify = JSON.parse(JSON.stringify(res));
            }
          );
        }
      }
      else {
        this.notifyService.create(this.notify).subscribe(res => {
            this.router.navigate([`/pages/capital-repair-notify/${res.id}`]);
          }
        );
      }
    }


  }

  onUploaded(e) {
    if (e.request.status == 201) {
      if (!this.notify.files) {
        this.notify.files = []
      }
      const file = JSON.parse(e.request.response);
      console.log(file);
      this.notify.files.push(file);
    }
  }

  fileDelete(file) {
    let result = confirm("<i>Удалить файл?</i>", "Подтверждение");
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
  Approved
}

enum SubmitType {
  Saving = 1,
  Sending,
  Rejecting,
  Accepting
}
