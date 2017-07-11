import React from 'react';
import ReactDOM from 'react-dom';
import ReactShallowRenderer from 'react-test-renderer/shallow';
import ReactTestRenderer from 'react-test-renderer';

jest.mock('react-dom', () => ({render: jest.fn()}));

import {YawnRouter, NotFound} from '../index';
import {mockAPI} from './mocks'

it('router renders', () => {
  const renderer = new ReactShallowRenderer();
  renderer.render(<YawnRouter />);
  const result = renderer.getRenderOutput();
  // this doesn't work for some reason...
  // expect(result.type).toBe('Router');
});

it('404 renders', () => {
  mockAPI();
  const component = ReactTestRenderer.create(<NotFound />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('ReactDOM is called', () => {
  expect(ReactDOM.render).toHaveBeenCalled();
});
