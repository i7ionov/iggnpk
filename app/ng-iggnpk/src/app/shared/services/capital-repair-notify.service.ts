import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {environment} from "../../../environments/environment";
import {Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";
import {House} from "./house.service";
import {Organization} from "../interfaces/organization";
import {CreditOrganization} from "./credit-organization.service";
import {Organizations} from "./organization.service";

export class NotifyStatus {
  id: number;
  text?: string;
  constructor() {
    this.id = 0;
  }

}

export class Notify {
  id: number;
  date?: string;
  house?: House;
  organization?: Organization;
  bank?: CreditOrganization;
  account_number?: string;
  account_opening_date?: string;
  monthly_contribution_amount?: number;
  protocol_details?: string;
  comment?: string;
  status?: NotifyStatus;
  files?:any[];
  constructor() {
    this.id = 0;
    this.house = new House();
    this.organization = new Organization();
    this.bank = new CreditOrganization();
    this.files = [];
    this.status = new NotifyStatus();
  }
}

export class Notifies {
  items: [];
  totalCount: number
}


@Injectable({
  providedIn: 'root'
})
export class CapitalRepairNotifyService {
  url = '/api/v1/cr/notifies';

  constructor(private http: HttpClient) {
  }

  getNotifies(params): Observable<Notifies> {
    return this.http.get<Notifies>(`${environment.backend_url}${this.url}/${params}`)
  }

  retrieve(id): Observable<Notify> {
    return this.http.get<Notify>(`${environment.backend_url}${this.url}/${id}/`)
  }

  update(id, notify: any): Observable<Notify> {
    return this.http.patch<Notify>(`${environment.backend_url}${this.url}/${id}/`, notify)
  }

  create(notify: Notify): Observable<Notify> {
    return this.http.post<Notify>(`${environment.backend_url}${this.url}/`, notify)
  }

  search(params): Observable<Notify> {
    return this.http.get<Notify>(`${environment.backend_url}${this.url}/${params}`)
  }

  generateActs(params): Observable<any> {
    return this.http.get<Notify>(`${environment.backend_url}${this.url}/generate_acts/${params}`)
  }

}
