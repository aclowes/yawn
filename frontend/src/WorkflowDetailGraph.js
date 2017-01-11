import React from 'react';
import graphlib from 'graphlib'
import render from 'dagre-d3/lib/render'
import d3 from 'd3'

export default class WorkflowDetailGraph extends React.Component {
  shouldComponentUpdate() {
    /* Never re-render */
    return false
  }

  render() {
    return <svg></svg>
  }

  componentDidMount() {
    /* After rendering, draw the graph */
    const workflow = this.props.workflow;
    const renderer = new render();
    const graph = new graphlib.Graph().setGraph({});

    workflow.tasks.forEach(function (task) {
      // Add nodes: rx ry is border radius
      graph.setNode(task.name, {label: task.name, rx: 5, ry: 5});

      // Add lines between nodes
      task.upstream.forEach(function (upstreamTask) {
        graph.setEdge(upstreamTask, task.name, {})
      })
    });

    const inner = d3.select("svg").append("g");
    renderer(inner, graph);
  }
}