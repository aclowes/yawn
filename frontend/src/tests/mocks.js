import API from '../API';

/*
 Mock API with canned responses; it will call the callback
 immediately instead of waiting for a Promise. This means
 your component can populate the API response using setState
 during componentDidMount instead of afterwords.
 */
export function mockAPI(responses = []) {
  const availableResponses = responses;
  API.get = jest.fn((url, callback) => {
    let response = availableResponses.shift();
    if (response === undefined) {
      callback(null, 'some error message')
    } else {
      callback(response, null)
    }
  });
  API.patch = API.delete = jest.fn((url, data, callback) => {
    // just ignore the payload data
    API.get(url, callback);
  })
}
