import React from 'react';
import ReactDOM from 'react-dom';
import {Router, Route, IndexRedirect, browserHistory} from 'react-router'

import Login from './Login';
import App from './App';
import WorkflowList from './WorkflowList';
import WorkflowDetail from './WorkflowDetail';
import ExecutionList from "./ExecutionList";
import TaskDetail from "./TaskDetail";
import WorkerList from "./WorkerList";
import WorkerDetail from "./WorkerDetail";
import QueueList from "./QueueList";
import UserList from "./UserList";
import UserDetail from "./UserDetail";

export class NotFound extends React.Component {
  render() {
    return <h3>Page Not Found (404)</h3>
  }
}

export class YawnRouter extends React.Component {
  render() {
    return (
      <Router history={browserHistory}>
        <Route path="/login" component={Login}/>
        <Route path="/" component={App}>
          <IndexRedirect to="workflows"/>
          <Route path="workflows" component={WorkflowList}/>
          <Route path="workflows/:id" component={WorkflowDetail}/>
          <Route path="executions" component={ExecutionList}/>
          <Route path="tasks/:id" component={TaskDetail}/>
          <Route path="workers" component={WorkerList}/>
          <Route path="workers/:id" component={WorkerDetail}/>
          <Route path="queues" component={QueueList}/>
          <Route path="users" component={UserList}/>
          <Route path="users/:id" component={UserDetail}/>
          <Route path="*" component={NotFound}/>
        </Route>
      </Router>
    )
  }
}

ReactDOM.render(<YawnRouter/>, document.getElementById('root'));
