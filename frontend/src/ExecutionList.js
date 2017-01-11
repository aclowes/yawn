import React from 'react';
import {Table, Alert, Button} from 'react-bootstrap';
import {Link} from 'react-router';

import API from "./API";

export default class ExecutionList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {executions: null, error: null};
  }

  componentDidMount() {
    API.get(`/api/executions/`, (payload, error) => {
      this.setState({executions: payload, error});
    });
  }

  renderRows() {
    if (this.state.executions === null) {
      return (
        <tr>
          <td colSpan="3">Loading...</td>
        </tr>
      )
    } else {
      return this.state.executions.map((execution) => (
        <tr key={execution.id}>
          <td><Link to={`/workers/${execution.worker.id}`}>{execution.worker.name}</Link></td>
          <td>{execution.task.workflow.name}</td>
          <td><Link to={`/tasks/${execution.task.id}`}>{execution.task.name}</Link></td>
          <td>{execution.status}</td>
          <td>{execution.start_timestamp}</td>
          <td>{execution.minutes_running}</td>
        </tr>
      ))
    }
  }

  render() {
    return (
      <div>
        <h3>Executions</h3>
        {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
        <Table striped bordered condensed hover>
          <thead>
          <tr>
            <th>Worker</th>
            <th>Workflow</th>
            <th>Task</th>
            <th>Status</th>
            <th>Start Time</th>
            <th>Minutes Running</th>
          </tr>
          </thead>
          <tbody>
          {this.renderRows()}
          </tbody>
        </Table>
      </div>
    )
  }
}