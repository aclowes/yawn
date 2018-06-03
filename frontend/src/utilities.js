import moment from "moment/moment";

export function formatDateTime(datetime) {
  if (!datetime) {
    return '';
  }
  return moment(datetime).format('MMMM Do YYYY, h:mm:ss a');
}
