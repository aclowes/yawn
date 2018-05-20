import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import WorkflowDetail from '../WorkflowDetail';
import {mockAPI} from './mocks'

it('WorkflowDetail loading', () => {
  mockAPI([null]);
  const component = ReactTestRenderer.create(<WorkflowDetail params={{id: 1}}/>);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('WorkflowDetail failure', () => {
  mockAPI();
  const component = ReactTestRenderer.create(<WorkflowDetail params={{id: 1}}/>);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('WorkflowDetail success', () => {
  mockAPI([
    {
      "id": 1,
      "name": "Simple Workflow Example",
      "name_id": 1,
      "tasks": [{
        "id": 1,
        "queue": "default",
        "upstream": [],
        "name": "start",
        "command": "echo Starting...",
        "max_retries": 0,
        "timeout": null
      }, {
        "id": 2,
        "queue": "default",
        "upstream": ["start"],
        "name": "task2",
        "command": "echo Working on $MY_OBJECT_ID",
        "max_retries": 0,
        "timeout": null
      }, {
        "id": 3,
        "queue": "default",
        "upstream": ["start"],
        "name": "task3",
        "command": "echo Another busy thing && sleep 20",
        "max_retries": 0,
        "timeout": null
      }, {
        "id": 4,
        "queue": "default",
        "upstream": ["task2", "task3"],
        "name": "done",
        "command": "echo Finished!",
        "max_retries": 0,
        "timeout": null
      }],
      "version": 1,
      "schedule_active": false,
      "schedule": null,
      "next_run": null,
      "parameters": {"MY_OBJECT_ID": "1", "SOME_SETTING": "false"}
    },
    // version list
    {
      "id": 1,
      "current_version": 1,
      "current_version_id": 1,
      "task_count": 4,
      "schedule": null,
      "schedule_active": false,
      "versions": [1],
      "name": "Simple Workflow Example"
    },
    // run history
    [{
      "id": 1,
      "tasks": [{
        "id": 1,
        "name": "start",
        "workflow": {"id": 1, "name": "Simple Workflow Example", "version": 1},
        "status": "succeeded"
      }, {
        "id": 2,
        "name": "task2",
        "workflow": {"id": 1, "name": "Simple Workflow Example", "version": 1},
        "status": "succeeded"
      }, {
        "id": 3,
        "name": "task3",
        "workflow": {"id": 1, "name": "Simple Workflow Example", "version": 1},
        "status": "succeeded"
      }, {
        "id": 4,
        "name": "done",
        "workflow": {"id": 1, "name": "Simple Workflow Example", "version": 1},
        "status": "succeeded"
      }],
      "workflow_id": 1,
      "submitted_time": "2017-01-22T20:53:36.548913Z",
      "scheduled_time": null,
      "status": "succeeded",
      "parameters": {"child": "true", "MY_OBJECT_ID": "1", "SOME_SETTING": "false"},
      "workflow": 1
    }]
  ]);
  const component = ReactTestRenderer.create(<WorkflowDetail params={{id: 1}}/>);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
