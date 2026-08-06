#!/usr/bin/env python3
"""
Generate synthetic data for 30GB scale testing
Generates realistic user profiles, applications, recommendations, and job postings
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import csv

# Configuration
USERS_COUNT = 2000000
JOBS_COUNT = 5000000
APPLICATIONS_COUNT = 15000000
RECOMMENDATIONS_COUNT = 50000000
COMPANIES_COUNT = 500000
SKILLS_COUNT = 50000

# Data pools for realistic generation
STATES = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC']
CITIES = {
    'CA': ['San Francisco', 'Los Angeles', 'San Diego', 'San Jose', 'Sacramento'],
    'NY': ['New York', 'Buffalo', 'Rochester', 'Albany', 'Syracuse'],
    'TX': ['Austin', 'Dallas', 'Houston', 'San Antonio', 'Fort Worth'],
    'FL': ['Miami', 'Tampa', 'Orlando', 'Jacksonville', 'Tallahassee'],
    'WA': ['Seattle', 'Spokane', 'Tacoma', 'Vancouver', 'Bellevue'],
    'IL': ['Chicago', 'Aurora', 'Naperville', 'Rockford', 'Peoria'],
    'MA': ['Boston', 'Worcester', 'Springfield', 'Cambridge', 'Lowell'],
    'CO': ['Denver', 'Colorado Springs', 'Aurora', 'Fort Collins', 'Boulder'],
    'GA': ['Atlanta', 'Augusta', 'Columbus', 'Savannah', 'Athens'],
    'OR': ['Portland', 'Eugene', 'Salem', 'Gresham', 'Hillsboro']
}

JOB_TITLES = [
    'Software Engineer', 'Data Engineer', 'Data Scientist', 'ML Engineer', 'DevOps Engineer',
    'Backend Engineer', 'Frontend Engineer', 'Full-Stack Developer', 'Product Manager',
    'Data Analyst', 'Security Engineer', 'Cloud Architect', 'Database Administrator',
    'QA Engineer', 'Site Reliability Engineer', 'Solutions Architect', 'Technical Lead',
    'Engineering Manager', 'Research Scientist', 'Business Analyst'
]

SKILLS = [
    'Python', 'SQL', 'JavaScript', 'Java', 'React', 'Node.js', 'AWS', 'Kubernetes',
    'Docker', 'TensorFlow', 'PyTorch', 'PostgreSQL', 'MongoDB', 'Git', 'Linux',
    'TypeScript', 'Angular', 'Vue.js', 'Spring Boot', 'Django', 'Flask', 'FastAPI',
    'Spark', 'Kafka', 'Elasticsearch', 'Redis', 'GraphQL', 'REST API', 'Microservices',
    'CI/CD', 'Terraform', 'Ansible', 'Jenkins', 'GitLab', 'GitHub Actions'
]

INDUSTRIES = [
    'Technology', 'Finance', 'Healthcare', 'Retail', 'Manufacturing',
    'Education', 'Government', 'Consulting', 'Media', 'Telecommunications'
]

WORK_MODELS = ['remote', 'hybrid', 'onsite']
JOB_TYPES = ['full_time', 'part_time', 'contract', 'temporary', 'internship']
APPLICATION_STATUSES = ['draft', 'submitted', 'under_review', 'interview', 'offer', 'rejected', 'withdrawn']
EDUCATION_LEVELS = ['High School', "Bachelor's Degree", "Master's Degree", 'PhD', 'MBA']
PROFICIENCY_LEVELS = ['beginner', 'intermediate', 'advanced', 'expert']


def generate_user_profiles(count: int, output_file: Path):
    """Generate synthetic user profiles"""
    print(f"Generating {count:,} user profiles...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'user_id', 'email', 'full_name', 'location_city', 'location_state',
            'location_country', 'location_latitude', 'location_longitude',
            'current_job_title', 'current_company', 'years_experience',
            'education_level', 'resume_text', 'linkedin_url', 'github_url',
            'portfolio_url', 'preferred_work_model', 'salary_expectation_min',
            'salary_expectation_max', 'preferred_locations', 'profile_completeness_score',
            'is_active', 'created_at', 'updated_at', 'last_active_at'
        ])
        
        for i in range(count):
            user_id = f'user_{str(uuid.uuid4())[:8]}'
            state = random.choice(STATES)
            city = random.choice(CITIES.get(state, ['City']))
            
            years_exp = random.randint(0, 20)
            job_title = random.choice(JOB_TITLES)
            
            # Generate email
            first_name = f"User{i}"
            last_name = f"Test{random.randint(1000, 9999)}"
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            
            # Salary expectations based on experience
            base_salary = 60000 + (years_exp * 8000)
            salary_min = base_salary - random.randint(10000, 20000)
            salary_max = base_salary + random.randint(10000, 30000)
            
            # Profile completeness (20-100%)
            completeness = random.uniform(20, 100)
            
            # Timestamps
            created_at = datetime.now() - timedelta(days=random.randint(0, 730))
            updated_at = created_at + timedelta(days=random.randint(0, 30))
            last_active_at = datetime.now() - timedelta(days=random.randint(0, 7))
            
            writer.writerow([
                user_id, email, f"{first_name} {last_name}", city, state, 'US',
                round(random.uniform(25.0, 49.0), 7), round(random.uniform(-125.0, -66.0), 7),
                job_title, f"Company{random.randint(1, 1000)}", years_exp,
                random.choice(EDUCATION_LEVELS), f"Resume text for {first_name} {last_name}",
                f"https://linkedin.com/in/{first_name.lower()}{last_name.lower()}",
                f"https://github.com/{first_name.lower()}{last_name.lower()}",
                f"https://{first_name.lower()}.dev" if random.random() > 0.7 else None,
                random.choice(WORK_MODELS), salary_min, salary_max,
                json.dumps([city, state, 'Remote']), round(completeness, 2),
                True, created_at, updated_at, last_active_at
            ])
            
            if (i + 1) % 100000 == 0:
                print(f"  Generated {i + 1:,} users...")
    
    print(f"✓ Generated {count:,} user profiles")


def generate_companies(count: int, output_file: Path):
    """Generate synthetic companies"""
    print(f"Generating {count:,} companies...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'company_id', 'company_name', 'company_name_normalized', 'industry',
            'company_size', 'headquarters_city', 'headquarters_state',
            'headquarters_country', 'website_url', 'linkedin_url', 'description',
            'founded_year', 'employee_count', 'revenue_range', 'is_federal_agency',
            'agency_code', 'data_source', 'company_rating', 'total_reviews',
            'created_at', 'updated_at'
        ])
        
        for i in range(count):
            company_id = f'comp_{str(uuid.uuid4())[:8]}'
            company_name = f"Company {i+1}"
            state = random.choice(STATES)
            city = random.choice(CITIES.get(state, ['City']))
            industry = random.choice(INDUSTRIES)
            is_federal = random.random() < 0.1  # 10% federal
            
            # Company size distribution
            size_weights = [0.1, 0.2, 0.3, 0.3, 0.1]  # startup, small, medium, large, enterprise
            company_size = random.choices(
                ['startup', 'small', 'medium', 'large', 'enterprise'],
                weights=size_weights
            )[0]
            
            # Employee count based on size
            employee_counts = {
                'startup': (10, 100),
                'small': (100, 500),
                'medium': (500, 5000),
                'large': (5000, 50000),
                'enterprise': (50000, 500000)
            }
            employee_count = random.randint(*employee_counts[company_size])
            
            founded_year = random.randint(1950, 2023)
            rating = round(random.uniform(3.0, 5.0), 2) if random.random() > 0.2 else None
            reviews = random.randint(0, 50000) if rating else 0
            
            created_at = datetime.now() - timedelta(days=random.randint(0, 365))
            
            writer.writerow([
                company_id, company_name, company_name.lower().replace(' ', '_'),
                industry, company_size, city, state, 'US',
                f"https://www.{company_name.lower().replace(' ', '')}.com",
                f"https://linkedin.com/company/{company_name.lower().replace(' ', '-')}",
                f"Description for {company_name}", founded_year, employee_count,
                f"${random.randint(1, 100)}M-${random.randint(100, 1000)}M",
                is_federal, f"AGENCY{random.randint(1, 100)}" if is_federal else None,
                'usajobs' if is_federal else 'aggregated', rating, reviews,
                created_at, created_at
            ])
            
            if (i + 1) % 50000 == 0:
                print(f"  Generated {i + 1:,} companies...")
    
    print(f"✓ Generated {count:,} companies")


def generate_job_postings(count: int, companies: List[str], output_file: Path):
    """Generate synthetic job postings"""
    print(f"Generating {count:,} job postings...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'job_id', 'company_id', 'job_title', 'job_title_normalized', 'job_description',
            'job_type', 'work_model', 'location_city', 'location_state', 'location_country',
            'location_latitude', 'location_longitude', 'salary_min', 'salary_max',
            'salary_currency', 'salary_type', 'posted_date', 'expiration_date',
            'application_url', 'application_method', 'is_active', 'is_federal_job',
            'usajobs_id', 'agency_name', 'pay_plan', 'grade_level', 'data_source',
            'source_url', 'view_count', 'application_count', 'match_score_avg',
            'created_at', 'updated_at'
        ])
        
        for i in range(count):
            job_id = f'job_{str(uuid.uuid4())[:8]}'
            company_id = random.choice(companies)
            job_title = random.choice(JOB_TITLES)
            state = random.choice(STATES)
            city = random.choice(CITIES.get(state, ['City']))
            
            # Salary based on job title and location
            base_salary = random.randint(80000, 200000)
            salary_min = base_salary - random.randint(10000, 30000)
            salary_max = base_salary + random.randint(10000, 50000)
            
            # Posted date (last 2 years)
            posted_date = datetime.now() - timedelta(days=random.randint(0, 730))
            expiration_date = posted_date + timedelta(days=random.randint(30, 90))
            is_active = expiration_date > datetime.now() and random.random() > 0.1
            
            is_federal = random.random() < 0.15  # 15% federal jobs
            
            view_count = random.randint(0, 10000) if is_active else 0
            application_count = random.randint(0, min(500, view_count // 10))
            
            writer.writerow([
                job_id, company_id, job_title, job_title.lower().replace(' ', '_'),
                f"Job description for {job_title} at company", random.choice(JOB_TYPES),
                random.choice(WORK_MODELS), city, state, 'US',
                round(random.uniform(25.0, 49.0), 7), round(random.uniform(-125.0, -66.0), 7),
                salary_min, salary_max, 'USD', 'annual', posted_date, expiration_date,
                f"https://company.com/careers/{job_id}", random.choice(['ats', 'url', 'email']),
                is_active, is_federal,
                f"USAJOBS-{random.randint(10000000, 99999999)}" if is_federal else None,
                f"Agency {random.randint(1, 50)}" if is_federal else None,
                random.choice(['GS', 'GG']) if is_federal else None,
                f"GS-{random.randint(7, 15)}" if is_federal else None,
                'usajobs' if is_federal else 'aggregated',
                f"https://source.com/job/{job_id}", view_count, application_count,
                round(random.uniform(60, 95), 2) if is_active else None,
                posted_date, posted_date
            ])
            
            if (i + 1) % 100000 == 0:
                print(f"  Generated {i + 1:,} job postings...")
    
    print(f"✓ Generated {count:,} job postings")


def generate_applications(count: int, users: List[str], jobs: List[str], output_file: Path):
    """Generate synthetic job applications"""
    print(f"Generating {count:,} job applications...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'application_id', 'user_id', 'job_id', 'application_status',
            'application_date', 'submitted_at', 'status_updated_at',
            'cover_letter_text', 'resume_version', 'match_score',
            'application_method', 'application_reference_id', 'notes',
            'created_at', 'updated_at'
        ])
        
        for i in range(count):
            application_id = f'app_{str(uuid.uuid4())[:8]}'
            user_id = random.choice(users)
            job_id = random.choice(jobs)
            
            # Application status distribution
            status_weights = [0.05, 0.40, 0.30, 0.15, 0.05, 0.04, 0.01]
            status = random.choices(
                APPLICATION_STATUSES,
                weights=status_weights
            )[0]
            
            # Timestamps based on status
            application_date = datetime.now() - timedelta(days=random.randint(0, 180))
            submitted_at = application_date + timedelta(hours=random.randint(1, 48)) if status != 'draft' else None
            status_updated_at = submitted_at + timedelta(days=random.randint(0, 30)) if submitted_at else application_date
            
            match_score = round(random.uniform(60, 95), 2) if submitted_at else None
            
            writer.writerow([
                application_id, user_id, job_id, status,
                application_date, submitted_at, status_updated_at,
                f"Cover letter for application {application_id}",
                f"resume_v{random.randint(1, 5)}.pdf", match_score,
                random.choice(['direct', 'ats', 'email', 'usajobs']),
                f"REF-{random.randint(100000, 999999)}" if submitted_at else None,
                None, application_date, status_updated_at
            ])
            
            if (i + 1) % 500000 == 0:
                print(f"  Generated {i + 1:,} applications...")
    
    print(f"✓ Generated {count:,} job applications")


def generate_recommendations(count: int, users: List[str], jobs: List[str], output_file: Path):
    """Generate synthetic job recommendations"""
    print(f"Generating {count:,} job recommendations...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'recommendation_id', 'user_id', 'job_id', 'match_score',
            'skill_match_score', 'location_match_score', 'salary_match_score',
            'experience_match_score', 'work_model_match_score', 'recommendation_reason',
            'recommendation_rank', 'is_liked', 'is_applied', 'is_dismissed',
            'recommendation_date', 'expires_at', 'created_at'
        ])
        
        # Generate recommendations per user (average 25 per user)
        users_per_batch = len(users) // (count // 25) if count // 25 > 0 else len(users)
        
        for user_idx, user_id in enumerate(users):
            if user_idx >= count // 25:
                break
            
            # Generate 20-30 recommendations per user
            num_recommendations = random.randint(20, 30)
            user_jobs = random.sample(jobs, min(num_recommendations, len(jobs)))
            
            for rank, job_id in enumerate(user_jobs, 1):
                recommendation_id = f'rec_{str(uuid.uuid4())[:8]}'
                
                # Generate match scores
                skill_match = round(random.uniform(70, 95), 2)
                location_match = round(random.uniform(60, 100), 2)
                salary_match = round(random.uniform(65, 95), 2)
                experience_match = round(random.uniform(70, 95), 2)
                work_model_match = round(random.uniform(70, 100), 2)
                
                # Overall match score (weighted average)
                overall_match = round(
                    skill_match * 0.35 +
                    location_match * 0.20 +
                    salary_match * 0.15 +
                    experience_match * 0.15 +
                    work_model_match * 0.15,
                    2
                )
                
                recommendation_date = datetime.now() - timedelta(days=random.randint(0, 30))
                expires_at = recommendation_date + timedelta(days=30)
                
                is_applied = random.random() < 0.1  # 10% applied
                is_liked = random.random() < 0.15  # 15% liked
                is_dismissed = random.random() < 0.05  # 5% dismissed
                
                writer.writerow([
                    recommendation_id, user_id, job_id, overall_match,
                    skill_match, location_match, salary_match,
                    experience_match, work_model_match,
                    f"Strong match: {overall_match}% alignment",
                    rank, is_liked, is_applied, is_dismissed,
                    recommendation_date, expires_at, recommendation_date
                ])
            
            if (user_idx + 1) % 10000 == 0:
                print(f"  Generated recommendations for {user_idx + 1:,} users...")
    
    print(f"✓ Generated {count:,} job recommendations")


def main():
    """Main data generation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate synthetic data for db-8')
    parser.add_argument('--output-dir', type=str, default='data/generated',
                       help='Output directory for generated files')
    parser.add_argument('--users', type=int, default=USERS_COUNT, help='Number of users')
    parser.add_argument('--companies', type=int, default=COMPANIES_COUNT, help='Number of companies')
    parser.add_argument('--jobs', type=int, default=JOBS_COUNT, help='Number of jobs')
    parser.add_argument('--applications', type=int, default=APPLICATIONS_COUNT, help='Number of applications')
    parser.add_argument('--recommendations', type=int, default=RECOMMENDATIONS_COUNT, help='Number of recommendations')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("Synthetic Data Generation for db-8 (30GB Scale)")
    print("="*70)
    
    # Generate companies first (needed for jobs)
    companies_file = output_dir / 'companies.csv'
    generate_companies(args.companies, companies_file)
    
    # Load company IDs
    companies = []
    with open(companies_file, 'r') as f:
        reader = csv.DictReader(f)
        companies = [row['company_id'] for row in reader]
    
    # Generate users
    users_file = output_dir / 'user_profiles.csv'
    generate_user_profiles(args.users, users_file)
    
    # Load user IDs
    users = []
    with open(users_file, 'r') as f:
        reader = csv.DictReader(f)
        users = [row['user_id'] for row in reader]
    
    # Generate jobs
    jobs_file = output_dir / 'job_postings.csv'
    generate_job_postings(args.jobs, companies, jobs_file)
    
    # Load job IDs
    jobs = []
    with open(jobs_file, 'r') as f:
        reader = csv.DictReader(f)
        jobs = [row['job_id'] for row in reader]
    
    # Generate applications
    applications_file = output_dir / 'job_applications.csv'
    generate_applications(args.applications, users[:min(1000000, len(users))], jobs[:min(1000000, len(jobs))], applications_file)
    
    # Generate recommendations
    recommendations_file = output_dir / 'job_recommendations.csv'
    generate_recommendations(args.recommendations, users[:min(2000000, len(users))], jobs[:min(1000000, len(jobs))], recommendations_file)
    
    print("\n" + "="*70)
    print("Data Generation Complete")
    print("="*70)
    print(f"Output directory: {output_dir}")
    print(f"Generated files:")
    print(f"  - {companies_file.name}: {args.companies:,} companies")
    print(f"  - {users_file.name}: {args.users:,} users")
    print(f"  - {jobs_file.name}: {args.jobs:,} jobs")
    print(f"  - {applications_file.name}: {args.applications:,} applications")
    print(f"  - {recommendations_file.name}: {args.recommendations:,} recommendations")
    print("="*70)


if __name__ == '__main__':
    main()
