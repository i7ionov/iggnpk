import {Injectable} from '@angular/core';
import {ActivatedRouteSnapshot, CanActivate, Router} from '@angular/router';
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


  get currentUser(){
    if (this.current_user) {
      return this.current_user
    }
    else {
      this.getUserInfo().subscribe(res =>{
        this.current_user = res;
        return res;
      }, error1 => {
        localStorage.remove('token')
      })
    }

  }
  constructor(private router: Router, private http: HttpClient) {
  }

  getToken(login: string, password: string): Observable<any> {

    return this.http.post<any>(`${environment.backend_url}/api/v1/auth/token/login/`, {
      'username': login,
      'password': password
    })
  }

  getUserInfo(): Observable<any> {
    return this.http.get<any>(`${environment.backend_url}/api/v1/dict/users/me/`)
  }

}

@Injectable({providedIn: 'root'})
export class AuthGuardService implements CanActivate {
  constructor(private router: Router, private authService: AuthService) {
  }

  canActivate(route: ActivatedRouteSnapshot): boolean {
    const isLoggedIn = !!this.authService.token;
    const isLoginForm = route.routeConfig.path === 'login-form';
    if (isLoggedIn && isLoginForm) {
      this.router.navigate(['/']);
      return false;
    }

    if (!isLoggedIn && !isLoginForm) {
      this.router.navigate(['/login-form']);
    }

    return isLoggedIn || isLoginForm;
  }
}


@Injectable({providedIn: 'root'})
export class AuthInterceptor implements HttpInterceptor {
  constructor(private auth: AuthService) {
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (this.auth.token) {
      const cloned = req.clone({
        headers: req.headers.set('Authorization', "Token " + this.auth.token)
      });
      return next.handle(cloned);
    }
    else
    {
      return next.handle(req);
    }


  }

}
