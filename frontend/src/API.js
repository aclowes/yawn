import 'whatwg-fetch'

function getCsrfCookie() {
  return (document.cookie || '').split(';').reduce((accumulator, cookie) => {
    const index = cookie.indexOf('csrftoken=');
    if (index === 0) {
      accumulator += cookie.substr('csrftoken='.length);
    }
    return accumulator;
  }, '');
}

export default {

  generic(url, method, body, callback) {
    const headers = {
      'Accepts': 'application/json',
    };
    if (body) {
      // Request.mode = 'cors' provides some cross-origin protection
      headers['X-CSRFToken'] = getCsrfCookie();
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(body);
    }
    let responseObj;

    fetch(url, {
      method: method,
      headers, body
    }).then(function (response) {
      responseObj = response;
      return response.json()
    }).then(function (payload) {
      // if (payload === undefined) return;  // caught exception

      if (responseObj.status >= 200 && responseObj.status < 300) {
        // return the object list, a list endpoint
        callback(payload.results || payload, null);
      } else {
        callback(null, JSON.stringify(payload));
      }
    }).catch((error) => {
      callback(null, error.message);
    })
  },

  get(url, callback) {
    this.generic(url, 'GET', null, callback)
  },

  patch(url, body, callback) {
    this.generic(url, 'PATCH', body, callback)
  },

};