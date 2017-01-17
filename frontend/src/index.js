import React from 'react';
import ReactDOM from 'react-dom';
import {Router, Route, IndexRedirect, browserHistory} from 'react-router'

import App from './App';
import WorkflowList from './WorkflowList';
import WorkflowDetail from './WorkflowDetail';
import TaskDetail from "./TaskDetail";
import QueueList from "./QueueList";
import WorkerList from "./WorkerList";
import ExecutionList from "./ExecutionList";

const NotFound = React.createClass({
  render() {
    return <h3>Not Found (404)</h3>
  }
});

ReactDOM.render(
  <Router history={browserHistory}>
    <Route path="/" component={App}>
      <IndexRedirect to="workflows"/>
      <Route path="workflows" component={WorkflowList}/>
      <Route path="workflows/:id" component={WorkflowDetail}/>
      <Route path="tasks/:id" component={TaskDetail}/>
      <Route path="workers" component={WorkerList}/>
      <Route path="executions" component={ExecutionList}/>
      <Route path="queues" component={QueueList}/>
      <Route path="*" component={NotFound}/>
    </Route>
  </Router>,
  document.getElementById('root')
);
