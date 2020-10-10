
function getContent(notify, mistakes){
  let options = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      timezone: 'UTC'
    };
    let now = new Date();
    let mistakes_text = '';
    mistakes.forEach(function (item, i, arr) {
      if (i > 0){
        mistakes_text = mistakes_text + ', ';
      }
      mistakes_text = mistakes_text + item.full_text;
      if (i > arr.length-2){
        mistakes_text = mistakes_text + '.';
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
    mistakes_text = mistakes_text.replace(new RegExp('{house}', 'g'), `${notify.house.address.city}, ${notify.house.address.street}, д. ${notify.house.number}`);
    mistakes_text = mistakes_text.replace(new RegExp('{reporting_quarter_date}', 'g'), reporting_quarter_date.toLocaleString("ru", options));
    mistakes_text = mistakes_text.replace(new RegExp('{last_reporting_date}', 'g'), last_reporting_date.toLocaleString("ru", options));

    let data = {
      date: now.toLocaleString("ru", options),
      notify: notify,
      mistakes_text: mistakes_text,
      reporting_quarter_date: reporting_quarter_date.toLocaleString("ru", options)
    }
    return data;
}
export { getContent }
