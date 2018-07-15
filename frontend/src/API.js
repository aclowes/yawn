import 'whatwg-fetch';

function getCsrfCookie() {
  return (document.cookie || '').split(';').reduce((accumulator, cookie) => {
    const index = cookie.indexOf('csrftoken=');
    if (index === 0) {
      accumulator += cookie.substr('csrftoken='.length);
    }
    return accumulator;
  }, '');
}

export function request(url, method, body, callback) {
  let response_obj;
  const headers = {
    'Accepts': 'application/json',
  };
  if (body) {
    // Request.mode = 'cors' (the default) provides some cross-origin protection
    headers['X-CSRFToken'] = getCsrfCookie();
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(body);
  }

  fetch(url, {
    method: method,
    credentials: 'include',
    headers, body
  }).then(function (response) {
    response_obj = response;
    if (response.headers.get('Content-Type') === 'application/json') {
      response.json().then(function (payload) {
        if (response_obj.ok) {
          if (payload && payload.hasOwnProperty('results')) {
            // list endpoint; return results and pagination information separately
            const results = payload.results;
            delete payload.results;
            callback(results, null, response_obj.status, payload);
          } else {
            callback(payload, null, response_obj.status);
          }
        } else {
          // the default rest framework error is in 'detail'
          callback(null, payload.detail || payload, response_obj.status);
        }
      })
    } else {
      // try getting the response text
      response_obj.text().then(function (error) {
        callback(null, error, response_obj.status);
      })
    }
  }).catch(function (error) {
    // if we can't connect, etc
    callback(null, error.message || error);
  })
}

export default class API {

  static get(url, callback) {
    request(url, 'GET', null, callback)
  }

  static post(url, body, callback) {
    request(url, 'POST', body, callback)
  }

  static patch(url, body, callback) {
    request(url, 'PATCH', body, callback)
  }

  static delete(url, body, callback) {
    request(url, 'DELETE', body, callback)
  }

};
