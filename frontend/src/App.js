import React from 'react';
import {Nav, NavItem} from 'react-bootstrap';

import 'bootswatch/united/bootstrap.css';
import './App.css';
import API from './API'
import {YawnNavBar, YawnNavItem} from './utilities';

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {user: null, error: null};
  }

  componentDidMount() {
    API.get(`/api/users/me/`, (payload, error, status) => {
      if (status === 403) {
        // redirect to login page if not authenticated
        this.props.router.push('/login');
      } else {
        if (window.location.pathname === '/login') {
          // return to the homepage; not sure why we're here if we're logged in
          this.props.router.push('/');
        }
        this.setState({user: payload, error});
      }
    });
  }

  logout = (event) => {
    event.preventDefault();
    API.delete(`/api/users/logout/`, {}, (payload, error) => {
      this.setState({user: null, error});
      this.props.router.push('/login');
    });
  };

  renderToolbar() {
    const user = this.state.user && `(${this.state.user.username})`;
    return (
      <div>
        <Nav>
          <YawnNavItem href="/workflows">Workflows</YawnNavItem>
          <YawnNavItem href="/executions">Executions</YawnNavItem>
          <YawnNavItem href="/workers">Workers</YawnNavItem>
          <YawnNavItem href="/queues">Queues</YawnNavItem>
          <YawnNavItem href="/users">Users</YawnNavItem>
        </Nav>
        <Nav pullRight>
          <NavItem onClick={this.logout}>Logout {user}</NavItem>
        </Nav>
      </div>
    )
  }

  render() {
    return (
      <YawnNavBar toolbar={this.renderToolbar()} error={this.state.error}>
        {this.props.children}
      </YawnNavBar>
    );
  }
}
