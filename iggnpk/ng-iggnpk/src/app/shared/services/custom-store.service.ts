import {Injectable} from "@angular/core";
import CustomStore from "devextreme/data/custom_store";
import {Observable} from "rxjs/internal/Observable";


export declare interface Service {
    list(param): Observable<any>;
    retrieve(param): Observable<any>;
}


@Injectable({
  providedIn: 'root'
})
export class CustomStoreService {

  public static isNotEmpty(value) {
      return value !== undefined && value !== null && value !== "";
    }

  getSearchCustomStore(service: Service){
    return new CustomStore({
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
        return service.list(params).toPromise()
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
