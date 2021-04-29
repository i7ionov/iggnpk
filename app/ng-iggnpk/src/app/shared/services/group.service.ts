import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {environment} from "../../../environments/environment";
import {Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";
import {Address, Addresses} from "./addresses.service";
import {Service} from "./custom-store.service";
import {Organization} from "../interfaces/organization";
import {Notify} from "./capital-repair-notify.service";

export class Group {
  id: number;
  constructor() {
    this.id = 0;
  }
}

export class Groups {
  items: [];
  totalCount: number
}


@Injectable({
  providedIn: 'root'
})
export class GroupService implements Service {
  url = '/api/v1/dict/groups';

  constructor(private http: HttpClient) {
  }

  retrieve(id): Observable<Group> {
    return this.http.get<Group>(`${environment.backend_url}${this.url}/${id}/`)
  }

  list(params): Observable<Groups> {
    return this.http.get<Groups>(`${environment.backend_url}${this.url}/${params}`)
  }

  search(params): Observable<Groups> {
    return this.http.get<Groups>(`${environment.backend_url}${this.url}/${params}`)
  }

  update(id, house: any): Observable<Group> {
    return this.http.patch<Group>(`${environment.backend_url}${this.url}/${id}/`, house);
  }

  create(house: Group): Observable<Group> {
    return this.http.post<Group>(`${environment.backend_url}${this.url}/`, house);
  }



}
