import React from 'react';
import {Table, Alert} from 'react-bootstrap';
import {Link} from 'react-router';

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

  renderRows() {
    if (this.state.users === null) {
      return (
        <tr>
          <td colSpan="3">Loading...</td>
        </tr>
      )
    } else {
      return this.state.users.map((user) => {
        return (
          <tr key={user.id}>
            <td><Link to={`/users/${user.id}`}>{user.username}</Link></td>
            <td>{user.email}</td>
            <td>{user.token}</td>
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
            <th>Username</th>
            <th>Email</th>
            <th>Token</th>
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
