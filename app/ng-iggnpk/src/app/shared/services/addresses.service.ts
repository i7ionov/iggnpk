import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {environment} from "../../../environments/environment";
import {Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";
import {Service} from "./custom-store.service";
import {Organization} from "../interfaces/organization";

export class Address {
  id: number;
  area?: string;
  place?: string;
  city?: string;
  street?: string;
  constructor() {
        this.id = 0;
    }
}
export class Addresses {
  items: [];
  totalCount: number
}


@Injectable({
  providedIn: 'root'
})
export class AddressService implements Service {
  url = '/api/v1/dict/addresses';
  constructor(private http: HttpClient) {
  }

  retrieve(id): Observable<Address>{
    return this.http.get<Address>(`${environment.backend_url}${this.url}/${id}/`)
  }

  search(params): Observable<Addresses> {
    return this.http.get<Addresses>(`${environment.backend_url}${this.url}/${params}`)
  }

  update(id, addr: any): Observable<Address> {
    return this.http.patch<Address>(`${environment.backend_url}${this.url}/${id}/`, addr);
  }

  create(addr: Address): Observable<Address> {
    return this.http.post<Address>(`${environment.backend_url}${this.url}/`, addr);
  }

}
