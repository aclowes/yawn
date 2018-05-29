import React from 'react';
import {Panel, PanelGroup, Alert} from 'react-bootstrap';

import API from "./API";
import ExecutionTable from "./ExecutionTable";

export default class WorkerDetail extends React.Component {
  constructor(props) {
    super(props);
    this.state = {worker: null, executions: null, error: null};
  }

  componentDidMount() {
    API.get(`/api/workers/${this.props.params.id}/`, (payload, error) => {
      this.setState({worker: payload, error});

      if (payload) {  // only get if worker returns... not strictly necessary
        document.title = `YAWN - Worker: ${payload.name}`;
        API.get(`/api/executions/?worker=${this.props.params.id}`, (payload, error) => {
          this.setState({executions: payload, error});
        });
      }

    });
  }

  render() {
    const worker = this.state.worker;
    if (worker) {
      return (
        <PanelGroup>
          <Panel header="Details">
            <dl className="dl-horizontal">
              <dt>Name</dt>
              <dd>{worker.name}</dd>
              <dt>Status</dt>
              <dd>{worker.status}</dd>
              <dt>Start Timestamp</dt>
              <dd>{worker.start_timestamp}</dd>
              <dt>Last Heartbeat</dt>
              <dd>{worker.last_heartbeat}</dd>
            </dl>
          </Panel>
          <Panel header="Executions">
            {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
            <ExecutionTable executions={this.state.executions}/>
          </Panel>
        </PanelGroup>
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
