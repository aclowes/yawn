import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import UserDetail from '../UserDetail';
import {mockAPI} from './mocks'

it('UserDetail success', () => {
  mockAPI([{
    "id": 4,
    "username": "tester",
    "email": "bob@smith.com",
    "api_token": "abcdef"
  }]);
  const component = ReactTestRenderer.create(<UserDetail params={{id: 1}}/>);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
