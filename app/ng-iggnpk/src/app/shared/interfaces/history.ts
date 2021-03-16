// tslint:disable:variable-name
export class HistoryDelta {
  field?: string;
  field_verbose?: string;
  new?: string;
  old?: string;

}
export class History {
  pk?: string;
  history_date?: string;
  history_type?: string;
  history_user?: string;
  history_user_id?: string;
  delta?: HistoryDelta;

}
