import {Organization} from "./organization";

export interface Permission {
  id: number
  codename: string,
}
export class User {
  id?: number;
  is_active?: boolean;
  is_staff?: boolean;
  username?: string;
  email?: string;
  password?: string;
  re_password?: string;
  organization?: Organization
  groups?: number[];
  permissions?: Permission[]
}
