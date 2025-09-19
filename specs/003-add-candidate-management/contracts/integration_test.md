# Candidate Management and Navigation Update: Integration Test

## Scenario: Full Candidate CRUD and Document Upload

### Given
- The application is running with backend and frontend started
- MongoDB is initialized with `init-mongo.js` (dummy data present)

### When
1. User navigates to the main screen
2. User sees Job and Candidate buttons in the navigation bar
3. User clicks Candidate button
4. User creates a candidate via form (name, email, skills)
5. User uploads a candidate document (PDF, DOCX, or TXT)
6. User views the candidate list
7. User updates a candidate's information
8. User deletes a candidate

### Then
- Candidate is created and visible in the list
- Uploaded document is stored and linked to candidate
- Candidate can be updated and deleted
- Navigation bar shows Job and Candidate buttons (no Home button)
- All operations reflect in the database (MongoDB)

---

This scenario validates the end-to-end flow for candidate management and navigation updates.
