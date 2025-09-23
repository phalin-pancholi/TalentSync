# Frontend Components Documentation

## CandidateCard Component

A clean, minimal candidate card component that displays essential candidate information with a "Show all details" modal for viewing complete information.

### Features

- **Minimal Display**: Shows only name, skills (truncated), and experience by default
- **Modal Details**: Click "Show all details" to open a modal with complete candidate information
- **Missing Data Handling**: Gracefully handles missing fields with appropriate placeholders
- **Long Data Truncation**: Automatically truncates long skill lists with ellipsis
- **Full Accessibility**: Keyboard navigable with proper ARIA labels and screen reader support
- **Responsive**: Works on desktop and mobile devices

### Usage

```jsx
import CandidateCard from './components/CandidateCard';

const candidate = {
  id: '1',
  name: 'Jane Doe',
  skills: ['React', 'Python', 'JavaScript'],
  experience: '5 years',
  otherDetails: {
    email: 'jane@example.com',
    phone: '+1234567890',
    education: 'Computer Science',
    resume: 'Resume uploaded'
  }
};

<CandidateCard candidate={candidate} />
```

### Props

#### `candidate` (object, required)

The candidate data object with the following structure:

- `id` (string): Unique identifier
- `name` (string): Candidate's full name
- `skills` (array): Array of skill strings
- `experience` (string | number): Experience description or years
- `otherDetails` (object): Additional candidate information
  - `email` (string): Email address
  - `phone` (string): Phone number
  - `education` (string): Education background
  - `resume` (string): Resume status or file info
  - Any other custom fields

### Behavior

#### Minimal View (Default)
- Displays candidate name prominently
- Shows up to 3 skills, with "... (+N more)" for longer lists
- Shows experience as provided
- Displays "Show all details" button

#### Modal View
- Opens on "Show all details" button click
- Organized sections: Skills (as badges), Experience, Contact Info, Additional Details
- Scrollable for long content
- Close with X button or clicking outside

#### Missing Data
- Skills: Shows "No skills listed" if empty
- Experience: Shows "No experience listed" if empty
- Other fields: Only shown if present

### Styling

Built with Tailwind CSS using the design system tokens:
- `bg-card`, `border-border` for card styling
- `text-foreground`, `text-muted-foreground` for typography
- `hover:shadow-md` for interaction feedback
- Responsive grid layout in modal

### Accessibility

- **Keyboard Navigation**: All interactive elements are keyboard accessible
- **Screen Readers**: Proper ARIA labels and semantic HTML
- **Focus Management**: Clear focus indicators and logical tab order
- **Modal Accessibility**: Proper dialog role and focus trapping

### Integration

Used within `CandidateList` component which handles:
- Action buttons overlay (edit, delete, etc.)
- Data transformation from backend format
- Grid layout for multiple cards

### Testing

Unit tests available in `__tests__/CandidateCard.test.js` covering:
- Minimal details rendering
- Modal functionality
- Missing data handling
- Long data truncation
- Accessibility features
    location: 'San Francisco, CA'
  }
};

<CandidateCard candidate={candidate} />
```

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `candidate` | Object | Yes | Candidate data object |

#### Candidate Object Structure

```typescript
{
  id: string;              // Unique identifier
  name: string;            // Candidate name (displayed prominently)
  skills: string[];        // Array of skills (first 3 shown by default)
  experience: string;      // Experience description
  otherDetails?: {         // Additional details (shown when expanded)
    [key: string]: any;    // Any additional properties
  }
}
```

### Features

- **Minimal Display**: Shows only name, skills (first 3), and experience by default
- **Expandable**: "Show all details" button reveals additional information
- **Missing Data Handling**: Gracefully handles missing fields with placeholders
- **Long Data Truncation**: Automatically truncates long skill lists with "... (+X more)"
- **Accessibility**: Full keyboard navigation and screen reader support
- **Responsive**: Works on mobile, tablet, and desktop

### Styling

Uses Tailwind CSS classes and follows the design system:
- `bg-card`, `border-border` for theming
- `text-foreground`, `text-muted-foreground` for text colors
- `bg-primary`, `text-primary-foreground` for the action button
- Hover and focus states for accessibility

### Accessibility Features

- ARIA labels for the expand/collapse button
- Keyboard navigation support (Tab to button, Enter/Space to activate)
- Screen reader friendly with descriptive text
- Focus management with proper focus rings

## CandidateList Component

A wrapper component that displays multiple candidate cards with action buttons.

### Usage

```jsx
import CandidateList from './components/CandidateList';

<CandidateList 
  candidates={candidatesArray}
  candidateExtraDetails={extraDetailsObject}
  onEdit={handleEdit}
  onDelete={handleDelete}
  onGenerateProfileSummary={generateProfileSummary}
  onOpenExtraDetailsDialog={openExtraDetailsDialog}
  generatingProfileSummary={generatingProfileSummary}
  searchTerm={searchTerm}
  onAddFirst={handleAddFirst}
/>
```

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `candidates` | Array | No | Array of candidate objects (default: []) |
| `candidateExtraDetails` | Object | No | Extra details keyed by candidate ID |
| `onEdit` | Function | No | Edit button click handler |
| `onDelete` | Function | No | Delete button click handler |
| `onGenerateProfileSummary` | Function | No | Generate PDF button handler |
| `onOpenExtraDetailsDialog` | Function | No | Upload extra details handler |
| `generatingProfileSummary` | Object | No | Loading states for PDF generation |
| `searchTerm` | String | No | Current search term for empty state |
| `onAddFirst` | Function | No | Add first candidate button handler |

### Features

- **Grid Layout**: Responsive grid (1 col mobile, 2 cols tablet, 3 cols desktop)
- **Action Buttons**: Overlay buttons for edit, delete, PDF generation, extra details
- **Empty States**: Handles both "no candidates" and "no search results" states
- **Loading States**: Shows spinners for async operations

## Candidate Model

Helper class for working with candidate data.

### Usage

```jsx
import { Candidate } from './lib/models/candidate';

const candidate = new Candidate({
  id: '1',
  name: 'John Doe',
  skills: ['JavaScript', 'React'],
  experience: '3 years',
  email: 'john@example.com'
});

const minimal = candidate.getMinimalDetails();
const all = candidate.getAllDetails();
const isValid = candidate.isValid();
```

### Methods

- `getMinimalDetails()`: Returns object with name, skills, experience
- `getAllDetails()`: Returns complete candidate object
- `isValid()`: Returns true if candidate has required id and name