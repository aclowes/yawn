import moment from "moment-timezone";

import API from '../API';

/*
* Set the timezone to UTC when running tests, for consistent
* snapshots.
* */
moment.tz.setDefault('UTC');
moment.tz.guess = (zone) => 'UTC';

/*
 Mock API with canned responses; it will call the callback
 immediately instead of waiting for a Promise. This means
 your component can populate the API response using setState
 during componentDidMount instead of afterwords.
 */
export function mockAPI(responses = []) {
  const availableResponses = responses;
  API.get = jest.fn((url, callback) => {
    let payload = availableResponses.shift();
    if (payload === undefined) {
      callback(null, 'some error message')
    } else if (payload && payload.hasOwnProperty('results')) {
      // list endpoint; return results and pagination information separately
      const results = payload.results;
      delete payload.results;
      callback(results, null, 200, payload)
    } else {
      callback(payload, null)
    }
  });
  API.post = API.patch = API.delete = jest.fn((url, data, callback) => {
    // just ignore the payload data
    API.get(url, callback);
  })
}
