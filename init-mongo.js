// MongoDB initialization script
db = db.getSiblingDB('talentsync_db');

// Drop existing collections to start fresh
db.job_postings.drop();
db.candidates.drop();
db.documents.drop();

// Create collections
db.createCollection('job_postings');
db.createCollection('candidates');
db.createCollection('documents');

// Create indexes for better performance
db.job_postings.createIndex({ "id": 1 }, { unique: true });
db.job_postings.createIndex({ "created_at": -1 });
db.job_postings.createIndex({ "department": 1 });
db.job_postings.createIndex({ "skills": 1 });
db.job_postings.createIndex({ "experience_level": 1 });
db.job_postings.createIndex({ "location": 1 });

// Create indexes for candidates
db.candidates.createIndex({ "email": 1 }, { unique: true });
db.candidates.createIndex({ "skills": 1 });
db.candidates.createIndex({ "created_at": -1 });
db.candidates.createIndex({ "location": 1 });
db.candidates.createIndex({ "experience_level": 1 });

// Create indexes for documents
db.documents.createIndex({ "candidate_id": 1 });
db.documents.createIndex({ "file_type": 1 });

// Insert 10 realistic job postings
const jobPostings = [
    {
        id: "senior-fullstack-dev-001",
        title: "Senior Full Stack Developer",
        description: "We are seeking a highly skilled Senior Full Stack Developer to join our dynamic engineering team. You will be responsible for developing and maintaining web applications using modern technologies like React, Node.js, and cloud platforms. The ideal candidate should have strong problem-solving skills and experience with microservices architecture.",
        skills: ["React", "Node.js", "TypeScript", "AWS", "MongoDB", "Docker"],
        experience_level: "Senior",
        department: "Engineering",
        location: "San Francisco, CA",
        salary_range: "$140,000 - $180,000",
        created_at: new Date("2024-09-01"),
        updated_at: new Date("2024-09-01")
    },
    {
        id: "python-data-scientist-002",
        title: "Data Scientist - Machine Learning",
        description: "Join our AI/ML team to develop cutting-edge machine learning models and data pipelines. You'll work on large-scale data analysis, model deployment, and collaborate with cross-functional teams to drive data-driven decisions. Experience with Python, TensorFlow, and cloud ML platforms is essential.",
        skills: ["Python", "TensorFlow", "Pandas", "SQL", "AWS", "Kubernetes", "MLOps"],
        experience_level: "Mid-level",
        department: "Data Science",
        location: "New York, NY",
        salary_range: "$120,000 - $150,000",
        created_at: new Date("2024-09-02"),
        updated_at: new Date("2024-09-02")
    },
    {
        id: "frontend-react-dev-003",
        title: "Frontend Developer - React",
        description: "We're looking for a passionate Frontend Developer to create amazing user experiences with React and modern JavaScript. You'll work closely with our design team to implement responsive, accessible web applications. Knowledge of state management, testing, and performance optimization is highly valued.",
        skills: ["React", "JavaScript", "CSS3", "Redux", "Jest", "Webpack"],
        experience_level: "Junior",
        department: "Engineering",
        location: "Austin, TX",
        salary_range: "$80,000 - $100,000",
        created_at: new Date("2024-09-03"),
        updated_at: new Date("2024-09-03")
    },
    {
        id: "devops-engineer-004",
        title: "DevOps Engineer",
        description: "Seeking an experienced DevOps Engineer to manage our cloud infrastructure and CI/CD pipelines. You'll be responsible for automating deployment processes, monitoring system performance, and ensuring high availability of our services. Strong background in containerization and cloud platforms required.",
        skills: ["Docker", "Kubernetes", "AWS", "Terraform", "Jenkins", "Python", "Monitoring"],
        experience_level: "Senior",
        department: "Infrastructure",
        location: "Seattle, WA",
        salary_range: "$130,000 - $170,000",
        created_at: new Date("2024-09-04"),
        updated_at: new Date("2024-09-04")
    },
    {
        id: "mobile-ios-dev-005",
        title: "iOS Developer",
        description: "Join our mobile team to build innovative iOS applications. You'll work on features that millions of users interact with daily, focusing on performance, user experience, and code quality. Experience with Swift, UIKit, and modern iOS development practices is required.",
        skills: ["Swift", "UIKit", "SwiftUI", "Core Data", "REST APIs", "Git"],
        experience_level: "Mid-level",
        department: "Mobile",
        location: "Los Angeles, CA",
        salary_range: "$110,000 - $140,000",
        created_at: new Date("2024-09-05"),
        updated_at: new Date("2024-09-05")
    },
    {
        id: "backend-java-dev-006",
        title: "Backend Java Developer",
        description: "We're seeking a skilled Backend Java Developer to work on our enterprise-grade applications. You'll design and implement scalable microservices, work with databases, and ensure system reliability. Strong knowledge of Spring Boot, databases, and distributed systems is essential.",
        skills: ["Java", "Spring Boot", "PostgreSQL", "Microservices", "Kafka", "Redis"],
        experience_level: "Senior",
        department: "Engineering",
        location: "Chicago, IL",
        salary_range: "$125,000 - $160,000",
        created_at: new Date("2024-09-06"),
        updated_at: new Date("2024-09-06")
    },
    {
        id: "qa-automation-007",
        title: "QA Automation Engineer",
        description: "Looking for a detail-oriented QA Automation Engineer to ensure the quality of our software products. You'll develop and maintain automated test suites, work closely with development teams, and help improve our testing processes. Experience with test automation frameworks and CI/CD integration required.",
        skills: ["Selenium", "Python", "Jest", "Cypress", "API Testing", "CI/CD"],
        experience_level: "Mid-level",
        department: "Quality Assurance",
        location: "Denver, CO",
        salary_range: "$95,000 - $120,000",
        created_at: new Date("2024-09-07"),
        updated_at: new Date("2024-09-07")
    },
    {
        id: "product-manager-008",
        title: "Product Manager - Growth",
        description: "Seeking an experienced Product Manager to drive growth initiatives and product strategy. You'll work with engineering, design, and marketing teams to define product requirements, analyze user data, and deliver features that drive business growth. Strong analytical and communication skills required.",
        skills: ["Product Strategy", "Analytics", "SQL", "A/B Testing", "Agile", "User Research"],
        experience_level: "Senior",
        department: "Product",
        location: "Remote",
        salary_range: "$140,000 - $170,000",
        created_at: new Date("2024-09-08"),
        updated_at: new Date("2024-09-08")
    },
    {
        id: "ui-ux-designer-009",
        title: "UI/UX Designer",
        description: "Join our design team to create intuitive and beautiful user experiences. You'll conduct user research, create wireframes and prototypes, and collaborate with engineering to implement designs. Portfolio demonstrating strong design thinking and user-centered design approach required.",
        skills: ["Figma", "Sketch", "User Research", "Prototyping", "Design Systems", "HTML/CSS"],
        experience_level: "Mid-level",
        department: "Design",
        location: "Portland, OR",
        salary_range: "$100,000 - $130,000",
        created_at: new Date("2024-09-09"),
        updated_at: new Date("2024-09-09")
    },
    {
        id: "security-engineer-010",
        title: "Cybersecurity Engineer",
        description: "We're looking for a Cybersecurity Engineer to protect our systems and data. You'll implement security measures, conduct vulnerability assessments, and respond to security incidents. Strong background in network security, penetration testing, and security frameworks required.",
        skills: ["Network Security", "Penetration Testing", "Python", "SIEM", "Incident Response", "Compliance"],
        experience_level: "Senior",
        department: "Security",
        location: "Washington, DC",
        salary_range: "$135,000 - $175,000",
        created_at: new Date("2024-09-10"),
        updated_at: new Date("2024-09-10")
    }
];

db.job_postings.insertMany(jobPostings);

// Generate 40 realistic candidates
const candidates = [
    {
        name: "Sarah Chen",
        email: "sarah.chen@email.com",
        phone: "+1-555-0101",
        skills: ["React", "JavaScript", "TypeScript", "Node.js", "GraphQL"],
        location: "San Francisco, CA",
        experience: "5 years in frontend development at tech startups",
        experience_level: "Senior",
        created_at: new Date("2024-08-15"),
        updated_at: new Date("2024-08-15")
    },
    {
        name: "Michael Rodriguez",
        email: "michael.rodriguez@email.com",
        phone: "+1-555-0102",
        skills: ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
        location: "Austin, TX",
        experience: "3 years building web applications with Python",
        experience_level: "Mid-level",
        created_at: new Date("2024-08-16"),
        updated_at: new Date("2024-08-16")
    },
    {
        name: "Emily Johnson",
        email: "emily.johnson@email.com",
        phone: "+1-555-0103",
        skills: ["Java", "Spring Boot", "Kubernetes", "Microservices", "MySQL"],
        location: "Chicago, IL",
        experience: "7 years in enterprise Java development",
        experience_level: "Senior",
        created_at: new Date("2024-08-17"),
        updated_at: new Date("2024-08-17")
    },
    {
        name: "David Kim",
        email: "david.kim@email.com",
        phone: "+1-555-0104",
        skills: ["React", "JavaScript", "CSS3", "HTML5", "Figma"],
        location: "New York, NY",
        experience: "2 years as a frontend developer",
        experience_level: "Junior",
        created_at: new Date("2024-08-18"),
        updated_at: new Date("2024-08-18")
    },
    {
        name: "Jessica Martinez",
        email: "jessica.martinez@email.com",
        phone: "+1-555-0105",
        skills: ["Python", "TensorFlow", "Pandas", "SQL", "Machine Learning"],
        location: "Seattle, WA",
        experience: "4 years in data science and ML",
        experience_level: "Mid-level",
        created_at: new Date("2024-08-19"),
        updated_at: new Date("2024-08-19")
    },
    {
        name: "Ryan Thompson",
        email: "ryan.thompson@email.com",
        phone: "+1-555-0106",
        skills: ["Swift", "UIKit", "Core Data", "REST APIs", "iOS"],
        location: "Los Angeles, CA",
        experience: "6 years developing iOS applications",
        experience_level: "Senior",
        created_at: new Date("2024-08-20"),
        updated_at: new Date("2024-08-20")
    },
    {
        name: "Amanda Wilson",
        email: "amanda.wilson@email.com",
        phone: "+1-555-0107",
        skills: ["Docker", "Kubernetes", "AWS", "Terraform", "Jenkins"],
        location: "Denver, CO",
        experience: "5 years in DevOps and cloud infrastructure",
        experience_level: "Senior",
        created_at: new Date("2024-08-21"),
        updated_at: new Date("2024-08-21")
    },
    {
        name: "James Brown",
        email: "james.brown@email.com",
        phone: "+1-555-0108",
        skills: ["JavaScript", "Vue.js", "Node.js", "MongoDB", "Express"],
        location: "Remote",
        experience: "3 years full-stack JavaScript development",
        experience_level: "Mid-level",
        created_at: new Date("2024-08-22"),
        updated_at: new Date("2024-08-22")
    },
    {
        name: "Linda Davis",
        email: "linda.davis@email.com",
        phone: "+1-555-0109",
        skills: ["Selenium", "Python", "Jest", "API Testing", "CI/CD"],
        location: "Portland, OR",
        experience: "4 years in QA automation",
        experience_level: "Mid-level",
        created_at: new Date("2024-08-23"),
        updated_at: new Date("2024-08-23")
    },
    {
        name: "Kevin Lee",
        email: "kevin.lee@email.com",
        phone: "+1-555-0110",
        skills: ["C#", ".NET", "SQL Server", "Azure", "Entity Framework"],
        location: "Dallas, TX",
        experience: "8 years in .NET development",
        experience_level: "Senior",
        created_at: new Date("2024-08-24"),
        updated_at: new Date("2024-08-24")
    },
    {
        name: "Sophie Anderson",
        email: "sophie.anderson@email.com",
        phone: "+1-555-0111",
        skills: ["Figma", "Sketch", "User Research", "Prototyping", "Design Systems"],
        location: "San Francisco, CA",
        experience: "5 years in UI/UX design",
        experience_level: "Senior",
        created_at: new Date("2024-08-25"),
        updated_at: new Date("2024-08-25")
    },
    {
        name: "Robert Garcia",
        email: "robert.garcia@email.com",
        phone: "+1-555-0112",
        skills: ["Network Security", "Python", "Penetration Testing", "SIEM"],
        location: "Washington, DC",
        experience: "6 years in cybersecurity",
        experience_level: "Senior",
        created_at: new Date("2024-08-26"),
        updated_at: new Date("2024-08-26")
    },
    {
        name: "Maria Gonzalez",
        email: "maria.gonzalez@email.com",
        phone: "+1-555-0113",
        skills: ["React", "Redux", "TypeScript", "Jest", "Webpack"],
        location: "Miami, FL",
        experience: "2 years React development",
        experience_level: "Junior",
        created_at: new Date("2024-08-27"),
        updated_at: new Date("2024-08-27")
    },
    {
        name: "Alex Turner",
        email: "alex.turner@email.com",
        phone: "+1-555-0114",
        skills: ["Go", "PostgreSQL", "Redis", "gRPC", "Microservices"],
        location: "Boulder, CO",
        experience: "4 years backend development with Go",
        experience_level: "Mid-level",
        created_at: new Date("2024-08-28"),
        updated_at: new Date("2024-08-28")
    },
    {
        name: "Rachel White",
        email: "rachel.white@email.com",
        phone: "+1-555-0115",
        skills: ["Product Strategy", "Analytics", "SQL", "A/B Testing", "Agile"],
        location: "Boston, MA",
        experience: "7 years in product management",
        experience_level: "Senior",
        created_at: new Date("2024-08-29"),
        updated_at: new Date("2024-08-29")
    },
    {
        name: "Chris Taylor",
        email: "chris.taylor@email.com",
        phone: "+1-555-0116",
        skills: ["Flutter", "Dart", "Firebase", "REST APIs", "Mobile Development"],
        location: "Phoenix, AZ",
        experience: "3 years mobile app development",
        experience_level: "Mid-level",
        created_at: new Date("2024-08-30"),
        updated_at: new Date("2024-08-30")
    },
    {
        name: "Nicole Clark",
        email: "nicole.clark@email.com",
        phone: "+1-555-0117",
        skills: ["Python", "FastAPI", "MongoDB", "Docker", "AWS"],
        location: "Atlanta, GA",
        experience: "5 years Python backend development",
        experience_level: "Senior",
        created_at: new Date("2024-09-01"),
        updated_at: new Date("2024-09-01")
    },
    {
        name: "Daniel Lewis",
        email: "daniel.lewis@email.com",
        phone: "+1-555-0118",
        skills: ["Angular", "TypeScript", "RxJS", "NgRx", "Jasmine"],
        location: "Minneapolis, MN",
        experience: "4 years Angular development",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-02"),
        updated_at: new Date("2024-09-02")
    },
    {
        name: "Stephanie Hall",
        email: "stephanie.hall@email.com",
        phone: "+1-555-0119",
        skills: ["R", "Python", "Statistics", "Machine Learning", "Tableau"],
        location: "Nashville, TN",
        experience: "3 years in data analysis",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-03"),
        updated_at: new Date("2024-09-03")
    },
    {
        name: "Brian Young",
        email: "brian.young@email.com",
        phone: "+1-555-0120",
        skills: ["PHP", "Laravel", "MySQL", "JavaScript", "HTML/CSS"],
        location: "Salt Lake City, UT",
        experience: "6 years PHP web development",
        experience_level: "Senior",
        created_at: new Date("2024-09-04"),
        updated_at: new Date("2024-09-04")
    },
    {
        name: "Melissa King",
        email: "melissa.king@email.com",
        phone: "+1-555-0121",
        skills: ["Ruby", "Rails", "PostgreSQL", "Redis", "Sidekiq"],
        location: "Portland, OR",
        experience: "5 years Ruby on Rails development",
        experience_level: "Senior",
        created_at: new Date("2024-09-05"),
        updated_at: new Date("2024-09-05")
    },
    {
        name: "Justin Wright",
        email: "justin.wright@email.com",
        phone: "+1-555-0122",
        skills: ["Unity", "C#", "3D Graphics", "Game Development", "Blender"],
        location: "San Diego, CA",
        experience: "4 years game development",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-06"),
        updated_at: new Date("2024-09-06")
    },
    {
        name: "Kimberly Scott",
        email: "kimberly.scott@email.com",
        phone: "+1-555-0123",
        skills: ["Salesforce", "Apex", "Lightning", "CRM", "Process Automation"],
        location: "Houston, TX",
        experience: "3 years Salesforce development",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-07"),
        updated_at: new Date("2024-09-07")
    },
    {
        name: "Andrew Green",
        email: "andrew.green@email.com",
        phone: "+1-555-0124",
        skills: ["Scala", "Akka", "Kafka", "Spark", "Functional Programming"],
        location: "San Jose, CA",
        experience: "7 years in big data and distributed systems",
        experience_level: "Senior",
        created_at: new Date("2024-09-08"),
        updated_at: new Date("2024-09-08")
    },
    {
        name: "Lauren Adams",
        email: "lauren.adams@email.com",
        phone: "+1-555-0125",
        skills: ["HTML5", "CSS3", "JavaScript", "Bootstrap", "WordPress"],
        location: "Orlando, FL",
        experience: "1 year frontend development",
        experience_level: "Entry-level",
        created_at: new Date("2024-09-09"),
        updated_at: new Date("2024-09-09")
    },
    {
        name: "Matthew Baker",
        email: "matthew.baker@email.com",
        phone: "+1-555-0126",
        skills: ["Rust", "WebAssembly", "Systems Programming", "Performance"],
        location: "Remote",
        experience: "3 years systems programming with Rust",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-10"),
        updated_at: new Date("2024-09-10")
    },
    {
        name: "Jennifer Nelson",
        email: "jennifer.nelson@email.com",
        phone: "+1-555-0127",
        skills: ["Blockchain", "Solidity", "Web3", "Ethereum", "Smart Contracts"],
        location: "Miami, FL",
        experience: "2 years blockchain development",
        experience_level: "Junior",
        created_at: new Date("2024-09-11"),
        updated_at: new Date("2024-09-11")
    },
    {
        name: "Joshua Carter",
        email: "joshua.carter@email.com",
        phone: "+1-555-0128",
        skills: ["Kotlin", "Android", "Jetpack Compose", "Room", "Retrofit"],
        location: "Raleigh, NC",
        experience: "4 years Android development",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-12"),
        updated_at: new Date("2024-09-12")
    },
    {
        name: "Hannah Mitchell",
        email: "hannah.mitchell@email.com",
        phone: "+1-555-0129",
        skills: ["Vue.js", "Nuxt.js", "JavaScript", "SCSS", "Vuex"],
        location: "Richmond, VA",
        experience: "3 years Vue.js development",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-13"),
        updated_at: new Date("2024-09-13")
    },
    {
        name: "Tyler Perez",
        email: "tyler.perez@email.com",
        phone: "+1-555-0130",
        skills: ["DevOps", "GitLab CI", "Ansible", "Monitoring", "Linux"],
        location: "Tampa, FL",
        experience: "5 years DevOps engineering",
        experience_level: "Senior",
        created_at: new Date("2024-09-14"),
        updated_at: new Date("2024-09-14")
    },
    {
        name: "Olivia Roberts",
        email: "olivia.roberts@email.com",
        phone: "+1-555-0131",
        skills: ["PowerBI", "Excel", "SQL", "Data Visualization", "Analytics"],
        location: "Charlotte, NC",
        experience: "3 years business intelligence",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-15"),
        updated_at: new Date("2024-09-15")
    },
    {
        name: "Jacob Phillips",
        email: "jacob.phillips@email.com",
        phone: "+1-555-0132",
        skills: ["Elixir", "Phoenix", "PostgreSQL", "Functional Programming"],
        location: "Austin, TX",
        experience: "4 years Elixir development",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-16"),
        updated_at: new Date("2024-09-16")
    },
    {
        name: "Samantha Campbell",
        email: "samantha.campbell@email.com",
        phone: "+1-555-0133",
        skills: ["Technical Writing", "Documentation", "API Documentation", "Markdown"],
        location: "Remote",
        experience: "4 years technical writing",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-17"),
        updated_at: new Date("2024-09-17")
    },
    {
        name: "Ethan Parker",
        email: "ethan.parker@email.com",
        phone: "+1-555-0134",
        skills: ["Node.js", "Express", "Socket.io", "Real-time Applications"],
        location: "Kansas City, MO",
        experience: "2 years Node.js development",
        experience_level: "Junior",
        created_at: new Date("2024-09-18"),
        updated_at: new Date("2024-09-18")
    },
    {
        name: "Natalie Evans",
        email: "natalie.evans@email.com",
        phone: "+1-555-0135",
        skills: ["Cybersecurity", "Incident Response", "Risk Assessment", "Compliance"],
        location: "Arlington, VA",
        experience: "6 years cybersecurity",
        experience_level: "Senior",
        created_at: new Date("2024-09-19"),
        updated_at: new Date("2024-09-19")
    },
    {
        name: "Logan Torres",
        email: "logan.torres@email.com",
        phone: "+1-555-0136",
        skills: ["GraphQL", "Apollo", "React", "Node.js", "MongoDB"],
        location: "Albuquerque, NM",
        experience: "3 years full-stack with GraphQL",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-20"),
        updated_at: new Date("2024-09-20")
    },
    {
        name: "Victoria Flores",
        email: "victoria.flores@email.com",
        phone: "+1-555-0137",
        skills: ["Scrum Master", "Agile", "Project Management", "JIRA", "Team Leadership"],
        location: "Indianapolis, IN",
        experience: "5 years agile project management",
        experience_level: "Senior",
        created_at: new Date("2024-09-21"),
        updated_at: new Date("2024-09-21")
    },
    {
        name: "Connor Rivera",
        email: "connor.rivera@email.com",
        phone: "+1-555-0138",
        skills: ["React Native", "JavaScript", "Mobile Development", "Redux"],
        location: "Columbus, OH",
        experience: "3 years mobile development",
        experience_level: "Mid-level",
        created_at: new Date("2024-09-22"),
        updated_at: new Date("2024-09-22")
    },
    {
        name: "Zoe Cook",
        email: "zoe.cook@email.com",
        phone: "+1-555-0139",
        skills: ["Machine Learning", "PyTorch", "Computer Vision", "OpenCV"],
        location: "San Francisco, CA",
        experience: "2 years ML engineering",
        experience_level: "Junior",
        created_at: new Date("2024-09-23"),
        updated_at: new Date("2024-09-23")
    },
    {
        name: "Ian Rogers",
        email: "ian.rogers@email.com",
        phone: "+1-555-0140",
        skills: ["Cloud Architecture", "AWS", "Azure", "Solution Design", "Enterprise"],
        location: "Remote",
        experience: "8 years cloud architecture",
        experience_level: "Senior",
        created_at: new Date("2024-09-24"),
        updated_at: new Date("2024-09-24")
    }
];

db.candidates.insertMany(candidates);

print('Database initialized successfully with 10 job postings and 40 candidates');
print('Job postings: ' + db.job_postings.countDocuments());
print('Candidates: ' + db.candidates.countDocuments());