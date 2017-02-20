import React from 'react';
import renderer from 'react-test-renderer';
import {browserHistory} from 'react-router'

import WorkflowList from '../WorkflowList';
import {mockAPI} from './mocks'

it('WorkflowList loading', () => {
  mockAPI([null]);
  const component = renderer.create(<WorkflowList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('WorkflowList failure', () => {
  mockAPI();
  const component = renderer.create(<WorkflowList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('WorkflowList success', () => {
  mockAPI([[{
    "id": 2,
    "current_version": 1,
    "current_version_id": 2,
    "task_count": 30,
    "schedule": null,
    "schedule_active": false,
    "versions": null,
    "name": "Big Ol' Workflow Example"
  }]]);
  const component = renderer.create(<WorkflowList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
