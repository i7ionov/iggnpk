import {Injectable} from '@angular/core';
import {ActivatedRouteSnapshot, CanActivate, CanLoad, Route, Router} from '@angular/router';
import {HttpClient, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from "../../../environments/environment";
import {User} from "../interfaces/user";

@Injectable()
export class AuthService {
  current_user: User;

  public get token() {
    return localStorage.getItem('token')
  }


  constructor(private router: Router, private http: HttpClient) {
  }

  getToken(login: string, password: string): Observable<any> {

    return this.http.post<any>(`${environment.backend_url}/api/v1/auth/token/login/`, {
      'username': login,
      'password': password
    })
  }

  createUser(user: User): Observable<User> {
    return this.http.post<any>(`${environment.backend_url}/api/v1/dict/users/create/`, user)
  }

  getOrgUserCount(inn): Observable<any> {
    return this.http.get<any>(`${environment.backend_url}/api/v1/dict/org_users_count/?inn=${inn}`)
  }

  getEmailIsUsed(email): Observable<any> {
    return this.http.get<any>(`${environment.backend_url}/api/v1/dict/is_email_already_used/?email=${email}`)
  }

  getUserInfo(): Observable<any> {
    return this.http.get<any>(`${environment.backend_url}/api/v1/dict/users/me/`)
  }

}

@Injectable({providedIn: 'root'})
export class AuthGuardService implements CanActivate {
  constructor(private router: Router, private authService: AuthService) {
  }

  canActivate(route: ActivatedRouteSnapshot): boolean | Observable<boolean> | Promise<boolean> {
    let promise: Promise<boolean> = new Promise((resolve, reject) => {
      if (this.authService.current_user) {
        resolve(true);
      }
      else {
        this.authService.getUserInfo().subscribe(user => {
          if (user.id) {
            this.authService.current_user = user;
            resolve(true);
          }
          else {
            resolve(false);
            this.router.navigate(['auth/login-form']);
          }
        }, error1 => {
          resolve(false);
          this.router.navigate(['auth/login-form']);
        })
      }


    });
    return promise;
  }

}

@Injectable({providedIn: 'root'})
export class AuthInterceptor
  implements HttpInterceptor {
  constructor(private auth: AuthService) {
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (this.auth.token) {
      const cloned = req.clone({
        headers: req.headers.set('Authorization', "Token " + this.auth.token)
      });
      return next.handle(cloned);
    } else {
      return next.handle(req);
    }


  }

}
