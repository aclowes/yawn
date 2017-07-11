import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import ExecutionList from '../ExecutionList';
import {mockAPI} from './mocks'

it('ExecutionList loading', () => {
  mockAPI([null]);
  const component = ReactTestRenderer.create(<ExecutionList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('ExecutionList failure', () => {
  mockAPI();
  const component = ReactTestRenderer.create(<ExecutionList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('ExecutionList success', () => {
  mockAPI([[{
    "id": 17,
    "task": {
      "id": 12,
      "name": "done",
      "workflow": {"id": 1, "name": "Simple Workflow Example", "version": 1},
      "status": "succeeded"
    },
    "worker": {
      "id": 8,
      "name": "graybeard.local 36594",
      "status": "exited",
      "start_timestamp": "2017-01-30T04:17:44.837597Z",
      "last_heartbeat": "2017-02-02T20:10:06.107192Z"
    },
    "status": "succeeded",
    "start_timestamp": "2017-01-30T04:17:47.008524Z",
    "minutes_running": "0m 0.05s"
  }]]);
  const component = ReactTestRenderer.create(<ExecutionList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
