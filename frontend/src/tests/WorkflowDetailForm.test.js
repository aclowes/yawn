import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import WorkflowDetailForm from '../WorkflowDetailForm';
import {mockAPI} from './mocks'
import API from "../API";

it('WorkflowDetailForm editable', () => {
  mockAPI([{versions: [1]}]);
  const workflow = {
      "id": 1,
      "name": "Simple Workflow Example",
      "name_id": 1,
      "version": 1,
      "schedule_active": false,
      "schedule": null,
      "next_run": null,
      "parameters": {"MY_OBJECT_ID": "1", "SOME_SETTING": "false"}
    };
  const component = ReactTestRenderer.create(<WorkflowDetailForm workflow={workflow}/>);
  component.getInstance().toggleEditable();
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('WorkflowDetailForm componentWillReceiveProps', () => {
  mockAPI([{versions: []}]);
  const workflow = {
      "id": 1,
      "name": "Simple Workflow Example",
      "name_id": 1,
      "version": 1,
      "schedule_active": false,
      "schedule": null,
      "next_run": null,
      "parameters": {"MY_OBJECT_ID": "1", "SOME_SETTING": "false"}
    };
  const component = ReactTestRenderer.create(<WorkflowDetailForm workflow={workflow}/>);
  const instance = component.getInstance();
  instance.setState = jest.fn();
  // same but different object
  instance.componentWillReceiveProps({workflow: {...workflow}});
  expect(instance.setState.mock.calls[0][0].parameters).toEqual('MY_OBJECT_ID=1\nSOME_SETTING=false');
});

it('WorkflowDetailForm submit', () => {
  mockAPI([{versions: []}]);
  const workflow = {
      "id": 1,
      "name": "Simple Workflow Example",
      "name_id": 1,
      "version": 1,
      "schedule_active": false,
      "schedule": null,
      "next_run": null,
      "parameters": {"MY_OBJECT_ID": "1", "SOME_SETTING": "false"}
    };
  const component = ReactTestRenderer.create(<WorkflowDetailForm workflow={workflow}/>);
  const instance = component.getInstance();
  instance.toggleEditable();
  const event = {preventDefault: jest.fn()};
  API.patch = jest.fn();
  instance.handleSubmit(event);
  expect(event.preventDefault).toBeCalled();
  // this does a roundtrip through formValues:
  expect(API.patch.mock.calls[0][1].parameters).toEqual(workflow.parameters);
});
