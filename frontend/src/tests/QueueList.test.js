import React from 'react';
import renderer from 'react-test-renderer';

import QueueList from '../QueueList';
import {mockAPI} from './mocks'

it('QueueList loading', () => {
  mockAPI([null]);
  const component = renderer.create(<QueueList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('QueueList failure', () => {
  mockAPI();
  const component = renderer.create(<QueueList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('QueueList success', () => {
  mockAPI([[{"id": 1, "message_count": 0, "name": "default"}]]);
  const component = renderer.create(<QueueList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
