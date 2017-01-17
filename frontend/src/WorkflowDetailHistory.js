import React from 'react';
import {Table, Alert, Tooltip, OverlayTrigger, Glyphicon} from 'react-bootstrap';
import {Link} from 'react-router';
import {startCase} from 'lodash';

import API from "./API";

export default class WorkflowDetailHistory extends React.Component {
  constructor(props) {
    super(props);
    this.state = {runs: null, error: null};
  }

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

  renderRunHeaders() {
    return this.state.runs.map((run, index) => {
      const date = (run.scheduled_time || run.submitted_time).substr(0, 10);
      const type = run.scheduled_time ? 'Scheduled' : 'Manual';
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
      const glyph = {
        waiting: 'glass',
        queued: 'download-alt',
        running: 'refresh',
        succeeded: 'ok',
        failed: 'remove',
      }[task.status];
      const tooltip = <Tooltip id={task.id}>{startCase(task.status)}</Tooltip>;
      return (
        <td key={task.id} className={task.status}>
          <OverlayTrigger overlay={tooltip} placement="right">
            <Link to={`/tasks/${task.id}`}>
              <Glyphicon glyph={glyph}/>
            </Link>
          </OverlayTrigger>
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
      )
    }
  }
}