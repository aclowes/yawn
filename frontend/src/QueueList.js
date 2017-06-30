import React from 'react';
import {Table, Alert, Button} from 'react-bootstrap';

import API from "./API";

export default class QueueList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {queues: null, error: null};
  }

  componentDidMount() {
    API.get(`/api/queues/`, (payload, error) => {
      this.setState({queues: payload, error});
    });
  }

  purgeQueue(id) {
    API.patch(`/api/queues/${id}/`, {purge: true}, (payload, error) => {
      if (error) {
        this.setState({error});
      } else {
        // insert the updated queue record
        this.setState({
          queues: this.state.queues.map((queue) => {
            return queue.id === payload.id ? payload : queue;
          })
        });
      }
    });
  }

  renderRows() {
    if (this.state.queues === null) {
      return (
        <tr>
          <td colSpan="3">Loading...</td>
        </tr>
      )
    } else {
      return this.state.queues.map((queue) => {
        const terminate = () => this.purgeQueue(queue.id);
        return (
          <tr key={queue.id}>
            <td>{queue.name}</td>
            <td>{queue.message_count}</td>
            <td>
              <Button bsSize="small" onClick={terminate}>
                Purge</Button>
            </td>
          </tr>
        )
      })
    }
  }

  render() {
    return (
      <div>
        <h3>Queues</h3>
        {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
        <Table striped bordered condensed hover>
          <thead>
          <tr>
            <th>Name</th>
            <th>Message Count</th>
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
