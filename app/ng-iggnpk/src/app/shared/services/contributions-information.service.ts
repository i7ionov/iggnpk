import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {environment} from "../../../environments/environment";
import {Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";
import {House} from "./house.service";
import {Organization} from "../interfaces/organization";
import {CreditOrganization} from "./credit-organization.service";
import {Notify} from "./capital-repair-notify.service";
import {Organizations} from "./organization.service";

export class Status {
  id: number;
  text?: string;

  constructor() {
    this.id = 0;
  }

}

export class ContributionsInformation {
  id: number;
  date?: string;
  notify?: Notify;
  assessed_contributions_total?: number;
  assessed_contributions_current?: number;
  received_contributions_total?: number;
  received_contributions_current?: number;
  delta_total?: number;
  funds_spent?: number;
  credit?: number;
  funds_on_special_deposit?: number;
  fund_balance?: number;
  comment?: string;
  comment2?: string;
  status?: Status;
  files?: any[];
  mistakes?: any[];
  constructor() {
    this.id = 0;

    this.files = [];
    this.mistakes = [];
    this.status = new Status();
    this.notify = new Notify();
  }
}

export class ContributionsInformations {
  items: [];
  totalCount: number
}


@Injectable({
  providedIn: 'root'
})
export class ContributionsInformationService {
  url = '/api/v1/cr/contrib_info';

  constructor(private http: HttpClient) {
  }

  list(params): Observable<ContributionsInformation> {
    return this.http.get<ContributionsInformation>(`${environment.backend_url}${this.url}/${params}`)
  }

  retrieve(id): Observable<ContributionsInformation> {
    return this.http.get<ContributionsInformation>(`${environment.backend_url}${this.url}/${id}/`)
  }

  update(id, contrib_info: any): Observable<ContributionsInformation> {
    return this.http.patch<ContributionsInformation>(`${environment.backend_url}${this.url}/${id}/`, contrib_info)
  }

  create(contrib_info: ContributionsInformation): Observable<ContributionsInformation> {
    return this.http.post<ContributionsInformation>(`${environment.backend_url}${this.url}/`, contrib_info)
  }

  search(params): Observable<ContributionsInformation> {
    return this.http.get<ContributionsInformation>(`${environment.backend_url}${this.url}/${params}`)
  }

  generate_act(id): Observable<ContributionsInformation> {
    return this.http.get<ContributionsInformation>(`${environment.backend_url}${this.url}/generate_act/${id}/`)
  }

  exportToExcel(params): Observable<any> {
    return this.http.get<ContributionsInformation>(`${environment.backend_url}${this.url}/export_to_excel/${params}`);
  }

  getHistory(params): Observable<any> {
    return this.http.get<History>(`${environment.backend_url}${this.url}/${params}/get_history/`);
  }

}
