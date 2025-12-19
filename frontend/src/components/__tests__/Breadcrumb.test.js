import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Breadcrumb from '../Breadcrumb';

describe('Breadcrumb Component', () => {
  const mockSetView = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders breadcrumb for dashboard view', () => {
    render(
      <MemoryRouter>
        <Breadcrumb
          view="dashboard"
          setView={mockSetView}
          token="fake-token"
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders breadcrumb for analyze view', () => {
    render(
      <MemoryRouter>
        <Breadcrumb
          view="analyze"
          setView={mockSetView}
          token="fake-token"
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('New Analysis')).toBeInTheDocument();
  });

  it('renders breadcrumb for result view with job title', () => {
    const currentAnalysis = {
      job_title: 'Software Engineer',
      company_name: 'Tech Corp'
    };

    render(
      <MemoryRouter>
        <Breadcrumb
          view="result"
          setView={mockSetView}
          token="fake-token"
          currentAnalysis={currentAnalysis}
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Software Engineer')).toBeInTheDocument();
  });

  it('renders breadcrumb for non-authenticated user', () => {
    render(
      <MemoryRouter>
        <Breadcrumb
          view="login"
          setView={mockSetView}
          token={null}
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  it('calls setView when breadcrumb item is clicked', () => {
    render(
      <MemoryRouter>
        <Breadcrumb
          view="analyze"
          setView={mockSetView}
          token="fake-token"
        />
      </MemoryRouter>
    );

    const dashboardLink = screen.getByText('Dashboard');
    fireEvent.click(dashboardLink);
    expect(mockSetView).toHaveBeenCalledWith('dashboard');
  });

  it('does not render for landing view', () => {
    const { container } = render(
      <MemoryRouter>
        <Breadcrumb
          view="landing"
          setView={mockSetView}
          token={null}
        />
      </MemoryRouter>
    );

    // When token is null, breadcrumb should not render
    // Check that no breadcrumb text or links are present
    expect(screen.queryByText(/home|dashboard|analysis/i)).not.toBeInTheDocument();
  });
});
