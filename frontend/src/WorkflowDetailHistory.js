import React from 'react';
import {
  Table, Alert, Tooltip, OverlayTrigger, Glyphicon, Button
} from 'react-bootstrap';
import {Link} from 'react-router';
import {startCase} from 'lodash';

import API from "./API";

export default class WorkflowDetailHistory extends React.Component {
  constructor(props) {
    super(props);
    this.state = {runs: null, error: null};
  }

  statuses = {
    waiting: 'glass',
    queued: 'calendar',
    running: 'console',
    succeeded: 'ok',
    failed: 'remove',
    upstream_failed: 'minus',
  };

  loadRuns(workflow_id) {
    API.get(`/api/runs/?workflow=${workflow_id}`, (payload, error) => {
      this.setState({runs: payload, error});
    });
  }

  componentDidMount() {
    this.loadRuns(this.props.workflow.id);
  }

  componentWillReceiveProps(nextProps) {
    // the version changed...
    if (nextProps.workflow !== this.props.workflow) {
      this.loadRuns(nextProps.workflow.id);
    }
  }

  submitRun = (event) => {
    const data = {workflow_id: this.props.workflow.id};
    API.post('/api/runs/', data, (payload, error) => {
      if (error) {
        this.setState({...this.state, error});
      } else {
        this.loadRuns(this.props.workflow.id);
      }
    });
    event.preventDefault();
  };

  renderRunHeaders() {
    return this.state.runs.map((run, index) => {
      const date = (run.scheduled_time || run.submitted_time).substr(0, 10);
      const type = run.scheduled_time ? 'Scheduled run' : 'Manual run';
      const tooltip = (
        <Tooltip id={run.id}>
          {type}<br/>
          {date}<br/>
          {startCase(run.status)}
        </Tooltip>
      );

      return (
        <OverlayTrigger key={run.id} overlay={tooltip} placement="bottom">
          <th className={run.status}>
            #{index}
          </th>
        </OverlayTrigger>
      )
    })
  }

  /* Render the status of each task run as a table cell */
  renderTaskRuns(template) {
    // extract this task from each run
    const taskRuns = this.state.runs.map((run) =>
      run.tasks.find((task) => task.name === template.name)
    );
    return taskRuns.map((task) => {
      const glyph = this.statuses[task.status];
      const tooltip = <Tooltip id={task.id}>{startCase(task.status)}</Tooltip>;
      return (
        <td key={task.id}>
          <Link to={`/tasks/${task.id}`}>
            <OverlayTrigger overlay={tooltip} placement="top">
              <div>
                <Glyphicon glyph={glyph} className={task.status}/>
              </div>
            </OverlayTrigger>
          </Link>
        </td>
      )
    })
  }

  renderRows() {
    return this.props.workflow.tasks.map((template) => (
        <tr key={template.name}>
          <td>{template.name}</td>
          {this.renderTaskRuns(template)}
        </tr>
      )
    )
  }

  render() {
    if (this.state.runs === null) {
      return (
        <div>
          {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
          Loading...
        </div>
      )
    } else {
      return (
        <div>
          <Table bordered condensed>
            <thead>
            <tr>
              <th className="text-center">Task</th>
              <th className="text-center" colSpan={this.state.runs.length}>Run</th>
            </tr>
            <tr>
              <th/>
              {this.renderRunHeaders()}
            </tr>
            </thead>
            <tbody>
            {this.renderRows()}
            </tbody>
          </Table>
          <Table bordered condensed>
            <tbody>
            <tr>
              <td>Key:</td>
              {Object.entries(this.statuses).map(function ([status, glyph]) {
                return (
                  <td key={status}>
                    <Glyphicon glyph={glyph} className={status}/>: {status}
                  </td>
                )
              })}
            </tr>
            </tbody>
          </Table>
          <Button onClick={this.submitRun}>Start new run</Button>
        </div>
      )
    }
  }
}
