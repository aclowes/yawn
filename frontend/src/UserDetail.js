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
    if (this.props.params.id === 'add') {
      this.setState({user: true});
    } else {
      API.get(`/api/users/${this.props.params.id}/`, (payload, error) => {
        this.setState({user: payload, error});
      });
    }
  }

  handleChange = (event) => {
    this.setState({
      user: {
        ...this.state.user,
        [event.target.id]: event.target.value
      }
    });
  };

  toggleReadOnly = (event) => {
    this.setState({
      user: {
        ...this.state.user,
        is_staff: !event.target.checked
      }
    });
  };

  handleSubmit = (event) => {
    event.preventDefault();
    const callback = (payload, error) => {
      if (error) {
        this.setState({error});
      } else {
        this.props.router.push('/users');
      }
    };
    if (this.props.params.id === 'add') {
      API.post('/api/users/', this.state.user, callback);
    } else {
      API.patch(`/api/users/${this.state.user.id}/`, this.state.user, callback);
    }
  };

  refreshToken = (event) => {
    event.preventDefault();
    const update = {refresh_token: true};
    API.patch(`/api/users/${this.state.user.id}/`, update, (payload, error) => {
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
                <FormGroup controlId="password">
                  <ControlLabel>New Password</ControlLabel>
                  <FormControl type="password" onChange={this.handleChange} value={user.password}/>
                </FormGroup>
                <Checkbox value="read_only" onChange={this.toggleReadOnly}
                          checked={!user.is_staff}>Read-only User</Checkbox>
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
