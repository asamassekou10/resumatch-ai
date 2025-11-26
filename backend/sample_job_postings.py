"""
Sample Job Posting Data Loaders

Provides realistic sample job postings across multiple industries and roles
for testing the market intelligence system without external API dependencies.

Usage:
    docker-compose exec backend python -c "from sample_job_postings import load_sample_postings; load_sample_postings()"
"""

from datetime import datetime, timedelta
from job_posting_ingestion import JobPosting, get_ingestion_manager
import logging

logger = logging.getLogger(__name__)


def create_sample_postings() -> list:
    """Create realistic sample job postings across industries"""

    now = datetime.utcnow()

    postings = [
        # Technology/Software Engineering
        JobPosting(
            job_title="Senior Python Developer",
            company_name="TechCorp Inc",
            job_description="""
            We're looking for a Senior Python Developer with 5+ years of experience.
            Required skills: Python, Django, PostgreSQL, Docker, Kubernetes, AWS
            Nice to have: Redis, Elasticsearch, Apache Kafka
            Responsibilities include designing scalable backend systems, code review, and mentoring junior developers.
            """,
            location="San Francisco, CA",
            salary_min=150000,
            salary_max=200000,
            salary_currency="USD",
            industry="Technology",
            source="indeed",
            posted_date=now - timedelta(days=5)
        ),

        JobPosting(
            job_title="Full Stack JavaScript Developer",
            company_name="WebInnovations",
            job_description="""
            Full-stack JavaScript role using modern web technologies.
            Required: React, Node.js, Express, MongoDB, Git, REST APIs
            Desired: TypeScript, GraphQL, Docker, CI/CD pipelines
            Work on exciting frontend and backend projects in a fast-paced environment.
            """,
            location="New York, NY",
            salary_min=120000,
            salary_max=160000,
            salary_currency="USD",
            industry="Technology",
            source="linkedin",
            posted_date=now - timedelta(days=3)
        ),

        JobPosting(
            job_title="Data Scientist",
            company_name="DataAnalytics Pro",
            job_description="""
            Data Science position focused on machine learning and analytics.
            Required: Python, Pandas, NumPy, Scikit-learn, SQL, Statistics
            Preferred: TensorFlow, PyTorch, Deep Learning, Spark, AWS SageMaker
            Strong background in statistics and data visualization (Matplotlib, Seaborn).
            """,
            location="Seattle, WA",
            salary_min=130000,
            salary_max=190000,
            salary_currency="USD",
            industry="Technology",
            source="indeed",
            posted_date=now - timedelta(days=2)
        ),

        JobPosting(
            job_title="DevOps Engineer",
            company_name="CloudSystems Ltd",
            job_description="""
            Build and maintain cloud infrastructure and deployment pipelines.
            Must have: Docker, Kubernetes, Linux, Jenkins, Git, AWS or Azure
            Experience with: Terraform, Ansible, Prometheus, ELK stack
            Collaborate with development teams to implement CI/CD best practices.
            """,
            location="Boston, MA",
            salary_min=140000,
            salary_max=180000,
            salary_currency="USD",
            industry="Technology",
            source="glassdoor",
            posted_date=now - timedelta(days=1)
        ),

        # Finance/Business
        JobPosting(
            job_title="Financial Analyst",
            company_name="InvestBank Corp",
            job_description="""
            Financial analysis and reporting role in investment banking.
            Required: Excel, Financial modeling, Accounting, SQL
            Preferred: Python, R, Power BI, Bloomberg Terminal
            Analyze financial statements and create investment recommendations.
            """,
            location="New York, NY",
            salary_min=80000,
            salary_max=120000,
            salary_currency="USD",
            industry="Finance",
            source="indeed",
            posted_date=now - timedelta(days=7)
        ),

        JobPosting(
            job_title="Business Intelligence Manager",
            company_name="RetailChain Global",
            job_description="""
            Lead BI initiatives and analytics projects for retail operations.
            Must have: SQL, Tableau, Power BI, Data warehousing, Business analysis
            Experience with: Python, ETL tools, Snowflake or Redshift
            Manage team of junior analysts and drive data-driven decisions.
            """,
            location="Chicago, IL",
            salary_min=100000,
            salary_max=150000,
            salary_currency="USD",
            industry="Finance",
            source="linkedin",
            posted_date=now - timedelta(days=4)
        ),

        # Marketing/Sales
        JobPosting(
            job_title="Digital Marketing Manager",
            company_name="MarketingHub",
            job_description="""
            Manage digital marketing campaigns and online presence.
            Required: SEO, SEM, Google Analytics, Content Marketing, Email Marketing
            Preferred: Marketing automation, Social Media Management, HTML/CSS
            Target salary range: $70,000 - $100,000
            """,
            location="Los Angeles, CA",
            salary_min=70000,
            salary_max=100000,
            salary_currency="USD",
            industry="Marketing",
            source="indeed",
            posted_date=now - timedelta(days=6)
        ),

        JobPosting(
            job_title="Sales Engineer",
            company_name="CloudSoftware Inc",
            job_description="""
            Sales engineer supporting enterprise software sales.
            Required: Solution selling, Technical communication, Product knowledge, Demo skills
            Preferred: Python, SQL, Cloud technologies, API integration
            Travel up to 20% to support customer accounts.
            """,
            location="Austin, TX",
            salary_min=90000,
            salary_max=130000,
            salary_currency="USD",
            industry="Sales",
            source="linkedin",
            posted_date=now - timedelta(days=5)
        ),

        # Design
        JobPosting(
            job_title="UX/UI Designer",
            company_name="DesignStudio Pro",
            job_description="""
            Design user experiences and interfaces for web and mobile applications.
            Required: Figma, User research, Wireframing, Prototyping, Design systems
            Preferred: Adobe Creative Suite, HTML/CSS basics, User testing
            Collaborate with developers and product managers.
            """,
            location="San Diego, CA",
            salary_min=75000,
            salary_max=115000,
            salary_currency="USD",
            industry="Design",
            source="dribbble",
            posted_date=now - timedelta(days=3)
        ),

        # Healthcare
        JobPosting(
            job_title="Clinical Nurse Specialist",
            company_name="City Medical Center",
            job_description="""
            Provide direct patient care and clinical leadership.
            Required: RN license, Clinical nursing experience, Patient assessment, EMR systems
            Preferred: BScN degree, Critical care experience, Teaching skills
            Weekend and holiday rotation required.
            """,
            location="Houston, TX",
            salary_min=60000,
            salary_max=85000,
            salary_currency="USD",
            industry="Healthcare",
            source="indeed",
            posted_date=now - timedelta(days=8)
        ),

        # Education
        JobPosting(
            job_title="High School Math Teacher",
            company_name="Central Academy",
            job_description="""
            Teach mathematics to high school students (grades 9-12).
            Required: Teaching certification, Math expertise, Lesson planning, Assessment
            Preferred: Technology integration, AP Calculus experience, Tutoring
            Salary range: $50,000 - $70,000 based on experience.
            """,
            location="Denver, CO",
            salary_min=50000,
            salary_max=70000,
            salary_currency="USD",
            industry="Education",
            source="indeed",
            posted_date=now - timedelta(days=10)
        ),

        # ============================================
        # FINANCE INDUSTRY - EXPANDED
        # ============================================
        JobPosting(
            job_title="Staff Accountant",
            company_name="Big Four Accounting",
            job_description="""
            Entry-level accounting position at a major accounting firm.
            Required: CPA eligible, Bachelor's in Accounting, Excel, QuickBooks, General ledger
            Preferred: Audit experience, Tax preparation, Month-end close, Journal entries
            Handle accounts payable, accounts receivable, and financial reconciliations.
            """,
            location="New York, NY",
            salary_min=55000,
            salary_max=75000,
            salary_currency="USD",
            industry="Finance",
            source="indeed",
            posted_date=now - timedelta(days=2)
        ),

        JobPosting(
            job_title="Senior Accountant",
            company_name="Corporate Finance Solutions",
            job_description="""
            Senior accounting role overseeing financial operations.
            Required: CPA, 5+ years accounting experience, GAAP, Financial reporting, Excel
            Skills: Month-end close, Reconciliations, Audit support, ERP systems (SAP, Oracle)
            Lead a team of junior accountants and ensure compliance with accounting standards.
            """,
            location="Chicago, IL",
            salary_min=85000,
            salary_max=110000,
            salary_currency="USD",
            industry="Finance",
            source="linkedin",
            posted_date=now - timedelta(days=3)
        ),

        JobPosting(
            job_title="Tax Accountant",
            company_name="TaxPro Services",
            job_description="""
            Tax preparation and planning for corporate clients.
            Required: CPA, Tax preparation, Corporate tax, Tax research, Tax software
            Skills: Federal and state tax returns, Tax compliance, IRS regulations, Excel
            Prepare and review complex tax returns for businesses and individuals.
            """,
            location="Houston, TX",
            salary_min=70000,
            salary_max=95000,
            salary_currency="USD",
            industry="Finance",
            source="indeed",
            posted_date=now - timedelta(days=1)
        ),

        JobPosting(
            job_title="Investment Banker",
            company_name="Goldman Stanley Partners",
            job_description="""
            Investment banking associate position focusing on M&A transactions.
            Required: MBA preferred, Financial modeling, Valuation, Due diligence, Excel
            Skills: DCF analysis, Comparable company analysis, Pitch books, Capital markets
            Work on high-profile mergers and acquisitions for Fortune 500 companies.
            """,
            location="New York, NY",
            salary_min=120000,
            salary_max=180000,
            salary_currency="USD",
            industry="Finance",
            source="linkedin",
            posted_date=now - timedelta(days=4)
        ),

        JobPosting(
            job_title="Portfolio Manager",
            company_name="Wealth Management Inc",
            job_description="""
            Manage investment portfolios for high-net-worth clients.
            Required: CFA, Portfolio management, Asset allocation, Risk management, Bloomberg
            Skills: Equity research, Fixed income, Alternative investments, Client relations
            Develop and execute investment strategies aligned with client goals.
            """,
            location="Boston, MA",
            salary_min=130000,
            salary_max=200000,
            salary_currency="USD",
            industry="Finance",
            source="linkedin",
            posted_date=now - timedelta(days=5)
        ),

        JobPosting(
            job_title="Accounts Payable Specialist",
            company_name="Manufacturing Corp",
            job_description="""
            Process vendor invoices and manage accounts payable operations.
            Required: Accounts payable, Invoice processing, Vendor management, Data entry
            Skills: Excel, ERP systems, Reconciliation, Payment processing, Attention to detail
            Ensure timely and accurate payment of vendor invoices.
            """,
            location="Detroit, MI",
            salary_min=45000,
            salary_max=60000,
            salary_currency="USD",
            industry="Finance",
            source="indeed",
            posted_date=now - timedelta(days=6)
        ),

        JobPosting(
            job_title="Financial Controller",
            company_name="StartupTech Inc",
            job_description="""
            Lead financial operations for a growing technology company.
            Required: CPA, Financial planning, Budgeting, GAAP, Financial reporting
            Skills: Cash flow management, Internal controls, Audit, Team leadership, NetSuite
            Report to CFO and oversee accounting team of 5 professionals.
            """,
            location="San Francisco, CA",
            salary_min=150000,
            salary_max=200000,
            salary_currency="USD",
            industry="Finance",
            source="linkedin",
            posted_date=now - timedelta(days=3)
        ),

        JobPosting(
            job_title="Credit Analyst",
            company_name="Regional Bank Corp",
            job_description="""
            Analyze credit risk for commercial lending decisions.
            Required: Credit analysis, Financial statement analysis, Risk assessment, Excel
            Skills: Commercial lending, Loan documentation, Credit scoring, Industry research
            Evaluate loan applications and recommend credit limits for business clients.
            """,
            location="Atlanta, GA",
            salary_min=60000,
            salary_max=85000,
            salary_currency="USD",
            industry="Finance",
            source="indeed",
            posted_date=now - timedelta(days=7)
        ),

        JobPosting(
            job_title="Bookkeeper",
            company_name="Small Business Services",
            job_description="""
            Full-charge bookkeeping for small and medium businesses.
            Required: Bookkeeping, QuickBooks, Bank reconciliation, Payroll, Invoicing
            Skills: Accounts receivable, Accounts payable, General ledger, Financial reports
            Manage day-to-day financial transactions for multiple clients.
            """,
            location="Phoenix, AZ",
            salary_min=40000,
            salary_max=55000,
            salary_currency="USD",
            industry="Finance",
            source="indeed",
            posted_date=now - timedelta(days=2)
        ),

        JobPosting(
            job_title="Auditor",
            company_name="Audit Partners LLP",
            job_description="""
            Conduct financial audits for corporate clients.
            Required: CPA, Auditing, GAAP, Internal controls, Risk assessment
            Skills: Audit planning, Workpapers, Financial analysis, Sox compliance, Excel
            Travel up to 40% for on-site audits at client locations.
            """,
            location="Philadelphia, PA",
            salary_min=65000,
            salary_max=90000,
            salary_currency="USD",
            industry="Finance",
            source="linkedin",
            posted_date=now - timedelta(days=4)
        ),

        # ============================================
        # HEALTHCARE INDUSTRY - EXPANDED
        # ============================================
        JobPosting(
            job_title="Registered Nurse",
            company_name="Metro General Hospital",
            job_description="""
            Provide direct patient care in a fast-paced hospital environment.
            Required: RN license, Patient assessment, Medication administration, EMR
            Skills: Critical thinking, IV therapy, Patient education, Team collaboration
            12-hour shifts with rotating weekends required.
            """,
            location="Los Angeles, CA",
            salary_min=70000,
            salary_max=95000,
            salary_currency="USD",
            industry="Healthcare",
            source="indeed",
            posted_date=now - timedelta(days=1)
        ),

        JobPosting(
            job_title="Medical Assistant",
            company_name="Family Practice Clinic",
            job_description="""
            Support physicians with clinical and administrative tasks.
            Required: Medical assistant certification, Vital signs, Phlebotomy, EHR
            Skills: Patient intake, Scheduling, Medical terminology, Injections
            Work in a friendly primary care environment with standard hours.
            """,
            location="San Diego, CA",
            salary_min=35000,
            salary_max=48000,
            salary_currency="USD",
            industry="Healthcare",
            source="indeed",
            posted_date=now - timedelta(days=3)
        ),

        JobPosting(
            job_title="Physician Assistant",
            company_name="Urgent Care Network",
            job_description="""
            Provide medical care under physician supervision at urgent care centers.
            Required: PA license, Diagnosis, Treatment planning, Prescribing, Procedures
            Skills: Emergency medicine, Patient assessment, Medical decision-making, EHR
            Full-time position with competitive benefits package.
            """,
            location="Miami, FL",
            salary_min=100000,
            salary_max=130000,
            salary_currency="USD",
            industry="Healthcare",
            source="linkedin",
            posted_date=now - timedelta(days=2)
        ),

        JobPosting(
            job_title="Physical Therapist",
            company_name="Rehabilitation Center",
            job_description="""
            Develop and implement physical therapy treatment plans.
            Required: PT license, Patient evaluation, Treatment planning, Exercise therapy
            Skills: Manual therapy, Gait training, Patient education, Documentation
            Work with patients recovering from injuries and surgeries.
            """,
            location="Denver, CO",
            salary_min=75000,
            salary_max=100000,
            salary_currency="USD",
            industry="Healthcare",
            source="indeed",
            posted_date=now - timedelta(days=5)
        ),

        JobPosting(
            job_title="Healthcare Administrator",
            company_name="Community Health System",
            job_description="""
            Oversee daily operations of healthcare facilities.
            Required: Healthcare administration, Budget management, Staff management, Compliance
            Skills: Strategic planning, Quality improvement, Medicare regulations, Leadership
            MBA in Healthcare Administration preferred.
            """,
            location="Chicago, IL",
            salary_min=90000,
            salary_max=130000,
            salary_currency="USD",
            industry="Healthcare",
            source="linkedin",
            posted_date=now - timedelta(days=4)
        ),

        JobPosting(
            job_title="Medical Coder",
            company_name="Health Billing Services",
            job_description="""
            Assign medical codes for diagnoses and procedures for billing.
            Required: CPC certification, ICD-10, CPT coding, Medical terminology, EHR
            Skills: Billing, Insurance claims, Compliance, Attention to detail, HIPAA
            Remote work option available for experienced coders.
            """,
            location="Remote",
            salary_min=50000,
            salary_max=70000,
            salary_currency="USD",
            industry="Healthcare",
            source="indeed",
            posted_date=now - timedelta(days=6)
        ),

        JobPosting(
            job_title="Pharmacist",
            company_name="National Pharmacy Chain",
            job_description="""
            Dispense medications and provide patient counseling.
            Required: PharmD, Pharmacist license, Medication dispensing, Drug interactions
            Skills: Patient counseling, Prescription verification, Inventory management, Customer service
            Full-time with flexible scheduling options.
            """,
            location="Seattle, WA",
            salary_min=120000,
            salary_max=145000,
            salary_currency="USD",
            industry="Healthcare",
            source="indeed",
            posted_date=now - timedelta(days=3)
        ),

        # ============================================
        # SECURITY/CYBERSECURITY - EXPANDED
        # ============================================
        JobPosting(
            job_title="Security Analyst",
            company_name="CyberDefense Corp",
            job_description="""
            Monitor and analyze security threats to protect enterprise systems.
            Required: Security monitoring, SIEM, Incident response, Threat analysis, TCP/IP
            Skills: Splunk, Network security, Malware analysis, Firewall management, IDS/IPS
            SOC experience preferred, must have Security+ or equivalent certification.
            """,
            location="Washington, DC",
            salary_min=85000,
            salary_max=120000,
            salary_currency="USD",
            industry="Security",
            source="linkedin",
            posted_date=now - timedelta(days=1)
        ),

        JobPosting(
            job_title="Penetration Tester",
            company_name="InfoSec Consultants",
            job_description="""
            Conduct authorized penetration testing and security assessments.
            Required: Penetration testing, Vulnerability assessment, Python, Kali Linux
            Skills: OWASP, Network exploitation, Web application security, Report writing
            OSCP or CEH certification required.
            """,
            location="San Francisco, CA",
            salary_min=110000,
            salary_max=160000,
            salary_currency="USD",
            industry="Security",
            source="linkedin",
            posted_date=now - timedelta(days=2)
        ),

        JobPosting(
            job_title="Information Security Manager",
            company_name="Enterprise Security Inc",
            job_description="""
            Lead information security program for large enterprise.
            Required: CISSP, Risk management, Security policies, Compliance, Team leadership
            Skills: ISO 27001, NIST, SOC 2, Vendor management, Budget management
            Report to CISO and manage team of 8 security professionals.
            """,
            location="New York, NY",
            salary_min=140000,
            salary_max=190000,
            salary_currency="USD",
            industry="Security",
            source="linkedin",
            posted_date=now - timedelta(days=3)
        ),

        JobPosting(
            job_title="Security Engineer",
            company_name="Cloud Security Solutions",
            job_description="""
            Design and implement security controls for cloud infrastructure.
            Required: AWS security, Azure security, Cloud architecture, IAM, Encryption
            Skills: Terraform, Docker security, Kubernetes security, SIEM integration
            Experience with DevSecOps practices required.
            """,
            location="Seattle, WA",
            salary_min=130000,
            salary_max=175000,
            salary_currency="USD",
            industry="Security",
            source="indeed",
            posted_date=now - timedelta(days=4)
        ),

        JobPosting(
            job_title="Compliance Analyst",
            company_name="Financial Compliance Corp",
            job_description="""
            Ensure regulatory compliance for financial services firm.
            Required: Compliance, Risk assessment, Regulatory knowledge, Documentation
            Skills: SOX compliance, PCI-DSS, GDPR, Audit support, Policy development
            Work with legal and IT teams to maintain compliance posture.
            """,
            location="Boston, MA",
            salary_min=70000,
            salary_max=95000,
            salary_currency="USD",
            industry="Security",
            source="indeed",
            posted_date=now - timedelta(days=5)
        ),

        JobPosting(
            job_title="Incident Response Analyst",
            company_name="Threat Intelligence Inc",
            job_description="""
            Respond to and investigate security incidents.
            Required: Incident response, Digital forensics, Malware analysis, SIEM
            Skills: Log analysis, Threat hunting, Memory forensics, Network forensics
            On-call rotation required for 24/7 incident coverage.
            """,
            location="Austin, TX",
            salary_min=90000,
            salary_max=130000,
            salary_currency="USD",
            industry="Security",
            source="linkedin",
            posted_date=now - timedelta(days=2)
        ),

        # ============================================
        # MARKETING - EXPANDED
        # ============================================
        JobPosting(
            job_title="Content Marketing Manager",
            company_name="Digital Media Agency",
            job_description="""
            Develop and execute content marketing strategies.
            Required: Content strategy, Blog writing, SEO, Content calendar, Analytics
            Skills: WordPress, Social media, Email marketing, Copywriting, A/B testing
            Lead team of content writers and coordinate with design team.
            """,
            location="Los Angeles, CA",
            salary_min=80000,
            salary_max=110000,
            salary_currency="USD",
            industry="Marketing",
            source="indeed",
            posted_date=now - timedelta(days=2)
        ),

        JobPosting(
            job_title="Social Media Manager",
            company_name="Brand Builders Inc",
            job_description="""
            Manage social media presence across multiple platforms.
            Required: Social media management, Content creation, Community management, Analytics
            Skills: Instagram, TikTok, LinkedIn, Facebook ads, Influencer marketing
            Create engaging content and grow brand following.
            """,
            location="Miami, FL",
            salary_min=55000,
            salary_max=80000,
            salary_currency="USD",
            industry="Marketing",
            source="linkedin",
            posted_date=now - timedelta(days=3)
        ),

        JobPosting(
            job_title="SEO Specialist",
            company_name="Search Marketing Experts",
            job_description="""
            Optimize websites for search engine rankings.
            Required: SEO, Keyword research, Google Analytics, Technical SEO, Link building
            Skills: SEMrush, Ahrefs, Content optimization, Site audits, Reporting
            Improve organic traffic and rankings for client websites.
            """,
            location="San Francisco, CA",
            salary_min=65000,
            salary_max=95000,
            salary_currency="USD",
            industry="Marketing",
            source="indeed",
            posted_date=now - timedelta(days=4)
        ),

        JobPosting(
            job_title="Marketing Analyst",
            company_name="Consumer Brands Corp",
            job_description="""
            Analyze marketing campaign performance and consumer behavior.
            Required: Marketing analytics, Data analysis, Excel, Google Analytics, SQL
            Skills: Tableau, A/B testing, Market research, Campaign tracking, ROI analysis
            Provide insights to optimize marketing spend and strategy.
            """,
            location="Chicago, IL",
            salary_min=70000,
            salary_max=100000,
            salary_currency="USD",
            industry="Marketing",
            source="linkedin",
            posted_date=now - timedelta(days=5)
        ),

        # ============================================
        # HUMAN RESOURCES - EXPANDED
        # ============================================
        JobPosting(
            job_title="HR Generalist",
            company_name="Corporate HR Solutions",
            job_description="""
            Handle full spectrum of HR functions for growing company.
            Required: HR administration, Employee relations, Recruiting, HRIS, Compliance
            Skills: Onboarding, Benefits administration, Performance management, Training
            SHRM-CP certification preferred.
            """,
            location="Dallas, TX",
            salary_min=55000,
            salary_max=75000,
            salary_currency="USD",
            industry="Human Resources",
            source="indeed",
            posted_date=now - timedelta(days=2)
        ),

        JobPosting(
            job_title="Talent Acquisition Specialist",
            company_name="Tech Talent Recruiters",
            job_description="""
            Source and recruit top talent for technology positions.
            Required: Technical recruiting, Sourcing, ATS, LinkedIn Recruiter, Interviewing
            Skills: Candidate screening, Offer negotiation, Employer branding, Pipeline management
            Experience recruiting software engineers and data scientists preferred.
            """,
            location="San Jose, CA",
            salary_min=70000,
            salary_max=100000,
            salary_currency="USD",
            industry="Human Resources",
            source="linkedin",
            posted_date=now - timedelta(days=3)
        ),

        JobPosting(
            job_title="Compensation Analyst",
            company_name="Enterprise HR Consulting",
            job_description="""
            Analyze and design compensation structures and programs.
            Required: Compensation analysis, Market benchmarking, Excel, HRIS, Salary surveys
            Skills: Job evaluation, Pay equity analysis, Benefits analysis, Data analysis
            Experience with Radford or Mercer surveys preferred.
            """,
            location="New York, NY",
            salary_min=75000,
            salary_max=105000,
            salary_currency="USD",
            industry="Human Resources",
            source="indeed",
            posted_date=now - timedelta(days=4)
        ),

        # ============================================
        # SALES - EXPANDED
        # ============================================
        JobPosting(
            job_title="Account Executive",
            company_name="SaaS Solutions Inc",
            job_description="""
            Sell enterprise software solutions to mid-market companies.
            Required: B2B sales, Solution selling, CRM, Sales presentations, Negotiation
            Skills: Salesforce, Pipeline management, Cold calling, Demo skills, Closing
            OTE $150K-$200K with uncapped commission.
            """,
            location="Boston, MA",
            salary_min=80000,
            salary_max=120000,
            salary_currency="USD",
            industry="Sales",
            source="linkedin",
            posted_date=now - timedelta(days=1)
        ),

        JobPosting(
            job_title="Business Development Representative",
            company_name="Growth Tech Startup",
            job_description="""
            Generate leads and qualify prospects for sales team.
            Required: Lead generation, Cold calling, Email outreach, Salesforce, Prospecting
            Skills: LinkedIn Sales Navigator, Objection handling, Appointment setting
            Great opportunity for entry-level sales career in technology.
            """,
            location="Austin, TX",
            salary_min=50000,
            salary_max=70000,
            salary_currency="USD",
            industry="Sales",
            source="indeed",
            posted_date=now - timedelta(days=2)
        ),

        JobPosting(
            job_title="Sales Manager",
            company_name="Enterprise Solutions Corp",
            job_description="""
            Lead team of 8 account executives and drive revenue growth.
            Required: Sales leadership, Coaching, Forecasting, Territory planning, CRM
            Skills: Team management, Performance management, Strategic selling, Executive presence
            5+ years of sales leadership experience required.
            """,
            location="Chicago, IL",
            salary_min=120000,
            salary_max=160000,
            salary_currency="USD",
            industry="Sales",
            source="linkedin",
            posted_date=now - timedelta(days=3)
        ),

        # ============================================
        # EDUCATION - EXPANDED
        # ============================================
        JobPosting(
            job_title="Elementary School Teacher",
            company_name="Sunny Valley School District",
            job_description="""
            Teach elementary students in grades K-5.
            Required: Teaching credential, Classroom management, Lesson planning, Differentiation
            Skills: Student assessment, Parent communication, Technology integration, IEP
            Full benefits and summer vacation included.
            """,
            location="Phoenix, AZ",
            salary_min=45000,
            salary_max=65000,
            salary_currency="USD",
            industry="Education",
            source="indeed",
            posted_date=now - timedelta(days=3)
        ),

        JobPosting(
            job_title="Instructional Designer",
            company_name="Corporate Training Solutions",
            job_description="""
            Design and develop corporate training programs and e-learning.
            Required: Instructional design, E-learning development, ADDIE, LMS, Storyboarding
            Skills: Articulate, Adobe Captivate, Video production, Adult learning, Assessment design
            Create engaging training content for Fortune 500 clients.
            """,
            location="Remote",
            salary_min=70000,
            salary_max=95000,
            salary_currency="USD",
            industry="Education",
            source="linkedin",
            posted_date=now - timedelta(days=4)
        ),

        JobPosting(
            job_title="University Professor",
            company_name="State University",
            job_description="""
            Teach computer science courses and conduct research.
            Required: PhD, Research experience, Teaching experience, Publication record
            Skills: Curriculum development, Grant writing, Mentoring, Academic writing
            Tenure-track position with research funding support.
            """,
            location="Boston, MA",
            salary_min=90000,
            salary_max=130000,
            salary_currency="USD",
            industry="Education",
            source="indeed",
            posted_date=now - timedelta(days=5)
        ),
    ]

    return postings


def load_sample_postings(db=None):
    """
    Load sample job postings into the system.

    Can be called from command line:
        docker-compose exec backend python init_sample_data.py

    Args:
        db: SQLAlchemy database instance (optional)
    """
    try:
        from app import db as app_db

        db = db or app_db

        # Get ingestion manager
        manager = get_ingestion_manager(db)

        # Create sample postings
        postings = create_sample_postings()

        logger.info(f"Loading {len(postings)} sample job postings...")

        # Ingest postings with skill extraction
        result = manager.ingest_postings(postings, extract_skills=True)

        logger.info(f"Sample postings loaded: {result}")
        print(f"\n✅ Sample Job Postings Loaded Successfully!")
        print(f"   Postings ingested: {result.get('postings_ingested', 0)}")
        print(f"   Skills extracted: {result.get('skills_extracted', 0)}")
        print(f"   Timestamp: {result.get('timestamp')}\n")

        return result

    except Exception as e:
        logger.error(f"Failed to load sample postings: {str(e)}")
        print(f"❌ Error loading sample postings: {str(e)}")
        return {'error': str(e)}


if __name__ == '__main__':
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Load sample data
    load_sample_postings()
