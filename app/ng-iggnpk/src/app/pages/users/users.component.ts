import {AfterContentInit, AfterViewInit, Component, NgModule, OnInit, ViewChild} from '@angular/core';
import {DxCheckBoxModule} from "devextreme-angular/ui/check-box";
import {DxTextBoxModule} from "devextreme-angular/ui/text-box";
import {Router, RouterModule, Routes} from "@angular/router";
import {CommonModule} from "@angular/common";
import {DxValidatorModule} from "devextreme-angular/ui/validator";
import {DxValidationGroupModule} from "devextreme-angular/ui/validation-group";
import {DxPopupModule, DxButtonModule, DxTemplateModule, DxDataGridComponent} from 'devextreme-angular';

import {DxDataGridModule} from 'devextreme-angular';

import CustomStore from 'devextreme/data/custom_store';

import {UserService} from "../../shared/services/user.service";
import {User} from 'src/app/shared/interfaces/user';
import {confirm} from 'devextreme/ui/dialog';
import {CapitalRepairNotifyComponent} from "../capital-repair-notify/capital-repair-notify.component";
import {CustomStoreService} from "../../shared/services/custom-store.service";

@Component({
  selector: 'app-users',
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.scss']
})
export class UsersComponent implements OnInit {
  @ViewChild(DxDataGridComponent, {static: false}) dataGrid: DxDataGridComponent;
  dataSource: any = {};
  currentFilter: any;

  constructor(private userService: UserService, private router: Router, private customStoreService: CustomStoreService) {
    this.dataSource = customStoreService.getListCustomStore(userService);
  }

  ngOnInit() {

  }

  refreshDataGrid() {
    this.dataGrid.instance.refresh();
  }

  onToolbarPreparing(e) {
    e.toolbarOptions.items.unshift({
      location: 'before',
      widget: 'dxButton',
      options: {
        width: 200,
        text: 'Новая запись',
        onClick: this.add.bind(this)
      }
    })

    e.toolbarOptions.items.unshift({
      location: 'after',
      widget: 'dxButton',
      options: {
        icon: 'refresh',
        onClick: this.refreshDataGrid.bind(this)
      }
    })


  }

  add() {
    this.router.navigate(['/pages/users/0']);
  }

  userActivityChange($event: boolean, cell: any) {
    let result = confirm("<i>Отправить электронное письмо об активации/деактивации учетной записи?</i>", "Уведомление");
    result.then((dialogResult) => {
      this.userService.update(cell.key, {id: cell.key, is_active: $event, sendmail:dialogResult}).subscribe();
    });

  }

}

const routes: Routes = [
  {path: '', component: UsersComponent}
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    DxButtonModule,
    DxCheckBoxModule,
    DxTextBoxModule,
    DxValidatorModule,
    DxValidationGroupModule,
    DxPopupModule,
    DxTemplateModule,
    DxDataGridModule
  ],
  declarations: [UsersComponent],
  exports: [UsersComponent]
})
export class UsersModule {
}
