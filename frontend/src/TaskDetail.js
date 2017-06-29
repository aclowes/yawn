import React from 'react';
import {PanelGroup, Panel, Alert, Pagination, Button} from 'react-bootstrap';
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

  enqueue = () => {
    API.patch(`/api/tasks/${this.props.params.id}/`, {enqueue: true}, (payload, error) => {
      this.setState({task: payload, error});
    });
  };

  terminate = () => {
    const execution = this.state.task.executions[this.state.execution - 1];
    API.patch(`/api/tasks/${this.props.params.id}/`, {terminate: execution.id}, (payload, error) => {
      this.setState({task: payload, error});
    });
  };

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

  renderWorkflowLink() {
    const task = this.state.task;
    if (task.workflow) return (
      <Link to={`/workflows/${task.workflow.id}`}>
        {task.workflow.name} - v{task.workflow.version}
      </Link>
    )
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
          <Link to={`/workers/${execution.worker.id}`}>
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
                  {this.renderWorkflowLink()}
                </dd>
                <dt>Task Name</dt>
                <dd>{task.name}</dd>
                <dt>Command</dt>
                <dd>
                  <pre>{task.command}</pre>
                </dd>
                <dt>Max Retries</dt>
                <dd>{task.max_retries}</dd>
                <dt>Timeout</dt>
                <dd>{task.timeout} {task.timeout ? 'seconds' : '(none)'}</dd>
                <dt>Status</dt>
                <dd>{task.status}</dd>
                <dt>Queued Executions</dt>
                <dd>{this.renderMessages()}</dd>
              </dl>
              <Button onClick={this.enqueue}>Run</Button>
            </Panel>
            <Panel header="Executions">
              {this.renderExecution()}
              <Button onClick={this.terminate}>Terminate</Button>
            </Panel>
          </PanelGroup>
        </div>
      )
    }
  }
}
