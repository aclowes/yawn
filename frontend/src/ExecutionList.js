import React from 'react';
import {Alert} from 'react-bootstrap';

import API from "./API";
import ExecutionTable from "./ExecutionTable";

export default class ExecutionList extends React.Component {
  constructor(props) {
    super(props);
    document.title = `YAWN - Executions`;
    this.state = {executions: null, error: null};
  }

  componentDidMount() {
    API.get(`/api/executions/`, (payload, error) => {
      this.setState({executions: payload, error});
    });
  }

  render() {
    return (
      <div>
        <h3>Executions</h3>
        {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
        <ExecutionTable executions={this.state.executions} />
      </div>
    )
  }
}
