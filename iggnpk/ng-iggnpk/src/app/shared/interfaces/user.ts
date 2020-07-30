import {Organization} from "./organization";

export interface User {
  username: string,
  email: string,
  password: string,
  re_password: string;
  organization?: Organization
  groups: number[]
}
