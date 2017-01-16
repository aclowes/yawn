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

export default {

  generic(url, method, body, callback) {
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
      headers, body

    }).then(function (response) {
      if (response.ok) {
        response.json().then((payload) => {
          // return the object list if response.results is defined:
          callback(payload.results || payload, null);
        });
      } else {
        response.text().then((error) => {
          // todo figure out the rest framework error json and parse it if possible
          callback(null, error);
        });
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