// MongoDB initialization script
db = db.getSiblingDB('talentsync_db');

// Create collections
db.createCollection('job_postings');
db.createCollection('candidates');
db.createCollection('documents');

// Create indexes for better performance
db.job_postings.createIndex({ "id": 1 }, { unique: true });
db.job_postings.createIndex({ "created_at": -1 });
db.job_postings.createIndex({ "department": 1 });
db.job_postings.createIndex({ "skills": 1 });

// Create indexes for candidates
db.candidates.createIndex({ "email": 1 }, { unique: true });
db.candidates.createIndex({ "skills": 1 });
db.candidates.createIndex({ "created_at": -1 });

// Create indexes for documents
db.documents.createIndex({ "candidate_id": 1 });
db.documents.createIndex({ "file_type": 1 });

// Insert some sample data if needed
db.job_postings.insertOne({
    id: "sample-job-1",
    title: "Sample Job Posting",
    description: "This is a sample job posting created during initialization",
    skills: ["JavaScript", "React", "Node.js"],
    experience_level: "Mid",
    department: "Engineering",
    location: "Remote",
    created_at: new Date(),
    updated_at: new Date()
});

// Insert sample candidates
const candidateId1 = new ObjectId();
const candidateId2 = new ObjectId();
const documentId1 = new ObjectId();
const documentId2 = new ObjectId();

db.candidates.insertMany([
    {
        _id: candidateId1,
        name: "Alice Johnson",
        email: "alice.johnson@email.com",
        phone: "+1234567890",
        skills: ["Python", "FastAPI", "MongoDB"],
        created_at: new Date(),
        updated_at: new Date(),
        document_id: documentId1
    },
    {
        _id: candidateId2,
        name: "Bob Smith", 
        email: "bob.smith@email.com",
        phone: "+1987654321",
        skills: ["JavaScript", "React", "Node.js"],
        created_at: new Date(),
        updated_at: new Date(),
        document_id: documentId2
    }
]);

// Insert sample documents
db.documents.insertMany([
    {
        _id: documentId1,
        candidate_id: candidateId1,
        file_name: "alice_resume.pdf",
        file_type: "PDF",
        content_text: "Alice Johnson - Senior Python Developer with 5 years experience in FastAPI and MongoDB...",
        upload_date: new Date(),
        raw_file_path: "/uploads/alice_resume.pdf"
    },
    {
        _id: documentId2,
        candidate_id: candidateId2,
        file_name: "bob_resume.docx",
        file_type: "DOCX", 
        content_text: "Bob Smith - Full Stack JavaScript Developer specializing in React and Node.js...",
        upload_date: new Date(),
        raw_file_path: "/uploads/bob_resume.docx"
    }
]);

print('Database initialized successfully');