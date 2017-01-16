import React from 'react';
import Graph from 'graphlib/lib/graph'
import render from 'dagre-d3/lib/render'
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
    const renderer = new render();
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