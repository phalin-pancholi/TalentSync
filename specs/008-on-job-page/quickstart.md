# Quickstart: Candidate Location and Experience Fields

## Prerequisites
- Backend and frontend running
- Candidate data available in the system

## Steps
1. **Add or update a candidate with location and experience fields**:
   - Via API: Use the `/candidates` POST or PUT endpoints with `location` and `experience` fields
   - Via form: Include location and experience in the candidate creation form
   - Via LLM extraction: Upload a resume/CV that contains location and experience information

2. **View candidates on the Job Page**:
   - Navigate to any job page
   - Go to the candidate matching section
   - View candidate cards to see location and experience displayed

3. **Verify display functionality**:
   - Check that each card shows location and experience when available
   - Verify "Not provided" is shown when location or experience is missing
   - Open the "Show all details" modal to see full candidate information

4. **Test edge cases**:
   - Create a candidate with only location (no experience)
   - Create a candidate with only experience (no location)
   - Create a candidate with neither field
   - Verify all cases display appropriately

## Validation
- All candidate cards show correct location and experience data or fallback message
- Modal displays complete candidate information including location and experience
- No errors in backend or frontend logs
- LLM extraction properly populates location and experience from resume text

## API Examples

### Create candidate with location and experience
```bash
curl -X POST "http://localhost:8001/api/candidates/json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "skills": ["Python", "React"],
    "location": "Austin, TX",
    "experience": "5 years"
  }'
```

### Update candidate location
```bash
curl -X PUT "http://localhost:8001/api/candidates/{candidate_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Remote"
  }'
```

## Frontend Usage
The CandidateCard component automatically displays location and experience when available:

```jsx
<CandidateCard 
  candidate={{
    id: "123",
    name: "Jane Smith",
    skills: ["JavaScript", "Node.js"],
    location: "San Francisco, CA",
    experience: "3 years"
  }} 
/>
```
