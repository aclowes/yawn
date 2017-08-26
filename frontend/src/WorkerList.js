import React from 'react';
import {Table, Alert} from 'react-bootstrap';
import {Link} from 'react-router';

import API from "./API";

export default class WorkerList extends React.Component {
  constructor(props) {
    super(props);
    document.title = `YAWN - Workers`;
    this.state = {workers: null, error: null};
  }

  componentDidMount() {
    API.get(`/api/workers/`, (payload, error) => {
      this.setState({workers: payload, error});
    });
  }

  renderRows() {
    if (this.state.workers === null) {
      return (
        <tr>
          <td colSpan="3">Loading...</td>
        </tr>
      )
    } else {
      return this.state.workers.map((worker) => {
        return (
          <tr key={worker.id}>
            <td><Link to={`/workers/${worker.id}`}>{worker.name}</Link></td>
            <td>{worker.status}</td>
            <td>{worker.start_timestamp}</td>
            <td>{worker.last_heartbeat}</td>
          </tr>
        )
      })
    }
  }

  render() {
    return (
      <div>
        <h3>Workers</h3>
        {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
        <Table striped bordered condensed hover>
          <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Start Time</th>
            <th>Last Heartbeat</th>
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
