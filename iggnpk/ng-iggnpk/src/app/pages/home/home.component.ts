import {Component, OnInit} from '@angular/core';
import {AuthService} from "../../shared/services";


@Component({
  templateUrl: 'home.component.html',
  styleUrls: [ './home.component.scss' ]
})

export class HomeComponent implements OnInit{
  constructor(private auth: AuthService) {}

  click() {

  }

  ngOnInit(): void {
  }
}
