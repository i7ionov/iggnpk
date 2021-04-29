import { Component } from '@angular/core';
import {User} from "../../shared/interfaces/user";

@Component({
  templateUrl: 'profile.component.html',
  styleUrls: [ './profile.component.scss' ]
})

export class ProfileComponent {
  org: User = new User();

  constructor() {

  }
}
