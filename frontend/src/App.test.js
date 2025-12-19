import { render, screen } from '@testing-library/react';
import App from './App';

// Mock axios to avoid ESM import issues in Jest
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn(), eject: jest.fn() },
      response: { use: jest.fn(), eject: jest.fn() }
    }
  })),
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn()
}));

test('renders app without crashing', () => {
  render(<App />);
  // Just check that the app renders without crashing
  expect(document.body).toBeTruthy();
});
