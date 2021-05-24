import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {environment} from "../../../environments/environment";
import {HttpClient} from "@angular/common/http";
import {User} from "../interfaces/user";
import {Notify} from "./capital-repair-notify.service";
import {Organization} from "../interfaces/organization";
import {Organizations} from "./organization.service";


export class Users {
  items: [];
  totalCount: number
}


@Injectable({
  providedIn: 'root'
})
export class UserService {
  url = '/api/v1/dict/users';

  constructor(private http: HttpClient) {
  }

  retrieve(id): Observable<User> {
    return this.http.get<User>(`${environment.backend_url}${this.url}/${id}/`);
  }

  create(user: User): Observable<User> {
    return this.http.post<User>(`${environment.backend_url}${this.url}/`, user);
  }

  list(params): Observable<User> {
    return this.http.get<User>(`${environment.backend_url}${this.url}/${params}`);
  }

  search(params): Observable<User> {
    return this.http.get<User>(`${environment.backend_url}${this.url}/${params}`);
  }

  me(params): Observable<User> {
    return this.http.get<User>(`${environment.backend_url}${this.url}/me/`);
  }

  update(id, user: any, sendmail = false): Observable<User> {
    return this.http.patch<User>(`${environment.backend_url}${this.url}/${id}/?sendmail=${sendmail}`, user)
  }

  getOrgUserCount(inn): Observable<any> {
    return this.http.get<any>(`${environment.backend_url}${this.url}/org_users_count/?inn=${inn}`)
  }

  getEmailIsUsed(email): Observable<any> {
    return this.http.get<any>(`${environment.backend_url}${this.url}/is_email_already_used/?email=${email}`)
  }

  getUsernameIsUsed(username): Observable<any> {
    return this.http.get<any>(`${environment.backend_url}${this.url}/is_username_already_used/?username=${username}`)
  }

  register(user: User): Observable<User> {
    return this.http.post<User>(`${environment.backend_url}${this.url}/register/`, user);
  }

}
