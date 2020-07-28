import {Organization} from "./organization";

export interface User {
  username: string,
  organization?: Organization
  groups: number[]
}
