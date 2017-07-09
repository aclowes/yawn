import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import WorkerDetail from '../WorkerDetail';
import {mockAPI} from './mocks'

it('WorkerDetail loading', () => {
  mockAPI([null]);
  const component = ReactTestRenderer.create(<WorkerDetail params={{id: 1}}/>);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('WorkerDetail failure', () => {
  mockAPI();
  const component = ReactTestRenderer.create(<WorkerDetail params={{id: 1}}/>);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('WorkerDetail success', () => {
  mockAPI([
    // the worker
    {
      "id": 4,
      "name": "alec-graybeard.local 36470",
      "status": "exited",
      "start_timestamp": "2017-01-30T04:13:47.966080Z",
      "last_heartbeat": "2017-01-30T04:15:10.845289Z"
    },
    // executions
    [{
      "id": 16,
      "task": {
        "id": 12,
        "name": "done",
        "workflow": {"id": 1, "name": "Simple Workflow Example", "version": 1},
        "status": "succeeded"
      },
      "worker": {
        "id": 7,
        "name": "alec-graybeard.local 36561",
        "status": "exited",
        "start_timestamp": "2017-01-30T04:17:01.039091Z",
        "last_heartbeat": "2017-01-30T04:17:43.763294Z"
      },
      "status": "succeeded",
      "start_timestamp": "2017-01-30T04:17:03.806599Z",
      "minutes_running": null
    }]
  ]);
  const component = ReactTestRenderer.create(<WorkerDetail params={{id: 1}}/>);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
