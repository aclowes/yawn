import React from 'react';
import {PanelGroup, Panel, Alert, Pagination} from 'react-bootstrap';
import {Link} from 'react-router';

import API from "./API";

export default class TaskDetail extends React.Component {
  constructor(props) {
    super(props);
    this.state = {task: null, error: null};
  }

  componentDidMount() {
    API.get(`/api/tasks/${this.props.params.id}/`, (payload, error) => {
      const execution = payload ? payload.executions.length : null;
      this.setState({task: payload, error, execution});
    });
  }

  selectExecution = (eventKey) => {
    this.setState({
      execution: eventKey
    });
  };

  renderMessages() {
    return this.state.task.messages.map((message) => (
      <Link to={`/queue/${message.queue_id}`} key={message.id}>{message.queue}</Link>
    ))
  }

  renderExecution() {
    if (this.state.execution === 0) {
      return <div>No executions</div>
    }
    const execution = this.state.task.executions[this.state.execution - 1];
    return (
      <dl className="dl-horizontal">
        <dt>Execution</dt>
        <dd>
          <Pagination
          ellipsis
          bsSize="small"
          items={this.state.task.executions.length}
          maxButtons={10}
          activePage={this.state.execution}
          onSelect={this.selectExecution}/>
        </dd>
        <dt>Status</dt>
        <dd>{execution.status}</dd>
        <dt>Worker</dt>
        <dd>
          <Link to={`/worker/${execution.worker.id}`}>
            {execution.worker.name}
          </Link>
        </dd>
        <dt>Start Time</dt>
        <dd>{execution.start_timestamp}</dd>
        <dt>Stop Time</dt>
        <dd>{execution.stop_timestamp}</dd>
        <dt>Exit Code</dt>
        <dd>{execution.exit_code}</dd>
        <dt>Standard Output</dt>
        <dd>
          <pre>{execution.stdout}</pre>
        </dd>
        <dt>Standard Error</dt>
        <dd>
          <pre>{execution.stderr}</pre>
        </dd>
      </dl>
    )
  }

  render() {
    if (this.state.task === null) {
      return (
        <div>
          {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
          Loading...
        </div>
      )
    } else {
      const task = this.state.task;
      return (
        <div>
          <PanelGroup>
            <Panel header="Details">
              <dl className="dl-horizontal">
                <dt>Workflow</dt>
                <dd>
                  <Link to={`/workflows/${task.workflow.id}`}>
                    {task.workflow.name}
                  </Link>
                </dd>
                <dt>Task Name</dt>
                <dd>{task.name}</dd>
                <dt>Status</dt>
                <dd>{task.status}</dd>
                <dt>Queued Executions</dt>
                <dd>{this.renderMessages()}</dd>
              </dl>
            </Panel>
            <Panel header="Executions">
              {this.renderExecution()}
            </Panel>
          </PanelGroup>
        </div>
      )
    }
  }
}