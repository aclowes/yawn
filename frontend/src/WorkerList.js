import React from 'react';
import {Table, Alert, Button} from 'react-bootstrap';
import {Link} from 'react-router';

import API from "./API";

export default class WorkerList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {workers: null, error: null};
  }

  componentDidMount() {
    API.get(`/api/workers/`, (payload, error) => {
      this.setState({workers: payload, error});
    });
  }

  terminateWorker(id) {
    API.patch(`/api/workers/${id}/`, {terminate: true}, (payload, error) => {
      if (error) {
        this.setState({error});
      } else {
        // insert the updated worker record
        this.setState({
          workers: this.state.workers.map((worker) => {
            return worker.id === payload.id ? payload : worker;
          })
        });
      }
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
      return this.state.workers.map((worker) => (
        <tr key={worker.id}>
          <td><Link to={`/workers/${worker.id}`}>{worker.name}</Link></td>
          <td>{worker.status}</td>
          <td>{worker.start_timestamp}</td>
          <td>{worker.last_heartbeat}</td>
          <td>
            <Button onClick={() => this.terminateWorker(worker.id)} disabled>Terminate</Button>
          </td>
        </tr>
      ))
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
            <th>Actions</th>
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