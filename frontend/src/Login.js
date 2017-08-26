import React from 'react';
import {
  FormGroup, FormControl, ControlLabel, Button, Alert, Panel, Grid, Row, Col
} from 'react-bootstrap';

import {YawnNavBar} from './utilities';
import API from './API'

export default class Login extends React.Component {
  constructor(props) {
    super(props);
    this.state = {username: '', password: '', error: null};
  }

  componentDidMount() {
    document.title = `YAWN - Login`;
  }

  handleChange = (event) => {
    this.setState({[event.target.id]: event.target.value});
  };

  handleSubmit = (event) => {
    event.preventDefault();
    const credentials = {
      username: this.state.username,
      password: this.state.password
    };
    API.patch('/api/users/login/', credentials, (payload, error) => {
      if (error) {
        this.setState({error});
      } else {
        this.props.router.push('/');
      }
    });
  };

  render() {
    return (
      <YawnNavBar>
        <Grid>
          <Row className="show-grid">
            <Col xs={1} md={4}/>
            <Col xs={4} md={4}>
              <Panel header="Login">
                <form onSubmit={this.handleSubmit}>
                  {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
                  <FormGroup controlId="username">
                    <ControlLabel>Username</ControlLabel>
                    <FormControl type="text" value={this.state.username}
                                 onChange={this.handleChange}
                    />
                  </FormGroup>
                  <FormGroup controlId="password">
                    <ControlLabel>Password</ControlLabel>
                    <FormControl type="password" value={this.state.password}
                                 onChange={this.handleChange}
                    />
                  </FormGroup>
                  <Button type="submit" bsStyle="primary">Login</Button>
                </form>
              </Panel>

            </Col>
            <Col xs={1} md={4}/>
          </Row>
        </Grid>
      </YawnNavBar>
    );
  }
}
