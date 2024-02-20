import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}


export function getPrettyTime(seconds: number): string {
  var SECOND_S = 1;
  var MINUTE_S = 60;
  var HOUR_S = 60 * MINUTE_S;
  var DAY_S = 24 * HOUR_S;
  var WEEK_S = 7 * DAY_S;
  var MONTH_S = 30 * DAY_S;
  var YEAR_S = 12 * MONTH_S;

  var lookup = ["year", "month", "week", "day", "hour", "minute", "second"];
  var values = [];
  values.push(seconds / YEAR_S); seconds %= YEAR_S;
  values.push(seconds / MONTH_S); seconds %= MONTH_S;
  values.push(seconds / WEEK_S); seconds %= WEEK_S;
  values.push(seconds / DAY_S); seconds %= DAY_S;
  values.push(seconds / HOUR_S); seconds %= HOUR_S;
  values.push(seconds / MINUTE_S); seconds %= MINUTE_S;
  values.push(seconds / SECOND_S); seconds %= SECOND_S;

  var pretty = ""; 
  for(var i=0 ; i <values.length; i++){
      var val = Math.round(values[i]);
      if(val <= 0) continue;

      const pluralEnding = val === 1 ? "" : "s"
      pretty += val + " " + lookup[i] + pluralEnding + " ago";
      break;
  }
  return pretty;
}


