import API from '../API';

/*
 Mock fetch with a series of canned responses
 */
export function mockFetch(responses) {
  const fetch = jest.fn(
    (body, init) => {
      const response = responses.shift();
      if (response === undefined) {
        console.log('no more responses');
        return Promise.reject({message: 'no more responses'})
      }
      console.log('returning response ' + JSON.stringify(response));
      return Promise.resolve({
        ok: true,
        json: function () {
          console.log('returning json');
          return Promise.resolve(response)
        }
      })
    }
  );
  global.fetch = fetch;
  console.log('setup mockFetch');
}

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
    // just ignore the data
    API.get(url, callback);
  })
}
