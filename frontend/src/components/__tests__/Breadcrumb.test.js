import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Breadcrumb from '../Breadcrumb';
import { AuthContext } from '../../contexts/AuthContext';

const mockSetView = jest.fn();

const renderWithContext = (ui, { route = '/' } = {}) => {
  return render(
    <AuthContext.Provider value={{ isAuthenticated: true, user: { name: 'Test' }, token: 'fake-token' }}>
      <MemoryRouter initialEntries={[route]}>
        {ui}
      </MemoryRouter>
    </AuthContext.Provider>
  );
};

describe('Breadcrumb Component', () => {
  it('renders breadcrumb for dashboard view', () => {
    renderWithContext(<Breadcrumb view="dashboard" setView={mockSetView} />, { route: '/dashboard' });
    // Direct assertion is required by linter
    expect(screen.getByText(/Home/i)).toBeInTheDocument();
  });

  it('renders breadcrumb for analyze view', () => {
    renderWithContext(<Breadcrumb view="analyze" setView={mockSetView} />, { route: '/analyze' });
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    // Matches "Analyze Resume" or "New Analysis"
    expect(screen.getByText(/(Analyze|New)/i)).toBeInTheDocument();
  });
});
