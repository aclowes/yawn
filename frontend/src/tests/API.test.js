import API from '../API';

it('API request success', () => {
  // setup mock fetch and callback
  const response = {payload: 1};
  global.fetch = jest.fn(
    (url, init) => {
      return Promise.resolve({
        ok: true,
        status: 200,
        headers: {
          'get': function () {
            return 'application/json'
          }
        },
        json: function () {
          return Promise.resolve(response)
        }
      })
    });
  const callback = jest.fn((payload, error, status) => {
    expect(payload).toEqual(response);
    expect(status).toEqual(200);
  });

  // call the api method
  API.request('/url/', 'POST', {a: 1}, callback);
});

it('API backend failure', () => {
  // setup mock fetch and callback
  const response = 'error message';
  global.fetch = jest.fn(
    (url, init) => {
      return Promise.resolve({
        ok: true,
        status: 200,
        headers: {
          'get': function () {
            return 'text'
          }
        },
        text: function () {
          return Promise.resolve(response)
        }
      })
    });
  const callback = jest.fn((payload, error, status) => {
    expect(error).toEqual(response);
    expect(status).toEqual(200);
  });

  // call the api method
  API.request('/url/', 'POST', {a: 1}, callback);
});

it('API http failure', () => {
  // setup mock fetch and callback
  const response = 'bad request';
  global.fetch = jest.fn(
    (url, init) => {
      return Promise.reject({
        message: response
      })
    });
  const callback = jest.fn((payload, error, status) => {
    expect(error).toEqual(error);
  });

  // call the api method
  API.request('/url/', 'POST', {a: 1}, callback);
});

it('API request success on list endpoint', () => {
  // setup mock fetch and callback
  const response = {results: [1, 2], page: 1};
  global.fetch = jest.fn(
    (url, init) => {
      return Promise.resolve({
        ok: true,
        status: 200,
        headers: {
          'get': function () {
            return 'application/json'
          }
        },
        json: function () {
          return Promise.resolve(response)
        }
      })
    });
  const callback = jest.fn((payload, error, status, pagination) => {
    expect(payload).toEqual([1, 2]);
    expect(pagination).toEqual({page: 1});
  });

  // call the api method
  API.request('/url/', 'GET', {a: 1}, callback);
});

it('API calls are passed on', () => {
  API.request = jest.fn();
  API.get();
  API.post();
  API.patch();
  API.delete();
  expect(API.request.mock.calls.length).toBe(4);
});
