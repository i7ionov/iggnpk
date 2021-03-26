import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {environment} from "../../../environments/environment";
import {Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";
import {Address, Addresses} from "./addresses.service";
import {Service} from "./custom-store.service";
import {Organization} from "../interfaces/organization";

export class House {
  id: number;
  number?: string;
  included_in_the_regional_program?: boolean;
  address?: Address;
  organization?:Organization;
  constructor() {
        this.id = 0;
        this.address = new Address();
        this.organization = new Organization();
    }
}
export class Houses {
  items: [];
  totalCount: number
}


@Injectable({
  providedIn: 'root'
})
export class HousesService implements Service {
  url = '/api/v1/dict/houses';
  constructor(private http: HttpClient) {
  }

  retrieve(id): Observable<House>{
    return this.http.get<House>(`${environment.backend_url}${this.url}/${id}/`)
  }
  find(address_id, number): Observable<House>{
    return this.http.get<House>(`${environment.backend_url}${this.url}/find/?address_id=${address_id}&number=${number}`)
  }
  list(params): Observable<Houses> {
    return this.http.get<Houses>(`${environment.backend_url}${this.url}/${params}`)
  }
  search(params): Observable<Houses> {
    return this.http.get<Houses>(`${environment.backend_url}${this.url}/${params}`)
  }

}
