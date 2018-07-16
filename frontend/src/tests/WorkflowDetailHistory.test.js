import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import WorkflowDetailHistory from '../WorkflowDetailHistory';
import {mockAPI} from './mocks'

it('WorkflowDetailHistory submitRun', () => {
  mockAPI([null, null]);
  const component = ReactTestRenderer.create(<WorkflowDetailHistory workflow={{id: 1}}/>);
  const event = {preventDefault: jest.fn()};
  const instance = component.getInstance();
  instance.loadRuns = jest.fn();
  instance.submitRun(event);
  expect(instance.loadRuns).toBeCalledWith(1);
});

it('WorkflowDetailHistory selectPage', () => {
  mockAPI([null, null]);
  const component = ReactTestRenderer.create(<WorkflowDetailHistory workflow={{id: 1}}/>);
  const instance = component.getInstance();
  instance.loadRuns = jest.fn();
  instance.selectPage(1);
  expect(instance.loadRuns).toBeCalledWith(1);
});

it('WorkflowDetailHistory componentWillReceiveProps', () => {
  mockAPI([null, null]);
  const component = ReactTestRenderer.create(<WorkflowDetailHistory workflow={{id: 1}}/>);
  const instance = component.getInstance();
  instance.loadRuns = jest.fn();
  instance.componentWillReceiveProps({workflow: {id: 2}});
  expect(instance.loadRuns).toBeCalledWith(2);
  expect(instance.state.pagination).toEqual({page: 'last'})
});
