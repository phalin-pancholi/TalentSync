// MongoDB initialization script
db = db.getSiblingDB('talentsync_db');

// Create collections
db.createCollection('job_postings');
db.createCollection('candidates');

// Create indexes for better performance
db.job_postings.createIndex({ "id": 1 }, { unique: true });
db.job_postings.createIndex({ "created_at": -1 });
db.job_postings.createIndex({ "department": 1 });
db.job_postings.createIndex({ "skills": 1 });

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

print('Database initialized successfully');