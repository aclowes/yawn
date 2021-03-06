import React from 'react';
import {Alert, Table} from 'react-bootstrap';
import {Link} from 'react-router';

import API from "./API";

export default class WorkflowList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {workflows: null};
  }

  componentDidMount() {
    document.title = `YAWN - Workflows`;
    API.get('/api/names/', (payload, error) => {
      this.setState({workflows: payload, error});
    })
  }

  renderRows() {
    if (this.state.workflows === null) {
      return (
        <tr>
          <td colSpan="4">Loading...</td>
        </tr>
      )
    } else {
      return this.state.workflows.map((workflow) => (
        <tr key={workflow.id}>
          <td><Link to={`/workflows/${workflow.current_version_id}`}>{workflow.name}</Link></td>
          <td>{workflow.schedule_active ? 'True' : 'False'}</td>
          <td>{workflow.schedule || '(none)'}</td>
          <td>{workflow.task_count}</td>
        </tr>
      ))
    }
  }

  render() {
    return (
      <div>
        <h3>Workflows</h3>
        {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
        <Table striped bordered condensed hover>
          <thead>
          <tr>
            <th>Name</th>
            <th>Schedule Active</th>
            <th>Schedule</th>
            <th>Tasks</th>
          </tr>
          </thead>
          <tbody>
          {this.renderRows()}
          </tbody>
        </Table>
      </div>
    );
  }
}
