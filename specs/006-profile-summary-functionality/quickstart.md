# Profile Summary Functionality - Quickstart Guide

This guide provides step-by-step instructions for using the new Profile Summary functionality in TalentSync.

## Overview

The Profile Summary feature allows recruiters and hiring managers to generate professional PDF summaries for candidates using AI-powered content generation. The system collects all available candidate data (structured information, unstructured resume text, and feedback) and creates a comprehensive profile summary document.

## Prerequisites

- TalentSync backend and frontend running
- Google API Key configured for Gemini LLM (set `GOOGLE_API_KEY` environment variable)
- Candidate records with data in the system

## Quick Start

### 1. Navigate to Candidates Page

1. Open TalentSync in your browser
2. Go to the "Candidates" section
3. You'll see a list of candidate cards

### 2. Generate Profile Summary

1. **Locate the candidate** for whom you want to generate a profile summary
2. **Click the purple download button** (📥) in the top-right corner of the candidate card
   - Button tooltip: "Generate Profile Summary PDF"
3. **Wait for generation** - the button will show a loading spinner
4. **Download starts automatically** when generation completes
5. **Success notification** appears when the PDF is ready

### 3. What Gets Included

The profile summary includes:
- **Candidate Information**: Name, contact details, skills
- **Professional Summary**: AI-generated overview based on experience and skills
- **Education**: Educational background and qualifications  
- **Key Strengths**: Highlighted professional strengths
- **Technical Skills**: Organized by category (Programming, Frontend, Backend, etc.)
- **Professional Experience**: Work history and achievements
- **Feedback Data**: Any extra details or interview feedback uploaded

## Advanced Usage

### Adding Extra Details for Richer Summaries

1. **Click the green upload button** (📤) on any candidate card
2. **Upload feedback files** (text or PDF) containing:
   - Interview feedback
   - Performance reviews
   - Additional skills assessments
   - Project summaries
3. **Generate profile summary** - the AI will incorporate this additional context

### Error Handling

The system gracefully handles various scenarios:

- **Missing Data**: Creates summary with available information
- **LLM Service Down**: Shows clear error message with retry suggestion
- **Network Issues**: Displays appropriate error notifications
- **Large Files**: Handles timeout scenarios appropriately

## Testing the Feature

### Manual Testing Steps

1. **Create Test Candidate**:
   ```json
   {
     "name": "John Doe",
     "email": "john.doe@example.com",
     "phone": "+1-555-0123",
     "skills": ["Python", "React", "MongoDB"],
     "experience": "5+ years in full-stack development",
     "education": "Bachelor of Computer Science",
     "summary": "Experienced software engineer"
   }
   ```

2. **Add Feedback**:
   - Upload a text file with interview feedback
   - Example: "Excellent problem-solving skills. Strong technical knowledge. Great cultural fit."

3. **Generate Summary**:
   - Click the profile summary button
   - Verify PDF downloads with expected content

### Expected Output Sample

```
PROFILE SUMMARY
John Doe

Professional Summary

Software Engineer with 5+ years of experience in full-stack development, 
specializing in Python, React, and MongoDB. Demonstrated expertise in 
building scalable web applications and strong problem-solving abilities.

Education

Bachelor of Computer Science

Key Strengths

• Excellent problem-solving skills and analytical thinking
• Strong technical knowledge across full-stack technologies  
• Great cultural fit and collaboration abilities
• Experience with modern development practices

Technical Skills

Programming Languages: Python
Frontend: React
Databases: MongoDB

Professional Experience

Experienced software engineer with 5+ years in full-stack development.
Contributed to building and maintaining scalable applications.

Project Summary:
Successfully delivered multiple projects using modern web technologies.

Generated on 2025-09-22 10:30:15 UTC by TalentSync
```

## API Reference

### Generate Profile Summary Endpoint

```http
POST /api/candidates/{candidate_id}/profile-summary
```

**Response**: PDF file (application/pdf)

**Error Codes**:
- `404`: Candidate not found
- `500`: Generation failed
- `503`: LLM service unavailable

## Troubleshooting

### Common Issues

1. **"LLM service unavailable" error**:
   - Check `GOOGLE_API_KEY` environment variable
   - Verify Gemini API access and quota
   - Check network connectivity

2. **PDF not downloading**:
   - Check browser popup blockers
   - Verify file download permissions
   - Try a different browser

3. **Poor quality summaries**:
   - Add more candidate data (experience, education)
   - Upload additional feedback files
   - Ensure resume text is properly extracted

4. **Button not responding**:
   - Check browser console for JavaScript errors
   - Verify backend API is running
   - Refresh the page and try again

### Backend Logs

Monitor these log messages:
```
INFO: Profile summary generated successfully for candidate: John Doe
ERROR: Profile summary generation failed for candidate abc123: LLM extraction failed
WARN: Could not retrieve extra details for candidate abc123
```

## Performance Notes

- **Generation Time**: Typically 3-10 seconds depending on data size
- **File Size**: PDF files are generally 50-200KB
- **Concurrent Requests**: System handles multiple simultaneous generations
- **Rate Limits**: Respects Gemini API rate limits

## Security Considerations

- **Data Privacy**: Candidate data is sent to Gemini LLM - ensure compliance
- **Access Control**: Only authorized users can generate summaries
- **Audit Logging**: All generation events are logged for compliance
- **File Handling**: PDFs are generated on-demand, not stored permanently

## Next Steps

- Review generated summaries for quality
- Gather user feedback on format and content
- Consider adding custom templates
- Monitor usage and API costs
- Plan for additional AI features

For technical support or feature requests, contact the development team.