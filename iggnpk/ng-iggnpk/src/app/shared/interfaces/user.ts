import {Organization} from "./organization";

export interface Permission {
  id: number
  codename: string,
}
export interface User {
  username: string,
  email: string,
  password: string,
  re_password: string;
  organization?: Organization
  groups: number[],
  permissions?: Permission[]
}
