import React from 'react';
import {Panel, PanelGroup, Alert} from 'react-bootstrap';

import API from "./API";
import WorkflowDetailGraph from "./WorkflowDetailGraph";
import WorkflowDetailHistory from "./WorkflowDetailHistory";
import WorkflowDetailForm from "./WorkflowDetailForm";

export default class WorkflowDetail extends React.Component {
  constructor(props) {
    super(props);
    this.state = {workflow: null, error: null};
  }

  componentDidMount() {
    this.loadWorkflow(this.props.params.id);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.params.id !== this.props.params.id) {
      this.loadWorkflow(nextProps.params.id)
    }
  }

  loadWorkflow(version) {
    API.get(`/api/workflows/${version}/`, (payload, error) => {
      this.setState({workflow: payload, error});
    });
  }

  render() {
    const workflow = this.state.workflow;
    if (workflow) {
      return (
        <PanelGroup>
          <Panel header="Details">
            <WorkflowDetailForm workflow={workflow} router={this.props.router}/>
          </Panel>
          <Panel header="Tasks">
            <WorkflowDetailGraph workflow={workflow}/>
          </Panel>
          <Panel header="Runs">
            <WorkflowDetailHistory workflow={workflow}/>
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
