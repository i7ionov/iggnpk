import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {environment} from "../../../environments/environment";
import {Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";
import {Service} from "./custom-store.service";

export class CreditOrganization {
  id: number;
  name?: string;
  inn?: string;

  constructor() {
    this.id = 0;
  }
}

export class CreditOrganizations {
  items: [];
  totalCount: number
}

export class Branch {
  id: number;
  credit_organization?: CreditOrganization;
  address?: string;
  bik?: string;
  correspondent_account?: string;
  kpp?: string;

  constructor() {
    this.id = 0;
    this.credit_organization = new CreditOrganization()
  }
}

export class Branches {
  items: [];
  totalCount: number
}

@Injectable({
  providedIn: 'root'
})
export class CreditOrganizationService implements Service {
  url = '/api/v1/cr/credit_organizations';

  constructor(private http: HttpClient) {
  }


  retrieve(id): Observable<CreditOrganization> {
    return this.http.get<CreditOrganization>(`${environment.backend_url}${this.url}/${id}/`)
  }

  list(params): Observable<CreditOrganizations> {
    return this.http.get<CreditOrganizations>(`${environment.backend_url}${this.url}/search/${params}`)
  }

}


@Injectable({
  providedIn: 'root'
})
export class BranchService {
  url = '/api/v1/cr/branches';

  constructor(private http: HttpClient) {
  }

  retrieve(id): Observable<CreditOrganization> {
    return this.http.get<CreditOrganization>(`${environment.backend_url}${this.url}/${id}/`)
  }

  list(params): Observable<CreditOrganizations> {
    return this.http.get<CreditOrganizations>(`${environment.backend_url}${this.url}/search/${params}`)
  }

}
