import {Injectable} from "@angular/core";
import CustomStore from "devextreme/data/custom_store";
import {Observable} from "rxjs/internal/Observable";
import DevExpress from "devextreme";
import DataSource from "devextreme/data/data_source";


export declare interface Service {
    retrieve(param): Observable<any>;
    search(param): Observable<any>;
}


@Injectable({
  providedIn: 'root'
})
export class CustomStoreService {

  public static isNotEmpty(value) {
      return value !== undefined && value !== null && value !== "";
    }

  getSearchCustomStore(service: Service) {
    return new DataSource({
      key: "id",
      totalCount: function () {
        return 6
      },
      byKey: function (key) {
        if (key) {
          return service.retrieve(key).toPromise()
        }
      },
      load: function (loadOptions) {
        let params = "?";
        [
          "searchValue",
          "searchExpr",
          "take",
          "skip",
          "filter"
        ].forEach(function (i) {
          if (i in loadOptions && CustomStoreService.isNotEmpty(loadOptions[i]))
            params += `${i}=${JSON.stringify(loadOptions[i])}&`;
        });
        params = params.slice(0, -1);
        if (loadOptions.sort) {
          params += `&orderby=${loadOptions.sort[0].selector}`;
          if (loadOptions.sort[0].desc) {
            params += ' desc';
          }
        }
        return service.search(params).toPromise()
          .then((data: any) => {
            return {
              data: data.items,
              totalCount: data.totalCount
            };
          })
          .catch(error => {
            throw 'Data Loading Error'
          });
      }


    });
  }

}
