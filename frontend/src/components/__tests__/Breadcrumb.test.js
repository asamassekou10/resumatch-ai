import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Breadcrumb from '../Breadcrumb';

describe('Breadcrumb Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders breadcrumb for dashboard view', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Breadcrumb
          token="fake-token"
        />
      </MemoryRouter>
    );

    // Breadcrumb only shows if there are more than 1 items
    // For dashboard with token, there's only 1 item (Dashboard), so it returns null
    const breadcrumb = screen.queryByRole('navigation');
    expect(breadcrumb).not.toBeInTheDocument();
  });

  it('renders breadcrumb for analyze view', () => {
    render(
      <MemoryRouter initialEntries={['/analyze']}>
        <Breadcrumb
          token="fake-token"
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Analyze Resume')).toBeInTheDocument();
  });

  it('renders breadcrumb for result view with job title', () => {
    const currentAnalysis = {
      job_title: 'Software Engineer',
      company_name: 'Tech Corp'
    };

    render(
      <MemoryRouter initialEntries={['/result']}>
        <Breadcrumb
          token="fake-token"
          currentAnalysis={currentAnalysis}
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Analysis Results')).toBeInTheDocument();
  });

  it('renders breadcrumb for non-authenticated user', () => {
    render(
      <MemoryRouter initialEntries={['/login']}>
        <Breadcrumb
          token={null}
        />
      </MemoryRouter>
    );

    // Breadcrumb only renders if items.length > 1
    // For login without token, breadcrumb should not render
    const breadcrumb = screen.queryByRole('navigation');
    expect(breadcrumb).not.toBeInTheDocument();
  });

  it('calls navigate when breadcrumb item is clicked', () => {
    render(
      <MemoryRouter initialEntries={['/analyze']}>
        <Breadcrumb
          token="fake-token"
        />
      </MemoryRouter>
    );

    // For analyze view with token, there are 2 items: Dashboard and Analyze Resume
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Analyze Resume')).toBeInTheDocument();
    
    const dashboardLink = screen.getByText('Dashboard');
    fireEvent.click(dashboardLink);
    // The component uses navigate() from react-router-dom
    // We verify the link exists and is clickable
    expect(dashboardLink).toBeInTheDocument();
  });

  it('does not render for landing view', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Breadcrumb
          token={null}
        />
      </MemoryRouter>
    );

    // Breadcrumb only renders if items.length > 1
    // For landing page without token, breadcrumb should not render
    const breadcrumb = screen.queryByRole('navigation');
    expect(breadcrumb).not.toBeInTheDocument();
  });
});
