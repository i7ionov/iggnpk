import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {environment} from "../../../environments/environment";
import {Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";
import {Address, Addresses} from "./addresses.service";
import {Service} from "./custom-store.service";

export class House {
  id: number;
  number?: string;
  address?: Address;
  constructor() {
        this.id = 0;
        this.address = new Address()
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

  list(params): Observable<Houses> {
    return this.http.get<Houses>(`${environment.backend_url}${this.url}/${params}`)
  }


}
