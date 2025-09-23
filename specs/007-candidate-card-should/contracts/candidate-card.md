# Contract: Candidate Card Minimal Details (Frontend)

## Component: CandidateCard
- Props:
  - candidate: {
      id: string,
      name: string,
      skills: string[],
      experience: string | number,
      [otherDetails]: any
    }
- Behavior:
  - Renders name, skills, experience by default
  - Renders "Show all details" button
  - On button click, expands to show all candidate details
  - Handles missing or long data gracefully

## Contract Test (Jest)
- Renders minimal details by default
- Expands to show all details on button click
- Handles missing fields without error
- Truncates long lists with ellipsis
- Button is accessible by keyboard and screen reader
