import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import WorkflowList from '../WorkflowList';
import {mockAPI} from './mocks'

it('WorkflowList loading', () => {
  mockAPI([null]);
  const component = ReactTestRenderer.create(<WorkflowList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('WorkflowList failure', () => {
  mockAPI();
  const component = ReactTestRenderer.create(<WorkflowList />);
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
  const component = ReactTestRenderer.create(<WorkflowList />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
