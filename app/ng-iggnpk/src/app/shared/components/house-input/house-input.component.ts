import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  forwardRef,
  Input,
  NgModule,
  OnInit,
  Output, QueryList, ViewChild, ViewChildren
} from '@angular/core';
import {
  DxAutocompleteComponent,
  DxAutocompleteModule,
  DxDataGridModule,
  DxDropDownBoxModule, DxFormComponent,
  DxFormModule,
  DxSelectBoxModule
} from "devextreme-angular";
import {House, HousesService} from "../../services/house.service";
import {Address, AddressService} from "../../services/addresses.service";
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from "@angular/forms";
import CustomStore from "devextreme/data/custom_store";
import {CommonModule} from "@angular/common";
import DevExpress from "devextreme";
import add = DevExpress.viz.map.projection.add;
import {CustomStoreService} from "../../services/custom-store.service";
import {Organization} from "../../interfaces/organization";
import {DxValidatorModule} from 'devextreme-angular/ui/validator';
import DataSource from "devextreme/data/data_source";

@Component({
  selector: 'app-house-input',
  templateUrl: './house-input.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrls: ['./house-input.component.scss'],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => HouseInputComponent),
      multi: true
    }
  ]
})
export class HouseInputComponent implements OnInit {
  @ViewChild('houseAutocomplete', {static: false}) houseAutocomplete: DxAutocompleteComponent;
  @ViewChild("form", {static: false}) form: DxFormComponent;
  ds: any;


  _value: House = new House();
  get value() {
    return this._value;
  }

  @Output() valueChange = new EventEmitter<Organization>();

  @Input() set value(val) {
    if (val !== undefined && val !== null) {
      this._value = val;
      this.valueChange.emit(this._value);
    }
    else {
      setTimeout(() => {
        this._value = new House();
        this.valueChange.emit(this._value);
      });

    }

  }

  addresses: any = {};
  houses: any = {};

  displayExpr(item) {
    // "item" can be null
    return item && `${item.area} ${item.city} ${item.street}`;
  }

  constructor(private houseService: HousesService, private addressService: AddressService, private customStoreService: CustomStoreService) {


    this.addresses = customStoreService.getSearchCustomStore(addressService);

    this.houses = customStoreService.getSearchCustomStore(houseService);

  }

  ngOnInit() {
  }


  addressChange(addr) {
    let temp = this.value;
    temp.address = addr;
    this.value = temp;
    this.houses.filter(['address_id', '=', addr.id]);
    this.houses.load();


  }

  houseChange(house) {
    let temp = this.value;
    temp.number = house;
    this.value = temp;
    this.houseService.find(this.value.address.id, house).subscribe(res=>{
      this.value.organization=res.organization
    })
  }

  public validate() {
    return (this.form.instance.validate());
  }

  isNotNull(e) {
    return e.value && e.value.id > 0;
  }
}

@NgModule({
  declarations: [HouseInputComponent],
  exports: [HouseInputComponent],
  imports: [DxSelectBoxModule, DxFormModule, DxAutocompleteModule, CommonModule, DxValidatorModule]
})
export class HouseInputModule {
}
