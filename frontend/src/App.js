import React from 'react';
import {Navbar, Nav} from 'react-bootstrap';  //NavDropdown, MenuItem

import 'bootswatch/united/bootstrap.css';
import './App.css';
import {YawnNavItem} from './utilities';

class App extends React.Component {

  render() {
    return (
      <div>
        <Navbar>
          <Navbar.Header>
            <Navbar.Brand>YAWN</Navbar.Brand>
          </Navbar.Header>
          <Nav>
            <YawnNavItem href="/">Workflows</YawnNavItem>
            <YawnNavItem href="/workers">Workers</YawnNavItem>
            <YawnNavItem href="/executions">Executions</YawnNavItem>
            <YawnNavItem href="/queues">Queues</YawnNavItem>
            {/*<NavDropdown eventKey={3} title="Dropdown" id="basic-nav-dropdown">*/}
            {/*<MenuItem eventKey={3.1}>Action</MenuItem>*/}
            {/*<MenuItem eventKey={3.2}>Another action</MenuItem>*/}
            {/*<MenuItem eventKey={3.3}>Something else here</MenuItem>*/}
            {/*<MenuItem divider/>*/}
            {/*<MenuItem eventKey={3.3}>Separated link</MenuItem>*/}
            {/*</NavDropdown>*/}
          </Nav>
        </Navbar>
        <div className="container">
          {this.props.children}
        </div>
      </div>
    );
  }
}

export default App;
