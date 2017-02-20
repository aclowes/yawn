import React from 'react';
import renderer from 'react-test-renderer';

import App from '../App';

import {mockAPI} from './mocks'

it('homepage renders', () => {
  mockAPI();
  const component = renderer.create(<App />);
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
