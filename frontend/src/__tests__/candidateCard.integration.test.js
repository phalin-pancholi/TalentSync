import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CandidateCard from '../components/CandidateCard';

describe('CandidateCard Integration Tests - Location and Experience', () => {
  test('should display candidate location and experience when provided', () => {
    const candidateWithLocationAndExperience = {
      id: '1',
      name: 'John Doe',
      skills: ['React', 'Node.js', 'Python'],
      location: 'San Francisco, CA',
      experience: '5 years'
    };

    render(<CandidateCard candidate={candidateWithLocationAndExperience} />);

    // Check that location is displayed
    expect(screen.getByText('Location:')).toBeInTheDocument();
    expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();

    // Check that experience is displayed
    expect(screen.getByText('Experience:')).toBeInTheDocument();
    expect(screen.getByText('5 years')).toBeInTheDocument();
  });

  test('should show "Not provided" when location is missing', () => {
    const candidateWithoutLocation = {
      id: '2',
      name: 'Jane Smith',
      skills: ['Java', 'Spring'],
      experience: '3 years'
    };

    render(<CandidateCard candidate={candidateWithoutLocation} />);

    // Check that location shows "Not provided"
    expect(screen.getByText('Location:')).toBeInTheDocument();
    expect(screen.getByText('Not provided')).toBeInTheDocument();

    // Experience should still be shown
    expect(screen.getByText('Experience:')).toBeInTheDocument();
    expect(screen.getByText('3 years')).toBeInTheDocument();
  });

  test('should show "Not provided" when experience is missing', () => {
    const candidateWithoutExperience = {
      id: '3',
      name: 'Bob Johnson',
      skills: ['JavaScript', 'Vue.js'],
      location: 'New York, NY'
    };

    render(<CandidateCard candidate={candidateWithoutExperience} />);

    // Check that experience shows "Not provided"
    expect(screen.getByText('Experience:')).toBeInTheDocument();
    expect(screen.getByText('Not provided')).toBeInTheDocument();

    // Location should still be shown
    expect(screen.getByText('Location:')).toBeInTheDocument();
    expect(screen.getByText('New York, NY')).toBeInTheDocument();
  });

  test('should show "Not provided" for both location and experience when missing', () => {
    const candidateWithoutLocationAndExperience = {
      id: '4',
      name: 'Alice Wilson',
      skills: ['Python', 'Django']
    };

    render(<CandidateCard candidate={candidateWithoutLocationAndExperience} />);

    // Check that both location and experience show "Not provided"
    const notProvidedTexts = screen.getAllByText('Not provided');
    expect(notProvidedTexts).toHaveLength(2);

    expect(screen.getByText('Location:')).toBeInTheDocument();
    expect(screen.getByText('Experience:')).toBeInTheDocument();
  });

  test('should display location and experience in modal when "Show all details" is clicked', () => {
    const candidateWithFullDetails = {
      id: '5',
      name: 'Charlie Brown',
      skills: ['React', 'TypeScript', 'GraphQL'],
      location: 'Austin, TX',
      experience: '7 years',
      otherDetails: {
        email: 'charlie@example.com',
        phone: '+1234567890'
      }
    };

    render(<CandidateCard candidate={candidateWithFullDetails} />);

    // Click "Show all details" button
    const showDetailsButton = screen.getByText('Show all details');
    fireEvent.click(showDetailsButton);

    // Check that location and experience are in the modal
    expect(screen.getByText('Austin, TX')).toBeInTheDocument();
    expect(screen.getByText('7 years')).toBeInTheDocument();
  });

  test('should handle empty string values for location and experience', () => {
    const candidateWithEmptyFields = {
      id: '6',
      name: 'Dave Davis',
      skills: ['Java'],
      location: '',
      experience: ''
    };

    render(<CandidateCard candidate={candidateWithEmptyFields} />);

    // Empty strings should be treated as "Not provided"
    const notProvidedTexts = screen.getAllByText('Not provided');
    expect(notProvidedTexts).toHaveLength(2);
  });
});