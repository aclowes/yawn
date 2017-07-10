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
    "name": "alec-graybeard.local 36470",
    "status": "exited",
    "start_timestamp": "2017-01-30T04:13:47.966080Z",
    "last_heartbeat": "2017-01-30T04:15:10.845289Z"
  }]]);
  const component = ReactTestRenderer.create(<UserList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
