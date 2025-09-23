import { render, screen, fireEvent } from '@testing-library/react';
import CandidateCard from '../components/CandidateCard';

describe('CandidateCard', () => {
  const minimalCandidate = {
    id: '1',
    name: 'Jane Doe',
    skills: ['React', 'Python'],
    experience: '5 years',
    location: 'San Francisco, CA',
    otherDetails: { email: 'jane@example.com', phone: '123-456-7890' }
  };

  it('renders minimal details by default', () => {
    render(<CandidateCard candidate={minimalCandidate} />);
    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    expect(screen.getByText('React, Python')).toBeInTheDocument();
    expect(screen.getByText('5 years')).toBeInTheDocument();
    expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /show all details/i })).toBeInTheDocument();
  });

  it('opens modal to show all details on button click', () => {
    render(<CandidateCard candidate={minimalCandidate} />);
    fireEvent.click(screen.getByRole('button', { name: /show all details/i }));
    
    // Check if modal is opened (dialog should be visible)
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Jane Doe', { selector: 'h2' })).toBeInTheDocument(); // Modal title
    
    // Check if all details are shown in modal
    expect(screen.getByText('jane@example.com')).toBeInTheDocument();
    expect(screen.getByText('123-456-7890')).toBeInTheDocument();
  });

  it('handles missing fields without error', () => {
    const incompleteCandidate = { id: '2', name: 'John', skills: [], experience: '' };
    render(<CandidateCard candidate={incompleteCandidate} />);
    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText(/no skills listed/i)).toBeInTheDocument();
    expect(screen.getByText(/not provided/i)).toBeInTheDocument(); // For experience and location
  });

  it('truncates long lists with ellipsis', () => {
    const longSkills = Array(20).fill('Skill').map((s, i) => s + i);
    render(<CandidateCard candidate={{ ...minimalCandidate, skills: longSkills }} />);
    expect(screen.getByText(/Skill0, Skill1, Skill2/)).toBeInTheDocument();
    expect(screen.getByText(/…/)).toBeInTheDocument();
  });

  it('button is accessible by keyboard and screen reader', () => {
    render(<CandidateCard candidate={minimalCandidate} />);
    const button = screen.getByRole('button', { name: /show all details/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute('type', 'button');
  });

  it('displays location correctly when provided', () => {
    render(<CandidateCard candidate={minimalCandidate} />);
    expect(screen.getByText('Location:')).toBeInTheDocument();
    expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
  });

  it('shows "Not provided" for missing location', () => {
    const candidateWithoutLocation = { ...minimalCandidate, location: undefined };
    render(<CandidateCard candidate={candidateWithoutLocation} />);
    expect(screen.getByText('Location:')).toBeInTheDocument();
    expect(screen.getByText('Not provided')).toBeInTheDocument();
  });
});