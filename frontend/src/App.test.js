import React from 'react';
import ReactDOM from 'react-dom';

import App from './App';
import ExecutionList from './ExecutionList';
import QueueList from './QueueList';
import TaskDetail from './TaskDetail';
import WorkerList from './WorkerList';
import WorkerDetail from './WorkerDetail';
import WorkflowList from './WorkflowList';
import WorkflowDetail from './WorkflowDetail';

/*
* TODO:
 * Mock API
 * Pass ID to Detail objects
 * Assert things
* */

it('homepage renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<App />, div);
});

it('ExecutionList renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<ExecutionList />, div);
});

it('QueueList renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<QueueList />, div);
});

xit('TaskDetail renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<TaskDetail />, div);
});

it('WorkerList renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<WorkerList />, div);
});

xit('WorkerDetail renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<WorkerDetail />, div);
});

it('WorkflowList renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<WorkflowList />, div);
});

xit('WorkflowDetail renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<WorkflowDetail />, div);
});
