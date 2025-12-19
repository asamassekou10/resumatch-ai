import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Navigation from '../Navigation';

describe('Navigation Component', () => {
  const mockSetView = jest.fn();
  const mockHandleLogout = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders navigation for authenticated user', () => {
    render(
      <MemoryRouter>
        <Navigation
          view="dashboard"
          setView={mockSetView}
          token="fake-token"
          handleLogout={mockHandleLogout}
        />
      </MemoryRouter>
    );

    expect(screen.getByText('ResumeAnalyzer AI')).toBeInTheDocument();
    expect(screen.getByText('Market Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders navigation for non-authenticated user', () => {
    render(
      <MemoryRouter>
        <Navigation
          view="landing"
          setView={mockSetView}
          token={null}
          handleLogout={mockHandleLogout}
        />
      </MemoryRouter>
    );

    expect(screen.getByText('ResumeAnalyzer AI')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByText('Sign Up')).toBeInTheDocument();
  });

  it('shows back button when showBackButton is true', () => {
    render(
      <MemoryRouter>
        <Navigation
          view="login"
          setView={mockSetView}
          token={null}
          handleLogout={mockHandleLogout}
          showBackButton={true}
          backButtonText="Back to Home"
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Back to Home')).toBeInTheDocument();
  });

  it('calls setView when logo is clicked', () => {
    render(
      <MemoryRouter>
        <Navigation
          view="dashboard"
          setView={mockSetView}
          token="fake-token"
          handleLogout={mockHandleLogout}
        />
      </MemoryRouter>
    );

    const logo = screen.getByText('ResumeAnalyzer AI');
    fireEvent.click(logo);
    expect(mockSetView).toHaveBeenCalledWith('dashboard');
  });

  it('calls handleLogout when logout button is clicked', () => {
    render(
      <MemoryRouter>
        <Navigation
          view="dashboard"
          setView={mockSetView}
          token="fake-token"
          handleLogout={mockHandleLogout}
        />
      </MemoryRouter>
    );

    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);
    expect(mockHandleLogout).toHaveBeenCalled();
  });

  it('calls custom onBackClick when back button is clicked', () => {
    const mockOnBackClick = jest.fn();
    
    render(
      <MemoryRouter>
        <Navigation
          view="result"
          setView={mockSetView}
          token="fake-token"
          handleLogout={mockHandleLogout}
          showBackButton={true}
          backButtonText="Back to Dashboard"
          onBackClick={mockOnBackClick}
        />
      </MemoryRouter>
    );

    const backButton = screen.getByText('Back to Dashboard');
    fireEvent.click(backButton);
    expect(mockOnBackClick).toHaveBeenCalled();
  });
});
