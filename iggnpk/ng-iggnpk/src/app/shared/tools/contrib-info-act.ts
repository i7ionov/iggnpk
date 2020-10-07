import {ContributionsInformation} from "../services/contributions-information.service";

function getContent(contrib_info: ContributionsInformation){
  let options = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      timezone: 'UTC'
    };
    let now = new Date();
    let mistakes = '';
    contrib_info.mistakes.forEach(function (item, i, arr) {
      if (i > 0){
        mistakes = mistakes + ', ';
      }
      mistakes = mistakes + item.full_text;
      if (i > arr.length-2){
        mistakes = mistakes + '.';
      }
    });
    let reporting_quarter_date;
    let last_reporting_date;
    let last_reporting_date1 = new Date(now.getFullYear(), 0, 1);
    let last_reporting_date2 = new Date(now.getFullYear(), 3, 1);
    let last_reporting_date3 = new Date(now.getFullYear(), 6, 1);
    let last_reporting_date4 = new Date(now.getFullYear(), 9, 1);
    if(now < last_reporting_date1){
      reporting_quarter_date = new Date(last_reporting_date1.getFullYear()-1, last_reporting_date1.getMonth()-1, 20);
      last_reporting_date = last_reporting_date1;
    }
    else if(now < last_reporting_date2){
      reporting_quarter_date = new Date(last_reporting_date2.getFullYear(), last_reporting_date2.getMonth()-1, 20);
      last_reporting_date = last_reporting_date2;
    }
    else if(now < last_reporting_date3){
      reporting_quarter_date = new Date(last_reporting_date3.getFullYear(), last_reporting_date3.getMonth()-1, 20);
      last_reporting_date = last_reporting_date3;
    }
    else {
      reporting_quarter_date = new Date(last_reporting_date4.getFullYear(), last_reporting_date4.getMonth()-1, 20);
      last_reporting_date = last_reporting_date4;
    }
    mistakes = mistakes.replace(new RegExp('{house}', 'g'), `${contrib_info.notify.house.address.city}, ${contrib_info.notify.house.address.street}, д. ${contrib_info.notify.house.number}`);
    mistakes = mistakes.replace(new RegExp('{reporting_quarter_date}', 'g'), reporting_quarter_date.toLocaleString("ru", options));
    mistakes = mistakes.replace(new RegExp('{last_reporting_date}', 'g'), last_reporting_date.toLocaleString("ru", options));

    let data = {
      date: now.toLocaleString("ru", options),
      org: contrib_info.notify.organization,
      mistakes: mistakes
    }
    return data;
}
export { getContent }
