import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import Login from '../Login';

it('Login renders', () => {
  const component = ReactTestRenderer.create(<Login />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
