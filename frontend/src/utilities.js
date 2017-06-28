import React from 'react';
import {NavItem} from 'react-bootstrap';
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
