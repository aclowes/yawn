import React from 'react';
import {
  Checkbox, FormGroup, FormControl, ControlLabel,
  Button, Alert, Grid, Row, Col
} from 'react-bootstrap';
import {Link} from 'react-router';

import API from "./API";

export default class UserDetail extends React.Component {
  constructor(props) {
    super(props);
    this.state = {user: null, error: null};
  }

  componentDidMount() {
    API.get(`/api/users/${this.props.params.id}/`, (payload, error) => {
      this.setState({user: payload, error});
    });
  }

  handleChange = (event) => {
    this.setState({[event.target.id]: event.target.value});
  };

  handleSubmit = (event) => {
    event.preventDefault();
    const update = {};
    API.patch(`/api/user/${this.props.user.id}/`, update, (payload, error) => {
      if (error) {
        this.setState({error});
      } else {
        this.props.router.push('/users');
      }
    });
  };

  refreshToken = (event) => {
    event.preventDefault();
    const update = {};
    API.patch(`/api/user/${this.props.user.id}/`, update, (payload, error) => {
      this.setState({user: payload, error});
    });
  };

  render() {
    const user = this.state.user;
    if (user) {
      return (
        <Grid>
          <Row className="show-grid">
            <Col xs={6} md={6}>
              <form onSubmit={this.handleSubmit}>
                {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
                <FormGroup controlId="username">
                  <ControlLabel>Username</ControlLabel>
                  <FormControl type="text" onChange={this.handleChange} value={user.username}/>
                </FormGroup>
                <FormGroup controlId="email">
                  <ControlLabel>Email</ControlLabel>
                  <FormControl type="text" onChange={this.handleChange} value={user.email}/>
                </FormGroup>
                <FormGroup controlId="new_password">
                  <ControlLabel>New Password</ControlLabel>
                  <FormControl type="text" onChange={this.handleChange} value={user.new_password}/>
                </FormGroup>
                <Checkbox value="read_only" onChange={this.toggleCheckbox}
                          checked={user.read_only}>Read-only User</Checkbox>
                <Button type="submit" bsStyle="primary">Save</Button>
                <Link to="/users"><Button>Cancel</Button></Link>
              </form>
            </Col>
            <Col xs={6} md={6}>
              <dl className="dl-horizontal">
                <dt>API Token</dt>
                <dd>{user.api_token}</dd>
              </dl>
              <Button onClick={this.refreshToken}>Refresh Token</Button>
            </Col>
          </Row>
        </Grid>
      );
    } else {
      return (
        <div>
          {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
          Loading...
        </div>
      )
    }
  }
}
