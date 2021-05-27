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

export class ContributionsInformationMistake {
  id: number;
  text?: string;

  constructor() {
    this.id = 0;
  }

}


export class ContributionsInformationMistakes {
  items: [];
  totalCount: number
}


@Injectable({
  providedIn: 'root'
})
export class ContributionsInformationMistakeService {
  public url = '/api/v1/cr/contrib_info_mistake';

  constructor(private http: HttpClient) {
  }

  list(params): Observable<ContributionsInformationMistake> {
    return this.http.get<ContributionsInformationMistake>(`${environment.backend_url}${this.url}/${params}`)
  }

  retrieve(id): Observable<ContributionsInformationMistake> {
    return this.http.get<ContributionsInformationMistake>(`${environment.backend_url}${this.url}/${id}/`)
  }

  search(params): Observable<ContributionsInformationMistake> {
    return this.http.get<ContributionsInformationMistake>(`${environment.backend_url}${this.url}/${params}`)
  }

}
