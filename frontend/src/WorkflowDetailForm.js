import React from 'react';
import {
  Checkbox, FormGroup, FormControl, ControlLabel,
  Button, Alert, Pagination
} from 'react-bootstrap';

import API from './API'

/* Helper to extract form values from a given object */
function formValues(object) {
  let parameters;
  // convert the parameters between 'bash' and 'dict' syntax
  if (typeof object.parameters === "string") {
    parameters = {};
    object.parameters.split(/\r\n|\r|\n/g).forEach((line) => {
      const parts = line.split('=');
      if (parts.length === 2) parameters[parts[0]] = parts[1];
    })
  } else {
    parameters = Object.keys(object.parameters).map((key) => {
      return `${key}=${object.parameters[key]}`
    });
    parameters = (parameters || []).join('\n');  // empty object returns null
  }
  return {
    schedule: object.schedule,
    schedule_active: object.schedule_active,
    parameters: parameters,
  }
}

export default class WorkflowDetailForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      editable: false,
      error: null,
      versions: [],
      ...formValues(this.props.workflow)
    };
  }

  componentDidMount() {
    API.get(`/api/names/${this.props.workflow.name_id}/`, (payload, error) => {
      this.setState({versions: payload.versions, error})
    });
  }

  componentWillReceiveProps(nextProps) {
    // the version changed...
    if (nextProps.workflow !== this.props.workflow) {
      this.setState({...formValues(nextProps.workflow)});
    }
  }

  selectVersion = (eventKey) => {
    const version = this.state.versions[eventKey - 1];
    this.props.router.push(`/workflows/${version}`);
  };

  toggleEditable = () => {
    this.setState({editable: !this.state.editable});
  };

  toggleCheckbox = (event) => {
    this.setState({[event.target.value]: event.target.checked});
  };

  handleChange = (event) => {
    this.setState({[event.target.id]: event.target.value});
  };

  handleSubmit = (event) => {
    const update = formValues(this.state);
    API.patch(`/api/workflows/${this.props.workflow.id}/`, update, (payload, error) => {
      this.setState({...formValues(payload), error, editable: false});
    });
    event.preventDefault();
  };

  render() {
    if (this.state.editable) {
      return (
        <form onSubmit={this.handleSubmit}>
          {this.state.error && <Alert bsStyle="danger">{this.state.error}</Alert>}
          <Checkbox value="schedule_active" onChange={this.toggleCheckbox}
                    checked={this.state.schedule_active}>Schedule Active</Checkbox>
          <FormGroup controlId="schedule">
            <ControlLabel>Schedule</ControlLabel>
            <FormControl type="text" placeholder="<minute> <hour> <weekday>"
                         onChange={this.handleChange} value={this.state.schedule}/>
          </FormGroup>
          <FormGroup controlId="parameters">
            <ControlLabel>Parameters</ControlLabel>
            <FormControl componentClass="textarea" placeholder="VARIABLE=value (one per line)"
                         onChange={this.handleChange} value={this.state.parameters}/>
          </FormGroup>
          <Button type="submit" bsStyle="primary">Save</Button>
          <Button onClick={this.toggleEditable}>Cancel</Button>
        </form>
      );
    } else {
      return (
        <div>
          <dl className="dl-horizontal">
            <dt>Name</dt>
            <dd>{this.props.workflow.name}</dd>
            <dt>Version</dt>
            <dd>{}
              <Pagination
                ellipsis
                bsSize="small"
                items={this.state.versions.length}
                maxButtons={10}
                activePage={this.props.workflow.version}
                onSelect={this.selectVersion}/>
            </dd>
            <dt>Schedule Active</dt>
            <dd>{this.state.schedule_active ? 'True' : 'False'}</dd>
            <dt>Schedule</dt>
            <dd>{this.state.schedule}</dd>
            <dt>Next Run</dt>
            <dd>{this.props.workflow.next_run}</dd>
            <dt>Parameters</dt>
            <dd>
              <pre>{this.state.parameters}</pre>
            </dd>
          </dl>
          <Button onClick={this.toggleEditable}>Edit</Button>
        </div>
      )
    }
  }
}