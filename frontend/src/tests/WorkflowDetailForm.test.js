import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import WorkflowDetailForm from '../WorkflowDetailForm';
import {mockAPI} from './mocks'

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
