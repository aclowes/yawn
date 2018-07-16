import React from 'react';
import {Glyphicon, Nav, NavItem} from 'react-bootstrap';
import moment from 'moment-timezone';

import 'bootswatch/united/bootstrap.css';
import './App.css';
import API from './API'
import {Container, YawnNavItem} from './AppContainer';

export default class App extends React.Component {
  constructor(props) {
    super(props);
    const timezone = moment().tz(moment.tz.guess()).zoneAbbr();
    moment.tz.setDefault(timezone);
    this.state = {user: {}, error: null, reload: false, timezone};
  }

  componentDidMount() {
    API.get(`/api/users/me/`, (payload, error, status) => {
      if ([401, 403].indexOf(status) > -1) {
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

  componentDidUpdate(prevProps) {
    if (this.state.reload) {
      this.setState({reload: false})
    }
  }

  logout = (event) => {
    event.preventDefault();
    API.delete(`/api/users/logout/`, {}, (payload, error) => {
      this.setState({user: {}, error});
      this.props.router.push('/login');
    });
  };

  /* Remount the page to force everything to reload */
  refresh = (event) => {
    this.setState({reload: true});
  };

  /* Switch between local and UTC time */
  toggleTimezone = (event) => {
    event.preventDefault();
    let timezone = this.state.timezone;
    if (timezone === 'UTC') {
      timezone = moment().tz(moment.tz.guess()).zoneAbbr();
    } else {
      timezone = 'UTC';
    }
    moment.tz.setDefault(timezone);
    this.setState({timezone, reload: true});
  };

  renderToolbar() {
    const userAction = this.state.user ? `Logout (${this.state.user.username})` : 'Login';
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
          <NavItem onClick={this.refresh}>
            <Glyphicon glyph="refresh"/>
          </NavItem>
          <NavItem onClick={this.toggleTimezone}>
            {this.state.timezone}
          </NavItem>
          <NavItem onClick={this.logout}>{userAction}</NavItem>
        </Nav>
      </div>
    )
  }

  render() {
    return (
      <Container toolbar={this.renderToolbar()} error={this.state.error}>
        {this.state.reload ? 'Loading...' : this.props.children}
      </Container>
    );
  }
}
