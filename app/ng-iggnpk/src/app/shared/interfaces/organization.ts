export class OrganizationType {
  id: number;
  text?: string;
  constructor() {
    this.id = 0;
  }
}

export class Organization {
  id: number;
  name?: string;
  inn?: string;
  ogrn?: string;
  type?: OrganizationType;
  constructor() {
    this.id = 0;
  }
}
