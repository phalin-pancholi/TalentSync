import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import { toast } from 'sonner';
import Candidates from '../Candidates';

// Mock dependencies
jest.mock('axios');
jest.mock('sonner');

const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockedToast = toast as jest.Mocked<typeof toast>;

describe('Candidates Component - Profile Summary', () => {
  const mockCandidates = [
    {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      phone: '+1-555-0123',
      skills: ['Python', 'JavaScript', 'React'],
      experience: '5+ years in software development',
      education: 'Bachelor of Computer Science',
      summary: 'Experienced full-stack developer',
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    },
    {
      id: '2',
      name: 'Jane Smith',
      email: 'jane@example.com',
      skills: ['Python', 'Data Science'],
      created_at: '2023-01-02T00:00:00Z',
      updated_at: '2023-01-02T00:00:00Z'
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    mockedAxios.get.mockResolvedValue({ data: mockCandidates });
  });

  test('renders profile summary button for each candidate', async () => {
    render(<Candidates />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Check that profile summary buttons are rendered
    const profileSummaryButtons = screen.getAllByTitle('Generate Profile Summary PDF');
    expect(profileSummaryButtons).toHaveLength(2);
  });

  test('profile summary button has correct styling and icon', async () => {
    render(<Candidates />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const profileSummaryButton = screen.getAllByTitle('Generate Profile Summary PDF')[0];
    
    // Check button styling
    expect(profileSummaryButton).toHaveClass('text-purple-600');
    expect(profileSummaryButton).toHaveClass('hover:text-purple-700');
    
    // Check for download icon (Lucide Download component)
    const downloadIcon = profileSummaryButton.querySelector('svg');
    expect(downloadIcon).toBeInTheDocument();
  });

  test('generates profile summary on button click', async () => {
    const mockBlob = new Blob(['fake pdf content'], { type: 'application/pdf' });
    mockedAxios.post.mockResolvedValue({ data: mockBlob });

    // Mock URL.createObjectURL and related functions
    global.URL.createObjectURL = jest.fn(() => 'mock-url');
    global.URL.revokeObjectURL = jest.fn();
    
    // Mock document.createElement and link.click
    const mockLink = {
      href: '',
      download: '',
      click: jest.fn(),
    };
    const originalCreateElement = document.createElement;
    document.createElement = jest.fn().mockImplementation((tagName) => {
      if (tagName === 'a') {
        return mockLink;
      }
      return originalCreateElement.call(document, tagName);
    });
    
    // Mock document.body methods
    document.body.appendChild = jest.fn();
    document.body.removeChild = jest.fn();

    render(<Candidates />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const profileSummaryButton = screen.getAllByTitle('Generate Profile Summary PDF')[0];
    fireEvent.click(profileSummaryButton);

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:8001/api/candidates/1/profile-summary',
        {},
        {
          responseType: 'blob',
          headers: {
            'Accept': 'application/pdf'
          }
        }
      );
    });

    // Check that download was triggered
    expect(global.URL.createObjectURL).toHaveBeenCalledWith(mockBlob);
    expect(mockLink.download).toBe('profile_summary_John_Doe_1.pdf');
    expect(mockLink.click).toHaveBeenCalled();
    expect(document.body.appendChild).toHaveBeenCalledWith(mockLink);
    expect(document.body.removeChild).toHaveBeenCalledWith(mockLink);
    expect(global.URL.revokeObjectURL).toHaveBeenCalledWith('mock-url');

    // Check success toast
    expect(mockedToast.success).toHaveBeenCalledWith('Profile summary generated successfully for John Doe');

    // Restore original functions
    document.createElement = originalCreateElement;
  });

  test('shows loading state during profile summary generation', async () => {
    // Create a promise that we can control
    let resolvePromise: (value: any) => void;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    mockedAxios.post.mockReturnValue(pendingPromise as any);

    render(<Candidates />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const profileSummaryButton = screen.getAllByTitle('Generate Profile Summary PDF')[0];
    fireEvent.click(profileSummaryButton);

    // Check that button shows loading state
    await waitFor(() => {
      expect(profileSummaryButton).toBeDisabled();
    });

    // Check for loading spinner
    const spinner = profileSummaryButton.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();

    // Resolve the promise to complete the test
    resolvePromise!({ data: new Blob(['test'], { type: 'application/pdf' }) });
  });

  test('handles profile summary generation errors', async () => {
    const errorResponse = {
      response: {
        status: 500,
        data: { detail: 'Internal server error' }
      }
    };
    mockedAxios.post.mockRejectedValue(errorResponse);

    render(<Candidates />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const profileSummaryButton = screen.getAllByTitle('Generate Profile Summary PDF')[0];
    fireEvent.click(profileSummaryButton);

    await waitFor(() => {
      expect(mockedToast.error).toHaveBeenCalledWith('Failed to generate profile summary. Please try again.');
    });
  });

  test('handles 404 error for non-existent candidate', async () => {
    const errorResponse = {
      response: {
        status: 404
      }
    };
    mockedAxios.post.mockRejectedValue(errorResponse);

    render(<Candidates />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const profileSummaryButton = screen.getAllByTitle('Generate Profile Summary PDF')[0];
    fireEvent.click(profileSummaryButton);

    await waitFor(() => {
      expect(mockedToast.error).toHaveBeenCalledWith('Candidate not found');
    });
  });

  test('handles LLM service unavailable error', async () => {
    const errorResponse = {
      response: {
        status: 503
      }
    };
    mockedAxios.post.mockRejectedValue(errorResponse);

    render(<Candidates />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const profileSummaryButton = screen.getAllByTitle('Generate Profile Summary PDF')[0];
    fireEvent.click(profileSummaryButton);

    await waitFor(() => {
      expect(mockedToast.error).toHaveBeenCalledWith('LLM service is currently unavailable. Please try again later.');
    });
  });

  test('prevents multiple simultaneous profile summary generations for same candidate', async () => {
    const mockBlob = new Blob(['fake pdf content'], { type: 'application/pdf' });
    
    // Create a slow-resolving promise
    let resolvePromise: (value: any) => void;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    mockedAxios.post.mockReturnValue(pendingPromise as any);

    render(<Candidates />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const profileSummaryButton = screen.getAllByTitle('Generate Profile Summary PDF')[0];
    
    // Click button multiple times
    fireEvent.click(profileSummaryButton);
    fireEvent.click(profileSummaryButton);
    fireEvent.click(profileSummaryButton);

    // Should only call API once
    expect(mockedAxios.post).toHaveBeenCalledTimes(1);

    // Button should be disabled
    expect(profileSummaryButton).toBeDisabled();

    // Resolve the promise
    resolvePromise!({ data: mockBlob });
  });

  test('sanitizes filename for download', async () => {
    const candidateWithSpecialChars = {
      ...mockCandidates[0],
      name: 'John O\'Connor / Smith'
    };
    
    mockedAxios.get.mockResolvedValue({ data: [candidateWithSpecialChars] });
    
    const mockBlob = new Blob(['fake pdf content'], { type: 'application/pdf' });
    mockedAxios.post.mockResolvedValue({ data: mockBlob });

    global.URL.createObjectURL = jest.fn(() => 'mock-url');
    global.URL.revokeObjectURL = jest.fn();
    
    const mockLink = {
      href: '',
      download: '',
      click: jest.fn(),
    };
    document.createElement = jest.fn().mockReturnValue(mockLink);
    document.body.appendChild = jest.fn();
    document.body.removeChild = jest.fn();

    render(<Candidates />);

    await waitFor(() => {
      expect(screen.getByText('John O\'Connor / Smith')).toBeInTheDocument();
    });

    const profileSummaryButton = screen.getByTitle('Generate Profile Summary PDF');
    fireEvent.click(profileSummaryButton);

    await waitFor(() => {
      expect(mockLink.download).toBe('profile_summary_John_O_Connor___Smith_1.pdf');
    });
  });
});