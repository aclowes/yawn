import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import TaskDetail from '../TaskDetail';
import {mockAPI} from './mocks'

it('TaskDetail loading', () => {
  mockAPI([null]);
  const component = ReactTestRenderer.create(<TaskDetail params={{id: 1}}/>);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('TaskDetail failure', () => {
  mockAPI();
  const component = ReactTestRenderer.create(<TaskDetail params={{id: 1}}/>);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('TaskDetail success', () => {
  mockAPI([
    {
      "id": 1,
      "name": "start",
      "workflow": {"id": 1, "name": "Simple Workflow Example", "version": 1},
      "executions": [{
        "id": 1,
        "worker": {
          "id": 1,
          "name": "graybeard.local 35405",
          "status": "exited",
          "start_timestamp": "2017-01-30T03:26:38.197807Z",
          "last_heartbeat": "2017-01-30T03:44:38.063205Z"
        },
        "status": "succeeded",
        "start_timestamp": "2017-01-30T03:26:38.211839Z",
        "stop_timestamp": null,
        "exit_code": null,
        "stdout": "Starting...\n",
        "stderr": ""
      }],
      "messages": [],
      "max_retries": 0,
      "timeout": null,
      "command": "echo Starting...",
      "status": "succeeded"
    }
  ]);
  const component = ReactTestRenderer.create(<TaskDetail params={{id: 1}}/>);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
