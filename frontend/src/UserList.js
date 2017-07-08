import React from 'react';
import {Table, Alert, Button} from 'react-bootstrap';

import API from "./API";

export default class UserList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {users: null, error: null};
  }

  componentDidMount() {
    API.get(`/api/users/`, (payload, error) => {
      this.setState({users: payload, error});
    });
  }

  purgeUser(id) {
    API.patch(`/api/users/${id}/`, {purge: true}, (payload, error) => {
      if (error) {
        this.setState({error});
      } else {
        // insert the updated user record
        this.setState({
          users: this.state.users.map((user) => {
            return user.id === payload.id ? payload : user;
          })
        });
      }
    });
  }

  renderRows() {
    if (this.state.users === null) {
      return (
        <tr>
          <td colSpan="3">Loading...</td>
        </tr>
      )
    } else {
      return this.state.users.map((user) => {
        const terminate = () => this.purgeUser(user.id);
        return (
          <tr key={user.id}>
            <td>{user.username}</td>
            <td>{user.email}</td>
            <td>{user.message_count}</td>
          </tr>
        )
      })
    }
  }

  render() {
    return (
      <div>
        <h3>Users</h3>
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
