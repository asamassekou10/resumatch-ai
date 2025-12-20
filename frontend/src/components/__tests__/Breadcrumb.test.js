import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Breadcrumb from '../Breadcrumb';
import AuthContext from '../../contexts/AuthContext';

const mockSetView = jest.fn();

const renderWithContext = (ui, { route = '/' } = {}) => {
  return render(
    <AuthContext.Provider value={{ isAuthenticated: true, user: { name: 'Test' }, token: 'fake-token', isLoading: false }}>
      <MemoryRouter 
        initialEntries={[route]}
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true
        }}
      >
        {ui}
      </MemoryRouter>
    </AuthContext.Provider>
  );
};

describe('Breadcrumb Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders breadcrumb for dashboard view', () => {
    renderWithContext(
      <Breadcrumb view="dashboard" setView={mockSetView} token="fake-token" />, 
      { route: '/dashboard' }
    );
    // Breadcrumb only shows if there are more than 1 items
    // For dashboard with token, there's only 1 item (Dashboard), so it returns null
    const breadcrumb = screen.queryByRole('navigation');
    expect(breadcrumb).not.toBeInTheDocument();
  });

  it('renders breadcrumb for analyze view', () => {
    renderWithContext(
      <Breadcrumb view="analyze" setView={mockSetView} token="fake-token" />, 
      { route: '/analyze' }
    );
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    // Flexible check for "Analyze Resume" or "New Analysis"
    expect(screen.getByText(/(Analyze|New)/i)).toBeInTheDocument();
  });
});
