import React from 'react';
// importing from /dist/ because something in dagre-d3 isn't webpack compatible
import * as dagreD3 from 'dagre-d3/dist/dagre-d3'
import Graph from 'graphlib/lib/graph'
import d3 from 'd3'

export default class WorkflowDetailGraph extends React.Component {
  shouldComponentUpdate() {
    /* Never re-render */
    return false
  }

  render() {
    return <svg/>
  }

  componentDidMount() {
    /* After rendering, draw the graph */
    const workflow = this.props.workflow;
    const renderer = new dagreD3.render();
    const graph = new Graph().setGraph({});

    workflow.tasks.forEach(function (task) {
      // Add nodes: rx ry is border radius
      graph.setNode(task.name, {label: task.name, rx: 5, ry: 5});

      // Add lines between nodes
      task.upstream.forEach(function (upstreamTask) {
        graph.setEdge(upstreamTask, task.name, {})
      })
    });

    const svg = d3.select("svg");
    const g = svg.append("g");
    renderer(g, graph);
    svg.attr('height', graph.graph().height);
    svg.attr('width', graph.graph().width);
  }
}
