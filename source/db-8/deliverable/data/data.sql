-- Job Market Intelligence Database Sample Data
-- Production sample data for job market intelligence and targeted application system
-- Includes federal jobs (USAJobs.gov format), private sector jobs, users, companies, and market analytics

-- User Profiles Sample Data
INSERT INTO user_profiles (user_id, email, full_name, location_city, location_state, location_country, location_latitude, location_longitude, current_job_title, current_company, years_experience, education_level, resume_text, linkedin_url, github_url, portfolio_url, preferred_work_model, salary_expectation_min, salary_expectation_max, preferred_locations, profile_completeness_score, is_active) VALUES
('user_001', 'alice.johnson@email.com', 'Alice Johnson', 'Washington', 'DC', 'US', 38.9072, -77.0369, 'Data Engineer', 'Tech Corp', 5, 'Bachelor''s Degree', 'Experienced data engineer with expertise in Python, SQL, and cloud platforms. Led data pipeline projects serving 1M+ users.', 'https://linkedin.com/in/alicejohnson', 'https://github.com/alicejohnson', 'https://alicejohnson.dev', 'remote', 120000, 160000, '["Washington DC", "Remote", "New York NY"]', 85.50, TRUE),
('user_002', 'bob.smith@email.com', 'Bob Smith', 'San Francisco', 'CA', 'US', 37.7749, -122.4194, 'Software Engineer', 'StartupXYZ', 3, 'Master''s Degree', 'Full-stack developer specializing in React and Node.js. Built scalable web applications.', 'https://linkedin.com/in/bobsmith', 'https://github.com/bobsmith', NULL, 'hybrid', 100000, 140000, '["San Francisco CA", "Remote"]', 78.25, TRUE),
('user_003', 'carol.williams@email.com', 'Carol Williams', 'Austin', 'TX', 'US', 30.2672, -97.7431, 'Data Scientist', 'DataCo', 7, 'PhD', 'Machine learning researcher with publications in top-tier conferences. Expert in NLP and computer vision.', 'https://linkedin.com/in/carolwilliams', 'https://github.com/carolwilliams', 'https://carolwilliams.research', 'remote', 140000, 180000, '["Remote", "Austin TX"]', 92.00, TRUE),
('user_004', 'david.brown@email.com', 'David Brown', 'New York', 'NY', 'US', 40.7128, -74.0060, 'Product Manager', 'ProductInc', 4, 'MBA', 'Product manager with track record of launching successful products. Strong analytical and leadership skills.', 'https://linkedin.com/in/davidbrown', NULL, NULL, 'onsite', 130000, 170000, '["New York NY"]', 70.50, TRUE),
('user_005', 'emma.davis@email.com', 'Emma Davis', 'Seattle', 'WA', 'US', 47.6062, -122.3321, 'DevOps Engineer', 'CloudTech', 6, 'Bachelor''s Degree', 'DevOps engineer specializing in Kubernetes, AWS, and CI/CD pipelines. Reduced deployment time by 80%.', 'https://linkedin.com/in/emmadavis', 'https://github.com/emmadavis', NULL, 'hybrid', 115000, 155000, '["Seattle WA", "Remote"]', 81.75, TRUE),
('user_006', 'frank.miller@email.com', 'Frank Miller', 'Chicago', 'IL', 'US', 41.8781, -87.6298, 'Backend Engineer', 'BackendCo', 2, 'Bachelor''s Degree', 'Backend engineer with experience in Java, Spring Boot, and microservices architecture.', 'https://linkedin.com/in/frankmiller', 'https://github.com/frankmiller', NULL, 'onsite', 90000, 120000, '["Chicago IL"]', 65.00, TRUE),
('user_007', 'grace.wilson@email.com', 'Grace Wilson', 'Boston', 'MA', 'US', 42.3601, -71.0589, 'Frontend Engineer', 'FrontendPro', 4, 'Bachelor''s Degree', 'Frontend engineer specializing in React, TypeScript, and modern UI frameworks. Built responsive web applications.', 'https://linkedin.com/in/gracewilson', 'https://github.com/gracewilson', 'https://gracewilson.dev', 'remote', 100000, 135000, '["Remote", "Boston MA"]', 75.25, TRUE),
('user_008', 'henry.moore@email.com', 'Henry Moore', 'Denver', 'CO', 'US', 39.7392, -104.9903, 'Data Analyst', 'AnalyticsCo', 3, 'Master''s Degree', 'Data analyst with expertise in SQL, Python, and Tableau. Created dashboards driving business decisions.', 'https://linkedin.com/in/henrymoore', NULL, NULL, 'hybrid', 85000, 110000, '["Denver CO", "Remote"]', 68.50, TRUE),
('user_009', 'ivy.taylor@email.com', 'Ivy Taylor', 'Atlanta', 'GA', 'US', 33.7490, -84.3880, 'ML Engineer', 'MLTech', 5, 'Master''s Degree', 'Machine learning engineer with experience deploying ML models to production. Expert in TensorFlow and PyTorch.', 'https://linkedin.com/in/ivytaylor', 'https://github.com/ivytaylor', NULL, 'remote', 125000, 165000, '["Remote", "Atlanta GA"]', 88.00, TRUE),
('user_010', 'jack.anderson@email.com', 'Jack Anderson', 'Portland', 'OR', 'US', 45.5152, -122.6784, 'Security Engineer', 'SecureTech', 8, 'Bachelor''s Degree', 'Cybersecurity engineer with CISSP certification. Expert in network security and threat detection.', 'https://linkedin.com/in/jackanderson', NULL, NULL, 'hybrid', 140000, 180000, '["Portland OR", "Remote"]', 90.25, TRUE);

-- Companies Sample Data (mix of federal agencies and private companies)
INSERT INTO companies (company_id, company_name, company_name_normalized, industry, company_size, headquarters_city, headquarters_state, headquarters_country, website_url, linkedin_url, description, founded_year, employee_count, revenue_range, is_federal_agency, agency_code, data_source, company_rating, total_reviews) VALUES
('comp_001', 'U.S. Department of Defense', 'us department of defense', 'Government', 'enterprise', 'Arlington', 'VA', 'US', 'https://www.defense.gov', 'https://linkedin.com/company/us-department-of-defense', 'The Department of Defense is America''s largest government agency.', 1947, 2800000, 'N/A', TRUE, 'DOD', 'usajobs', 4.2, 15000),
('comp_002', 'National Security Agency', 'national security agency', 'Government', 'large', 'Fort Meade', 'MD', 'US', 'https://www.nsa.gov', NULL, 'The National Security Agency leads the U.S. Government in cryptology.', 1952, 30000, 'N/A', TRUE, 'NSA', 'usajobs', 4.5, 5000),
('comp_003', 'Federal Bureau of Investigation', 'federal bureau of investigation', 'Government', 'large', 'Washington', 'DC', 'US', 'https://www.fbi.gov', 'https://linkedin.com/company/fbi', 'The FBI protects the American people and upholds the Constitution.', 1908, 35000, 'N/A', TRUE, 'FBI', 'usajobs', 4.3, 8000),
('comp_004', 'Tech Corp', 'tech corp', 'Technology', 'large', 'San Francisco', 'CA', 'US', 'https://www.techcorp.com', 'https://linkedin.com/company/techcorp', 'Leading technology company specializing in cloud computing and AI.', 2010, 50000, '$10B+', FALSE, NULL, 'aggregated', 4.1, 25000),
('comp_005', 'DataCo', 'dataco', 'Technology', 'medium', 'Austin', 'TX', 'US', 'https://www.dataco.com', 'https://linkedin.com/company/dataco', 'Data analytics and machine learning solutions provider.', 2015, 500, '$50M-$100M', FALSE, NULL, 'aggregated', 4.0, 500),
('comp_006', 'CloudTech', 'cloudtech', 'Technology', 'large', 'Seattle', 'WA', 'US', 'https://www.cloudtech.com', 'https://linkedin.com/company/cloudtech', 'Cloud infrastructure and DevOps solutions.', 2012, 10000, '$1B-$10B', FALSE, NULL, 'aggregated', 4.4, 12000),
('comp_007', 'U.S. Department of Energy', 'us department of energy', 'Government', 'large', 'Washington', 'DC', 'US', 'https://www.energy.gov', 'https://linkedin.com/company/us-department-of-energy', 'The Department of Energy ensures America''s security and prosperity.', 1977, 13000, 'N/A', TRUE, 'DOE', 'usajobs', 4.0, 3000),
('comp_008', 'National Aeronautics and Space Administration', 'national aeronautics and space administration', 'Government', 'large', 'Washington', 'DC', 'US', 'https://www.nasa.gov', 'https://linkedin.com/company/nasa', 'NASA explores space and advances aeronautics research.', 1958, 18000, 'N/A', TRUE, 'NASA', 'usajobs', 4.7, 20000),
('comp_009', 'StartupXYZ', 'startupxyz', 'Technology', 'startup', 'San Francisco', 'CA', 'US', 'https://www.startupxyz.com', 'https://linkedin.com/company/startupxyz', 'Innovative startup building next-generation software products.', 2020, 50, '$1M-$10M', FALSE, NULL, 'aggregated', 3.8, 100),
('comp_010', 'ProductInc', 'productinc', 'Technology', 'medium', 'New York', 'NY', 'US', 'https://www.productinc.com', 'https://linkedin.com/company/productinc', 'Product development and innovation company.', 2018, 200, '$10M-$50M', FALSE, NULL, 'aggregated', 4.2, 300);

-- Skills Sample Data
INSERT INTO skills (skill_id, skill_name, skill_category, skill_type, parent_skill_id, description, popularity_score) VALUES
('skill_001', 'Python', 'programming', 'technical', NULL, 'High-level programming language for data science and web development', 95.5),
('skill_002', 'SQL', 'programming', 'technical', NULL, 'Structured Query Language for database management', 92.0),
('skill_003', 'JavaScript', 'programming', 'technical', NULL, 'Programming language for web development', 90.0),
('skill_004', 'Java', 'programming', 'technical', NULL, 'Object-oriented programming language for enterprise applications', 88.5),
('skill_005', 'React', 'framework', 'technical', 'skill_003', 'JavaScript library for building user interfaces', 87.0),
('skill_006', 'Node.js', 'framework', 'technical', 'skill_003', 'JavaScript runtime for server-side development', 85.0),
('skill_007', 'AWS', 'tool', 'technical', NULL, 'Amazon Web Services cloud computing platform', 89.0),
('skill_008', 'Kubernetes', 'tool', 'technical', NULL, 'Container orchestration platform', 82.0),
('skill_009', 'Docker', 'tool', 'technical', NULL, 'Containerization platform', 80.0),
('skill_010', 'TensorFlow', 'framework', 'technical', 'skill_001', 'Machine learning framework', 75.0),
('skill_011', 'PyTorch', 'framework', 'technical', 'skill_001', 'Deep learning framework', 73.0),
('skill_012', 'PostgreSQL', 'tool', 'technical', NULL, 'Open-source relational database', 78.0),
('skill_013', 'MongoDB', 'tool', 'technical', NULL, 'NoSQL database', 70.0),
('skill_014', 'Git', 'tool', 'technical', NULL, 'Version control system', 85.0),
('skill_015', 'Linux', 'tool', 'technical', NULL, 'Operating system', 75.0),
('skill_016', 'Communication', 'soft_skill', 'soft', NULL, 'Effective verbal and written communication', 90.0),
('skill_017', 'Leadership', 'soft_skill', 'soft', NULL, 'Ability to lead and inspire teams', 85.0),
('skill_018', 'Problem Solving', 'soft_skill', 'soft', NULL, 'Analytical thinking and problem-solving abilities', 88.0),
('skill_019', 'CISSP', 'certification', 'certification', NULL, 'Certified Information Systems Security Professional', 70.0),
('skill_020', 'AWS Certified Solutions Architect', 'certification', 'certification', NULL, 'AWS cloud architecture certification', 75.0);

-- Job Postings Sample Data (mix of federal and private jobs)
INSERT INTO job_postings (job_id, company_id, job_title, job_title_normalized, job_description, job_type, work_model, location_city, location_state, location_country, location_latitude, location_longitude, salary_min, salary_max, salary_currency, salary_type, posted_date, expiration_date, application_url, application_method, is_active, is_federal_job, usajobs_id, agency_name, pay_plan, grade_level, data_source, source_url, view_count, application_count, match_score_avg) VALUES
('job_001', 'comp_001', 'Data Engineer', 'data engineer', 'Seeking experienced Data Engineer to design and implement data pipelines for defense systems. Must have TS/SCI clearance.', 'full_time', 'onsite', 'Arlington', 'VA', 'US', 38.8816, -77.0910, 120000, 160000, 'USD', 'annual', '2026-01-20 10:00:00', '2026-02-20 23:59:59', 'https://www.usajobs.gov/job/12345678', 'usajobs', TRUE, TRUE, '12345678', 'Department of Defense', 'GS', 'GS-13', 'usajobs', 'https://www.usajobs.gov/job/12345678', 450, 25, 78.5),
('job_002', 'comp_002', 'Cybersecurity Analyst', 'cybersecurity analyst', 'NSA is seeking Cybersecurity Analysts to protect national security systems. Requires TS/SCI clearance.', 'full_time', 'onsite', 'Fort Meade', 'MD', 'US', 39.1084, -76.7435, 110000, 150000, 'USD', 'annual', '2026-01-22 09:00:00', '2026-02-22 23:59:59', 'https://www.usajobs.gov/job/12345679', 'usajobs', TRUE, TRUE, '12345679', 'National Security Agency', 'GG', 'GG-12', 'usajobs', 'https://www.usajobs.gov/job/12345679', 320, 18, 82.0),
('job_003', 'comp_003', 'Data Scientist', 'data scientist', 'FBI is hiring Data Scientists to analyze intelligence data. Must have TS clearance.', 'full_time', 'onsite', 'Washington', 'DC', 'US', 38.9072, -77.0369, 130000, 170000, 'USD', 'annual', '2026-01-21 11:00:00', '2026-02-21 23:59:59', 'https://www.usajobs.gov/job/12345680', 'usajobs', TRUE, TRUE, '12345680', 'Federal Bureau of Investigation', 'GS', 'GS-14', 'usajobs', 'https://www.usajobs.gov/job/12345680', 280, 15, 85.5),
('job_004', 'comp_004', 'Senior Software Engineer', 'senior software engineer', 'Tech Corp is looking for Senior Software Engineers to build scalable cloud applications. Remote work available.', 'full_time', 'remote', 'San Francisco', 'CA', 'US', 37.7749, -122.4194, 150000, 200000, 'USD', 'annual', '2026-01-19 08:00:00', '2026-02-19 23:59:59', 'https://www.techcorp.com/careers/job-001', 'ats', TRUE, FALSE, NULL, NULL, NULL, NULL, 'aggregated', 'https://www.techcorp.com/careers/job-001', 1200, 85, 88.0),
('job_005', 'comp_005', 'Machine Learning Engineer', 'machine learning engineer', 'DataCo seeks ML Engineers to develop and deploy machine learning models. Strong Python and TensorFlow experience required.', 'full_time', 'hybrid', 'Austin', 'TX', 'US', 30.2672, -97.7431, 140000, 180000, 'USD', 'annual', '2026-01-18 14:00:00', '2026-02-18 23:59:59', 'https://www.dataco.com/careers/ml-engineer', 'ats', TRUE, FALSE, NULL, NULL, NULL, NULL, 'aggregated', 'https://www.dataco.com/careers/ml-engineer', 890, 42, 90.5),
('job_006', 'comp_006', 'DevOps Engineer', 'devops engineer', 'CloudTech is hiring DevOps Engineers to manage Kubernetes clusters and CI/CD pipelines. AWS certification preferred.', 'full_time', 'hybrid', 'Seattle', 'WA', 'US', 47.6062, -122.3321, 130000, 170000, 'USD', 'annual', '2026-01-17 10:00:00', '2026-02-17 23:59:59', 'https://www.cloudtech.com/careers/devops', 'ats', TRUE, FALSE, NULL, NULL, NULL, NULL, 'aggregated', 'https://www.cloudtech.com/careers/devops', 650, 38, 87.5),
('job_007', 'comp_007', 'Energy Data Analyst', 'energy data analyst', 'DOE is seeking Data Analysts to analyze energy consumption data and support policy decisions.', 'full_time', 'onsite', 'Washington', 'DC', 'US', 38.9072, -77.0369, 90000, 120000, 'USD', 'annual', '2026-01-23 09:00:00', '2026-02-23 23:59:59', 'https://www.usajobs.gov/job/12345681', 'usajobs', TRUE, TRUE, '12345681', 'Department of Energy', 'GS', 'GS-11', 'usajobs', 'https://www.usajobs.gov/job/12345681', 180, 12, 75.0),
('job_008', 'comp_008', 'Aerospace Data Engineer', 'aerospace data engineer', 'NASA is hiring Data Engineers to process satellite and mission data. Must have strong Python and SQL skills.', 'full_time', 'onsite', 'Houston', 'TX', 'US', 29.7604, -95.3698, 125000, 165000, 'USD', 'annual', '2026-01-24 08:00:00', '2026-02-24 23:59:59', 'https://www.usajobs.gov/job/12345682', 'usajobs', TRUE, TRUE, '12345682', 'National Aeronautics and Space Administration', 'GS', 'GS-13', 'usajobs', 'https://www.usajobs.gov/job/12345682', 520, 30, 88.5),
('job_009', 'comp_009', 'Full-Stack Developer', 'full stack developer', 'StartupXYZ is looking for Full-Stack Developers to build web applications using React and Node.js.', 'full_time', 'remote', 'San Francisco', 'CA', 'US', 37.7749, -122.4194, 100000, 140000, 'USD', 'annual', '2026-01-16 12:00:00', '2026-02-16 23:59:59', 'https://www.startupxyz.com/careers/fullstack', 'email', TRUE, FALSE, NULL, NULL, NULL, NULL, 'aggregated', 'https://www.startupxyz.com/careers/fullstack', 420, 28, 80.0),
('job_010', 'comp_010', 'Product Manager', 'product manager', 'ProductInc seeks Product Managers to lead product development initiatives. MBA preferred.', 'full_time', 'onsite', 'New York', 'NY', 'US', 40.7128, -74.0060, 140000, 180000, 'USD', 'annual', '2026-01-15 11:00:00', '2026-02-15 23:59:59', 'https://www.productinc.com/careers/pm', 'ats', TRUE, FALSE, NULL, NULL, NULL, NULL, 'aggregated', 'https://www.productinc.com/careers/pm', 380, 22, 82.5);

-- Job Skills Requirements Sample Data
INSERT INTO job_skills_requirements (requirement_id, job_id, skill_id, requirement_type, importance_score, years_experience_required, extracted_from_description) VALUES
('req_001', 'job_001', 'skill_001', 'required', 9.5, 5.0, TRUE),
('req_002', 'job_001', 'skill_002', 'required', 9.0, 5.0, TRUE),
('req_003', 'job_001', 'skill_007', 'preferred', 8.0, 3.0, TRUE),
('req_004', 'job_002', 'skill_019', 'required', 10.0, 5.0, TRUE),
('req_005', 'job_002', 'skill_015', 'required', 8.5, 4.0, TRUE),
('req_006', 'job_003', 'skill_001', 'required', 9.5, 5.0, TRUE),
('req_007', 'job_003', 'skill_010', 'preferred', 8.5, 3.0, TRUE),
('req_008', 'job_004', 'skill_003', 'required', 9.0, 5.0, TRUE),
('req_009', 'job_004', 'skill_005', 'required', 9.5, 4.0, TRUE),
('req_010', 'job_004', 'skill_006', 'preferred', 8.0, 3.0, TRUE),
('req_011', 'job_005', 'skill_001', 'required', 10.0, 5.0, TRUE),
('req_012', 'job_005', 'skill_010', 'required', 9.5, 4.0, TRUE),
('req_013', 'job_006', 'skill_008', 'required', 9.0, 4.0, TRUE),
('req_014', 'job_006', 'skill_007', 'required', 9.5, 5.0, TRUE),
('req_015', 'job_006', 'skill_020', 'preferred', 8.0, NULL, TRUE),
('req_016', 'job_007', 'skill_002', 'required', 8.5, 3.0, TRUE),
('req_017', 'job_007', 'skill_001', 'preferred', 7.5, 2.0, TRUE),
('req_018', 'job_008', 'skill_001', 'required', 9.5, 5.0, TRUE),
('req_019', 'job_008', 'skill_002', 'required', 9.0, 5.0, TRUE),
('req_020', 'job_009', 'skill_003', 'required', 9.0, 3.0, TRUE),
('req_021', 'job_009', 'skill_005', 'required', 9.0, 3.0, TRUE),
('req_022', 'job_009', 'skill_006', 'preferred', 8.0, 2.0, TRUE),
('req_023', 'job_010', 'skill_016', 'required', 9.5, 5.0, TRUE),
('req_024', 'job_010', 'skill_017', 'preferred', 8.5, 4.0, TRUE);

-- User Skills Sample Data
INSERT INTO user_skills (user_skill_id, user_id, skill_id, proficiency_level, proficiency_score, years_experience, last_used_date, verified) VALUES
('us_001', 'user_001', 'skill_001', 'advanced', 8.5, 5.0, '2026-01-15', TRUE),
('us_002', 'user_001', 'skill_002', 'expert', 9.5, 5.0, '2026-01-20', TRUE),
('us_003', 'user_001', 'skill_007', 'advanced', 8.0, 4.0, '2026-01-18', TRUE),
('us_004', 'user_002', 'skill_003', 'advanced', 8.5, 3.0, '2026-01-19', TRUE),
('us_005', 'user_002', 'skill_005', 'advanced', 8.0, 3.0, '2026-01-17', TRUE),
('us_006', 'user_002', 'skill_006', 'intermediate', 7.0, 2.0, '2026-01-16', FALSE),
('us_007', 'user_003', 'skill_001', 'expert', 9.5, 7.0, '2026-01-21', TRUE),
('us_008', 'user_003', 'skill_010', 'expert', 9.0, 6.0, '2026-01-20', TRUE),
('us_009', 'user_003', 'skill_011', 'advanced', 8.5, 5.0, '2026-01-19', TRUE),
('us_010', 'user_004', 'skill_016', 'expert', 9.5, 4.0, '2026-01-18', TRUE),
('us_011', 'user_004', 'skill_017', 'advanced', 8.5, 4.0, '2026-01-17', TRUE),
('us_012', 'user_005', 'skill_008', 'advanced', 8.5, 5.0, '2026-01-20', TRUE),
('us_013', 'user_005', 'skill_007', 'expert', 9.5, 6.0, '2026-01-19', TRUE),
('us_014', 'user_005', 'skill_009', 'advanced', 8.0, 4.0, '2026-01-18', TRUE),
('us_015', 'user_006', 'skill_004', 'intermediate', 7.5, 2.0, '2026-01-16', FALSE),
('us_016', 'user_007', 'skill_003', 'advanced', 8.0, 4.0, '2026-01-17', TRUE),
('us_017', 'user_007', 'skill_005', 'advanced', 8.5, 4.0, '2026-01-18', TRUE),
('us_018', 'user_008', 'skill_002', 'advanced', 8.0, 3.0, '2026-01-19', TRUE),
('us_019', 'user_008', 'skill_001', 'intermediate', 7.0, 2.0, '2026-01-18', FALSE),
('us_020', 'user_009', 'skill_001', 'advanced', 8.5, 5.0, '2026-01-20', TRUE),
('us_021', 'user_009', 'skill_010', 'advanced', 8.0, 4.0, '2026-01-19', TRUE),
('us_022', 'user_010', 'skill_019', 'expert', 9.5, 8.0, '2026-01-21', TRUE),
('us_023', 'user_010', 'skill_015', 'expert', 9.0, 8.0, '2026-01-20', TRUE);

-- Job Applications Sample Data
INSERT INTO job_applications (application_id, user_id, job_id, application_status, application_date, submitted_at, status_updated_at, cover_letter_text, resume_version, match_score, application_method, application_reference_id, notes) VALUES
('app_001', 'user_001', 'job_001', 'under_review', '2026-01-25 10:00:00', '2026-01-25 10:15:00', '2026-01-26 14:30:00', 'I am excited to apply for the Data Engineer position at DOD. My 5 years of experience align perfectly with your requirements.', 'resume_v2.pdf', 85.5, 'usajobs', 'USAJOBS-12345678', 'Strong match for federal position'),
('app_002', 'user_003', 'job_003', 'interview', '2026-01-26 09:00:00', '2026-01-26 09:20:00', '2026-01-28 16:00:00', 'As a Data Scientist with 7 years of experience, I am eager to contribute to FBI''s mission.', 'resume_v3.pdf', 90.0, 'usajobs', 'USAJOBS-12345680', 'Interview scheduled for next week'),
('app_003', 'user_002', 'job_009', 'submitted', '2026-01-24 14:00:00', '2026-01-24 14:30:00', '2026-01-24 14:30:00', 'I am interested in the Full-Stack Developer role at StartupXYZ.', 'resume_v1.pdf', 78.5, 'email', NULL, NULL),
('app_004', 'user_005', 'job_006', 'under_review', '2026-01-23 11:00:00', '2026-01-23 11:45:00', '2026-01-25 10:00:00', 'My DevOps experience makes me a strong candidate for this position.', 'resume_v2.pdf', 88.0, 'ats', 'CLOUDTECH-001', NULL),
('app_005', 'user_004', 'job_010', 'rejected', '2026-01-22 08:00:00', '2026-01-22 08:15:00', '2026-01-27 12:00:00', 'I am applying for the Product Manager position.', 'resume_v1.pdf', 75.0, 'ats', 'PRODUCTINC-001', 'Not selected - insufficient product management experience');

-- Job Recommendations Sample Data
INSERT INTO job_recommendations (recommendation_id, user_id, job_id, match_score, skill_match_score, location_match_score, salary_match_score, experience_match_score, work_model_match_score, recommendation_reason, recommendation_rank, is_liked, is_applied, is_dismissed, recommendation_date, expires_at) VALUES
('rec_001', 'user_001', 'job_001', 85.5, 90.0, 80.0, 85.0, 90.0, 60.0, 'Strong skill match (Python, SQL, AWS). Location preference met. Salary within range.', 1, FALSE, TRUE, FALSE, '2026-01-25 08:00:00', '2026-02-25 23:59:59'),
('rec_002', 'user_001', 'job_008', 82.0, 88.0, 70.0, 80.0, 85.0, 60.0, 'Excellent skill alignment. Federal position with competitive salary.', 2, FALSE, FALSE, FALSE, '2026-01-25 08:00:00', '2026-02-25 23:59:59'),
('rec_003', 'user_002', 'job_009', 78.5, 85.0, 90.0, 75.0, 70.0, 100.0, 'Perfect work model match (remote). Skills align with React and Node.js requirements.', 1, TRUE, TRUE, FALSE, '2026-01-24 09:00:00', '2026-02-24 23:59:59'),
('rec_004', 'user_003', 'job_003', 90.0, 95.0, 80.0, 90.0, 95.0, 60.0, 'Exceptional match. PhD in ML with TensorFlow experience aligns perfectly.', 1, TRUE, TRUE, FALSE, '2026-01-26 10:00:00', '2026-02-26 23:59:59'),
('rec_005', 'user_003', 'job_005', 88.5, 92.0, 90.0, 85.0, 90.0, 80.0, 'Strong ML engineering match. Hybrid work model preferred.', 2, FALSE, FALSE, FALSE, '2026-01-26 10:00:00', '2026-02-26 23:59:59'),
('rec_006', 'user_005', 'job_006', 88.0, 90.0, 85.0, 85.0, 90.0, 90.0, 'Perfect DevOps match. Kubernetes and AWS expertise required.', 1, TRUE, TRUE, FALSE, '2026-01-23 11:00:00', '2026-02-23 23:59:59'),
('rec_007', 'user_007', 'job_004', 75.0, 80.0, 70.0, 70.0, 75.0, 100.0, 'Good frontend match. Remote work available.', 1, FALSE, FALSE, FALSE, '2026-01-22 12:00:00', '2026-02-22 23:59:59'),
('rec_008', 'user_009', 'job_005', 90.5, 95.0, 90.0, 90.0, 90.0, 80.0, 'Excellent ML engineering match. Strong Python and TensorFlow alignment.', 1, FALSE, FALSE, FALSE, '2026-01-21 13:00:00', '2026-02-21 23:59:59');

-- Market Trends Sample Data
INSERT INTO market_trends (trend_id, trend_date, geographic_scope, location_state, location_city, location_metro, industry, job_category, total_job_postings, new_job_postings, active_job_seekers, average_salary_min, average_salary_max, median_salary, top_skills, skill_demand_trend, competition_index, growth_rate, data_source) VALUES
('trend_001', '2026-01-20', 'national', NULL, NULL, NULL, 'Technology', 'Data Engineering', 5000, 500, 15000, 120000, 160000, 140000, '["Python", "SQL", "AWS", "Kubernetes"]', '{"Python": 15, "SQL": 12, "AWS": 18, "Kubernetes": 20}', 3.0, 5.2, 'bls'),
('trend_002', '2026-01-20', 'state', 'CA', NULL, NULL, 'Technology', 'Software Engineering', 8000, 800, 25000, 130000, 180000, 155000, '["JavaScript", "React", "Node.js", "Python"]', '{"JavaScript": 10, "React": 15, "Node.js": 12, "Python": 8}', 3.1, 6.5, 'aggregated'),
('trend_003', '2026-01-20', 'city', 'DC', 'Washington', 'Washington-Arlington-Alexandria', 'Government', 'Data Science', 300, 30, 1200, 110000, 150000, 130000, '["Python", "SQL", "TensorFlow", "Security Clearance"]', '{"Python": 20, "SQL": 18, "TensorFlow": 15, "Security Clearance": 25}', 4.0, 8.0, 'usajobs'),
('trend_004', '2026-01-21', 'national', NULL, NULL, NULL, 'Technology', 'DevOps', 3500, 350, 10000, 125000, 170000, 147500, '["Kubernetes", "AWS", "Docker", "Linux"]', '{"Kubernetes": 22, "AWS": 20, "Docker": 18, "Linux": 15}', 2.9, 7.8, 'aggregated'),
('trend_005', '2026-01-21', 'state', 'TX', NULL, NULL, 'Technology', 'Machine Learning', 2000, 200, 6000, 135000, 180000, 157500, '["Python", "TensorFlow", "PyTorch", "MLOps"]', '{"Python": 18, "TensorFlow": 20, "PyTorch": 15, "MLOps": 25}', 3.0, 9.5, 'aggregated');

-- Job Market Analytics Sample Data
INSERT INTO job_market_analytics (analytics_id, analysis_date, analysis_type, geographic_scope, location_state, location_city, industry, total_companies, total_active_jobs, remote_job_percentage, hybrid_job_percentage, average_time_to_fill_days, average_applications_per_job, top_employers, emerging_skills, declining_skills, salary_trends, job_type_distribution, work_model_distribution) VALUES
('analytics_001', '2026-01-20', 'daily', 'national', NULL, NULL, 'Technology', 500, 15000, 35.5, 25.0, 28, 45.5, '["Tech Corp", "CloudTech", "DataCo"]', '["Kubernetes", "MLOps", "React"]', '["jQuery", "PHP"]', '{"trend": "increasing", "annual_growth": 5.2}', '{"full_time": 85, "contract": 10, "part_time": 5}', '{"remote": 35.5, "hybrid": 25.0, "onsite": 39.5}'),
('analytics_002', '2026-01-20', 'daily', 'state', 'CA', NULL, 'Technology', 200, 8000, 40.0, 30.0, 25, 50.0, '["Tech Corp", "StartupXYZ"]', '["React", "TypeScript", "Next.js"]', '["AngularJS", "Backbone.js"]', '{"trend": "increasing", "annual_growth": 6.5}', '{"full_time": 80, "contract": 15, "part_time": 5}', '{"remote": 40.0, "hybrid": 30.0, "onsite": 30.0}'),
('analytics_003', '2026-01-21', 'daily', 'city', 'DC', 'Washington', 'Government', 50, 500, 5.0, 10.0, 45, 30.0, '["Department of Defense", "FBI", "NSA"]', '["Security Clearance", "Python", "Data Engineering"]', '["Legacy Systems"]', '{"trend": "stable", "annual_growth": 2.0}', '{"full_time": 95, "contract": 5, "part_time": 0}', '{"remote": 5.0, "hybrid": 10.0, "onsite": 85.0}');

-- Data Source Metadata Sample Data
INSERT INTO data_source_metadata (metadata_id, source_name, source_type, extraction_date, extraction_method, records_extracted, records_new, records_updated, records_failed, extraction_status, error_message, api_endpoint, api_response_code, extraction_duration_seconds) VALUES
('meta_001', 'usajobs', 'api', '2026-01-20 08:00:00', 'REST API', 150, 120, 30, 0, 'success', NULL, 'https://data.usajobs.gov/api/Search?DatePosted=14', 200, 45),
('meta_002', 'bls', 'api', '2026-01-20 09:00:00', 'REST API POST', 5000, 5000, 0, 0, 'success', NULL, 'https://api.bls.gov/publicAPI/v2/timeseries/data', 200, 120),
('meta_003', 'aggregated', 'scraper', '2026-01-20 10:00:00', 'Web Scraping', 2000, 1800, 200, 0, 'success', NULL, NULL, NULL, 300),
('meta_004', 'usajobs', 'api', '2026-01-21 08:00:00', 'REST API', 180, 150, 30, 0, 'success', NULL, 'https://data.usajobs.gov/api/Search?DatePosted=14', 200, 50),
('meta_005', 'aggregated', 'scraper', '2026-01-21 10:00:00', 'Web Scraping', 2200, 2000, 200, 0, 'success', NULL, NULL, NULL, 320);

-- User Job Search History Sample Data
INSERT INTO user_job_search_history (search_id, user_id, search_query, search_filters, location_filter, salary_filter_min, salary_filter_max, work_model_filter, job_type_filter, industry_filter, results_count, search_date) VALUES
('search_001', 'user_001', 'data engineer', '{"skills": ["Python", "SQL"], "experience": "5+"}', 'Washington DC', 120000, 160000, 'remote', 'full_time', 'Technology', 25, '2026-01-25 08:00:00'),
('search_002', 'user_002', 'full stack developer', '{"skills": ["React", "Node.js"]}', 'San Francisco CA', 100000, 140000, 'remote', 'full_time', 'Technology', 18, '2026-01-24 09:00:00'),
('search_003', 'user_003', 'machine learning engineer', '{"skills": ["Python", "TensorFlow"], "education": "PhD"}', 'Remote', 140000, 180000, 'remote', 'full_time', 'Technology', 12, '2026-01-26 10:00:00'),
('search_004', 'user_005', 'devops engineer', '{"skills": ["Kubernetes", "AWS"]}', 'Seattle WA', 130000, 170000, 'hybrid', 'full_time', 'Technology', 15, '2026-01-23 11:00:00'),
('search_005', 'user_007', 'frontend engineer', '{"skills": ["React", "TypeScript"]}', 'Remote', 100000, 135000, 'remote', 'full_time', 'Technology', 20, '2026-01-22 12:00:00');

-- Backfill industry from companies for job_postings
UPDATE job_postings jp SET industry = c.industry FROM companies c WHERE jp.company_id = c.company_id;
