import React from 'react';
import {Panel, PanelGroup} from 'react-bootstrap';
//import {Link} from 'react-router';

import API from "./API";
import WorkflowDetailGraph from "./WorkflowDetailGraph";
import WorkflowDetailHistory from "./WorkflowDetailHistory";
import WorkflowDetailForm from "./WorkflowDetailForm";

export default class WorkflowDetail extends React.Component {
  constructor(props) {
    super(props);
    this.state = {workflow: null};
  }

  componentDidMount() {
    API.get(`/api/workflows/${this.props.params.id}/`, (payload, error) => {
      this.setState({workflow: payload, error: error});
    })
  }

  render() {
    const workflow = this.state.workflow;
    if (workflow) {
      return (
        <PanelGroup>
          <Panel header="Details">
            <WorkflowDetailForm workflow={workflow}/>
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
      return <span>Loading...</span>
    }
  }
}
