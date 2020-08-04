import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {environment} from "../../../environments/environment";
import {HttpClient} from "@angular/common/http";
import {User} from "../interfaces/user";
import {Notify} from "./capital-repair-notify.service";


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

  getUsers(params): Observable<Users> {
    return this.http.get<Users>(`${environment.backend_url}${this.url}${params}/`)
  }

  retrieve(id): Observable<User> {
    return this.http.get<User>(`${environment.backend_url}${this.url}/${id}/`)
  }

  update(id, user: any): Observable<User> {
    return this.http.post<User>(`${environment.backend_url}${this.url}/save/${id}/`, user)
  }


}
