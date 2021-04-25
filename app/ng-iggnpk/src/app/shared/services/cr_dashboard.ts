import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {environment} from "../../../environments/environment";
import {Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";
import {Service} from "./custom-store.service";

const defaultDataSource = {
  "mkd_in_reg_program": {"total": 0, "tsj": 0, "jk": 0, "uk": 0, "ro": 0},
  "total_area": {"total": 0, "tsj": 0, "jk": 0, "uk": 0, "ro": 0},
  "last_year_funds_spent": {
    "total": 0,
    "tsj": 0,
    "jk": 0,
    "uk": 0,
    "ro": 0
  },
  "assessed_contributions_total": {
    "total": 0,
    "tsj": 0,
    "jk": 0,
    "uk": 0,
    "ro": 0
  },
  "received_contributions_total": {
    "total": 0,
    "tsj": 0,
    "jk": 0,
    "uk": 0,
    "ro": 0
  },
  "level_of_fundraising_total": {
    "total": 0,
    "tsj": 0,
    "jk": 0,
    "uk": 0,
    "ro": 0
  },
  "assessed_contributions_current": {
    "total": 0,
    "tsj": 0,
    "jk": 0,
    "uk": 0,
    "ro": 0
  },
  "received_contributions_current": {
    "total": 0,
    "tsj": 0,
    "jk": 0,
    "uk": 0,
    "ro": 0
  },
  "level_of_fundraising_current": {
    "total": 0,
    "tsj": 0,
    "jk": 0,
    "uk": 0,
    "ro": 0
  },
  "total_debt": {
    "total": 0,
    "tsj": 0,
    "jk": 0,
    "uk": 0,
    "ro": 0
  },
  "fund_balance_total": {
    "total": 0,
    "tsj": 0,
    "jk": 0,
    "uk": 0,
    "ro": 0
  },
  "fund_balance_total_and_current": {
    "total": 0,
    "tsj": 0,
    "jk": 0,
    "uk": 0,
    "ro": 0
  }
}

@Injectable({
  providedIn: 'root'
})
export class CrReportService {
  url = '/api/v1/cr/dashboard/cr_report';

  constructor(private http: HttpClient) {
  }

  default_report(){
    return defaultDataSource;
  }
  get(params): Observable<any> {
    return this.http.get<any>(`${environment.backend_url}${this.url}/${params}`)
  }

}


