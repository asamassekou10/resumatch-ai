import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Navigation from '../Navigation';

describe('Navigation Component', () => {
  const mockSetView = jest.fn();
  const mockHandleLogout = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders navigation for authenticated user', () => {
    render(
      <Navigation
        view="dashboard"
        setView={mockSetView}
        token="fake-token"
        handleLogout={mockHandleLogout}
      />
    );

    expect(screen.getByText('ResumeAnalyzer AI')).toBeInTheDocument();
    expect(screen.getByText('New Analysis')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  it('renders navigation for non-authenticated user', () => {
    render(
      <Navigation
        view="landing"
        setView={mockSetView}
        token={null}
        handleLogout={mockHandleLogout}
      />
    );

    expect(screen.getByText('ResumeAnalyzer AI')).toBeInTheDocument();
    expect(screen.getByText('Log In')).toBeInTheDocument();
    expect(screen.getByText('Sign Up')).toBeInTheDocument();
  });

  it('shows back button when showBackButton is true', () => {
    render(
      <Navigation
        view="login"
        setView={mockSetView}
        token={null}
        handleLogout={mockHandleLogout}
        showBackButton={true}
        backButtonText="Back to Home"
      />
    );

    expect(screen.getByText('Back to Home')).toBeInTheDocument();
  });

  it('calls setView when logo is clicked', () => {
    render(
      <Navigation
        view="dashboard"
        setView={mockSetView}
        token="fake-token"
        handleLogout={mockHandleLogout}
      />
    );

    const logo = screen.getByText('ResumeAnalyzer AI');
    fireEvent.click(logo);
    expect(mockSetView).toHaveBeenCalledWith('dashboard');
  });

  it('calls handleLogout when logout button is clicked', () => {
    render(
      <Navigation
        view="dashboard"
        setView={mockSetView}
        token="fake-token"
        handleLogout={mockHandleLogout}
      />
    );

    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);
    expect(mockHandleLogout).toHaveBeenCalled();
  });

  it('calls custom onBackClick when back button is clicked', () => {
    const mockOnBackClick = jest.fn();
    
    render(
      <Navigation
        view="result"
        setView={mockSetView}
        token="fake-token"
        handleLogout={mockHandleLogout}
        showBackButton={true}
        backButtonText="Back to Dashboard"
        onBackClick={mockOnBackClick}
      />
    );

    const backButton = screen.getByText('Back to Dashboard');
    fireEvent.click(backButton);
    expect(mockOnBackClick).toHaveBeenCalled();
  });
});
