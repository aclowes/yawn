import React from 'react';
import {Table} from 'react-bootstrap';
import {Link} from 'react-router';


export default class ExecutionTable extends React.Component {

  renderRows() {
    if (this.props.executions === null) {
      return (
        <tr>
          <td colSpan="6">Loading...</td>
        </tr>
      )
    } else {
      return this.props.executions.map((execution) => (
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
      <Table striped bordered condensed hover>
        <thead>
        <tr>
          <th>Worker</th>
          <th>Workflow</th>
          <th>Task</th>
          <th>Status</th>
          <th>Start Time</th>
          <th>Runtime</th>
        </tr>
        </thead>
        <tbody>
        {this.renderRows()}
        </tbody>
      </Table>
    )
  }
}