import React from 'react';
import {PanelGroup, Panel, Alert, Pagination, Button, ButtonToolbar} from 'react-bootstrap';
import {Link} from 'react-router';

import API from "./API";
import {formatDateTime} from "./utilities";

export default class TaskDetail extends React.Component {
  constructor(props) {
    super(props);
    this.state = {task: null, error: null, follow: false};
  }

  componentDidMount() {
    this.refreshExecution();
  }

  componentDidUpdate() {
    if (this.state.follow) {
      const maxScroll = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      window.scroll(0, maxScroll);
    }
  };

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

  refreshExecution = () => {
    API.get(`/api/tasks/${this.props.params.id}/`, (payload, error) => {
      let execution = null;
      if (payload) {
        document.title = `YAWN - Task: ${payload.name}`;
        // keep the currently selected execution, or get the latest
        execution = this.state.execution || payload.executions.length;

        // while the task is running, refresh the page every five seconds
        const status = execution > 0 && payload.executions[execution - 1].status;
        if (status === 'running') {
          window.setTimeout(this.refreshExecution, 5000);
        }
      }
      this.setState({task: payload, error, execution});
    });
  };

  toggleFollow = () => {
    this.setState({follow: !this.state.follow});
  };

  renderMessages() {
    return this.state.task.messages.map((message) => (
      <span><Link to='/queues/' key={message.id}>{message.queue}</Link> </span>
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
    const canTerminate = execution.status === 'running';
    return (
      <div>
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
          <dd>{formatDateTime(execution.start_timestamp)}</dd>
          <dt>Stop Time</dt>
          <dd>{formatDateTime(execution.stop_timestamp)}</dd>
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
        <ButtonToolbar>
          <Button onClick={this.terminate} disabled={!canTerminate} bsStyle="danger">Terminate</Button>
          <Button onClick={this.toggleFollow}>
            {this.state.follow ? 'Unpin scroll' : 'Pin scroll'}
          </Button>
        </ButtonToolbar>
      </div>
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
          {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
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
            </Panel>
          </PanelGroup>
        </div>
      )
    }
  }
}
