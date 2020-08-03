import {Component, NgModule, OnInit} from '@angular/core';
import {AuthGuardService, AuthService} from "../../shared/services";



@Component({
  templateUrl: 'root-layout.component.html',
  styleUrls: [ './root-layout.component.scss' ]
})

export class RootLayoutComponent implements OnInit{
  constructor(private auth: AuthService) {}

  click() {

  }

  ngOnInit(): void {
    console.log('root')
  }
}
