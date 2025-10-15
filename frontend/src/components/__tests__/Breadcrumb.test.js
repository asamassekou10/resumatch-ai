import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Breadcrumb from '../Breadcrumb';

describe('Breadcrumb Component', () => {
  const mockSetView = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders breadcrumb for dashboard view', () => {
    render(
      <Breadcrumb
        view="dashboard"
        setView={mockSetView}
        token="fake-token"
      />
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders breadcrumb for analyze view', () => {
    render(
      <Breadcrumb
        view="analyze"
        setView={mockSetView}
        token="fake-token"
      />
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
      <Breadcrumb
        view="result"
        setView={mockSetView}
        token="fake-token"
        currentAnalysis={currentAnalysis}
      />
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Software Engineer')).toBeInTheDocument();
  });

  it('renders breadcrumb for non-authenticated user', () => {
    render(
      <Breadcrumb
        view="login"
        setView={mockSetView}
        token={null}
      />
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  it('calls setView when breadcrumb item is clicked', () => {
    render(
      <Breadcrumb
        view="analyze"
        setView={mockSetView}
        token="fake-token"
      />
    );

    const dashboardLink = screen.getByText('Dashboard');
    fireEvent.click(dashboardLink);
    expect(mockSetView).toHaveBeenCalledWith('dashboard');
  });

  it('does not render for landing view', () => {
    const { container } = render(
      <Breadcrumb
        view="landing"
        setView={mockSetView}
        token={null}
      />
    );

    expect(container.firstChild).toBeNull();
  });
});
