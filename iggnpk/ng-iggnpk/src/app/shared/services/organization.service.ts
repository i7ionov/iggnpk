import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {environment} from "../../../environments/environment";
import {HttpClient} from "@angular/common/http";
import {Service} from "./custom-store.service";
import {Organization} from "../interfaces/organization";

export class Organizations {
  items: [];
  totalCount: number
}


@Injectable({
  providedIn: 'root'
})
export class OrganizationService implements Service{
  url = '/api/v1/dict/organizations';
  constructor(private http: HttpClient) {
  }

  retrieve(id): Observable<Organization>{
    return this.http.get<Organization>(`${environment.backend_url}${this.url}/${id}/`)
  }

  list(params): Observable<Organizations> {
    return this.http.get<Organizations>(`${environment.backend_url}${this.url}/search/${params}`)
  }

}
