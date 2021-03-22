import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {Service} from './custom-store.service';
import {Organization, OrganizationType} from '../interfaces/organization';


export class OrganizationTypes {
  items: [];
  totalCount: number;
}


@Injectable({
  providedIn: 'root'
})
export class OrganizationTypeService implements Service {
  url = '/api/v1/dict/organization_types';

  constructor(private http: HttpClient) {
  }

  retrieve(id): Observable<OrganizationType> {
    return this.http.get<OrganizationType>(`${environment.backend_url}${this.url}/${id}/`);
  }

  search(params): Observable<OrganizationTypes> {
    return this.http.get<OrganizationTypes>(`${environment.backend_url}${this.url}/${params}`);
  }


}
