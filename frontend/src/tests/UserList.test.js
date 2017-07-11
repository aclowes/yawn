import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import UserList from '../UserList';
import {mockAPI} from './mocks'

it('UserList loading', () => {
  mockAPI([null]);
  const component = ReactTestRenderer.create(<UserList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('UserList failure', () => {
  mockAPI();
  const component = ReactTestRenderer.create(<UserList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('UserList success', () => {
  mockAPI([[{
    "id": 4,
    "username": "tester",
    "email": "bob@smith.com",
    "api_token": "abcdef"
  }]]);
  const component = ReactTestRenderer.create(<UserList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
