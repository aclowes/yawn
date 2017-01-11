import React from 'react';
import {Table, Alert} from 'react-bootstrap';
import {Link} from 'react-router';

import API from "./API";

export default class WorkflowDetailHistory extends React.Component {
  constructor(props) {
    super(props);
    this.state = {runs: null, error: null};
  }

  componentDidMount() {
    API.get(`/api/runs/?workflow=${this.props.workflow.id}`, (payload, error) => {
      this.setState({runs: payload, error});
    });
  }

  renderRunHeaders() {
    return this.state.runs.map((run, index) => {
      const date = (run.scheduled_time || run.submitted_time).substr(0, 10);
      const type = run.scheduled_time ? 'Scheduled' : 'Manual';
      const run_name = `${date} (${type})`;
      return <td key={run.id}>{run_name}</td>
    })
  }

  /* Render the status of each task run as a table cell */
  renderTaskRuns(template) {
    // extract this task from each run
    const taskRuns = this.state.runs.map((run) =>
      run.tasks.find((task) => task.name === template.name)
    );
    return taskRuns.map((task) => (
      <td key={task.id}>
        <Link to={`/tasks/${task.id}`}>
          {task.status}
        </Link>
      </td>
    ))
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
            <td/>
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