import React from 'react';
import ReactTestRenderer from 'react-test-renderer';

import App from '../App';

import {mockAPI} from './mocks'

it('homepage renders', () => {
  mockAPI([{'username': 'test user'}]);
  const component = ReactTestRenderer.create(<App />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});

it('calls logout on click', () => {
  const mock = jest.fn();
  mock.preventDefault = jest.fn();
  const app = new App();
  app.props = {router: {push: jest.fn()}};
  app.logout(mock);
  expect(mock.preventDefault).toBeCalled();
  expect(app.props.router.push).toBeCalledWith('/login');
});
