import React from 'react';
import {Alert, Navbar, NavItem} from 'react-bootstrap';
import {browserHistory} from 'react-router';

export class YawnNavItem extends React.Component {
  transition(event) {
    event.preventDefault();
    browserHistory.push(event.currentTarget.pathname);
  }

  render() {
    const className = window.location.pathname === this.props.href ? 'active' : '';
    return (
      <NavItem
        href={this.props.href}
        className={className}
        onClick={this.transition}
      >
        {this.props.children}
      </NavItem>
    );
  }
}


export class Container extends React.Component {
  render() {
    return (
      <div>
        <Navbar>
          <Navbar.Header>
            <Navbar.Brand>YAWN</Navbar.Brand>
          </Navbar.Header>
          {this.props.toolbar}
        </Navbar>
        <div className="container">
          {this.props.error && <Alert bsStyle="danger">{this.props.error}</Alert>}
          {this.props.children}
        </div>
      </div>
    );
  }
}
