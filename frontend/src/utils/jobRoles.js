/**
 * Job Role Data for Programmatic SEO
 * 
 * Contains job role information for dynamic landing page generation.
 * This is JSON-based for MVP - can be migrated to database later.
 */

export const JOB_ROLES = [
  {
    slug: 'software-engineer',
    name: 'Software Engineer',
    industry: 'Technology',
    keywords: ['Python', 'JavaScript', 'React', 'Node.js', 'Git', 'Agile', 'API', 'Database', 'Cloud Computing'],
    skills: ['Programming', 'Software Development', 'Problem Solving', 'Code Review', 'Testing'],
    description: 'Create a winning software engineer resume that highlights your technical skills, coding experience, and ability to build scalable applications.',
    tips: [
      'Highlight specific programming languages and frameworks',
      'Include GitHub projects and contributions',
      'Quantify your impact (e.g., "Reduced load time by 40%")',
      'Show experience with version control and CI/CD',
      'Mention cloud platforms (AWS, Azure, GCP)'
    ],
    commonMistakes: [
      'Listing too many languages without depth',
      'Missing quantifiable achievements',
      'Not including relevant projects',
      'Generic descriptions without technical details'
    ]
  },
  {
    slug: 'nursing-student',
    name: 'Nursing Student',
    industry: 'Healthcare',
    keywords: ['Patient Care', 'Clinical Rotation', 'Medication Administration', 'Vital Signs', 'HIPAA', 'CPR', 'BLS', 'Clinical Skills'],
    skills: ['Patient Assessment', 'Medical Terminology', 'Clinical Documentation', 'Team Collaboration', 'Empathy'],
    description: 'Build a standout nursing student resume that showcases your clinical experience, coursework, and passion for patient care.',
    tips: [
      'Highlight clinical rotations and patient care hours',
      'Include relevant certifications (CPR, BLS)',
      'Emphasize soft skills like empathy and communication',
      'Show experience with electronic health records',
      'Mention specific clinical skills learned'
    ],
    commonMistakes: [
      'Not highlighting clinical experience',
      'Missing relevant certifications',
      'Generic descriptions without specific skills',
      'Not showing progression in clinical rotations'
    ]
  },
  {
    slug: 'marketing-manager',
    name: 'Marketing Manager',
    industry: 'Marketing',
    keywords: ['Digital Marketing', 'SEO', 'Content Strategy', 'Social Media', 'Analytics', 'Campaign Management', 'ROI', 'Brand Management'],
    skills: ['Marketing Strategy', 'Data Analysis', 'Content Creation', 'Team Leadership', 'Budget Management'],
    description: 'Craft a compelling marketing manager resume that demonstrates your ability to drive growth, manage campaigns, and lead marketing teams.',
    tips: [
      'Quantify campaign results (ROI, conversion rates)',
      'Highlight experience with marketing tools (Google Analytics, HubSpot)',
      'Show leadership and team management experience',
      'Include budget management and P&L responsibility',
      'Demonstrate data-driven decision making'
    ],
    commonMistakes: [
      'Not quantifying campaign results',
      'Missing relevant marketing tool experience',
      'Generic job descriptions',
      'Not showing leadership capabilities'
    ]
  },
  {
    slug: 'project-manager',
    name: 'Project Manager',
    industry: 'Business',
    keywords: ['Agile', 'Scrum', 'Stakeholder Management', 'Risk Management', 'Budget', 'Timeline', 'PMP', 'JIRA', 'Project Planning'],
    skills: ['Project Planning', 'Team Coordination', 'Risk Management', 'Communication', 'Problem Solving'],
    description: 'Create a professional project manager resume that showcases your ability to deliver projects on time, within budget, and exceed stakeholder expectations.',
    tips: [
      'Highlight PMP or Agile certifications',
      'Quantify project success (budget saved, time reduced)',
      'Show experience with project management tools',
      'Demonstrate stakeholder management skills',
      'Include examples of risk mitigation'
    ],
    commonMistakes: [
      'Not showing quantifiable project outcomes',
      'Missing relevant certifications',
      'Generic project descriptions',
      'Not highlighting leadership skills'
    ]
  },
  {
    slug: 'data-analyst',
    name: 'Data Analyst',
    industry: 'Technology',
    keywords: ['SQL', 'Python', 'Excel', 'Tableau', 'Power BI', 'Data Visualization', 'Statistics', 'Machine Learning', 'ETL'],
    skills: ['Data Analysis', 'Statistical Analysis', 'Data Visualization', 'SQL', 'Python/R'],
    description: 'Build a data analyst resume that highlights your analytical skills, technical expertise, and ability to turn data into actionable insights.',
    tips: [
      'Show proficiency in SQL and data analysis tools',
      'Include examples of data-driven insights',
      'Highlight experience with visualization tools',
      'Quantify impact of your analysis',
      'Mention statistical methods and techniques'
    ],
    commonMistakes: [
      'Not showing specific tools and technologies',
      'Missing quantifiable results from analysis',
      'Generic descriptions without technical depth',
      'Not highlighting data visualization skills'
    ]
  },
  {
    slug: 'registered-nurse',
    name: 'Registered Nurse',
    industry: 'Healthcare',
    keywords: ['Patient Care', 'Medication Administration', 'Nursing Assessment', 'Electronic Health Records', 'BLS', 'ACLS', 'IV Therapy'],
    skills: ['Patient Assessment', 'Medication Administration', 'Clinical Documentation', 'Critical Thinking', 'Patient Education'],
    description: 'Develop a professional registered nurse resume that showcases your clinical expertise, certifications, and commitment to patient care.',
    tips: [
      'Highlight relevant nursing certifications',
      'Include specific clinical areas of expertise',
      'Show experience with EHR systems',
      'Quantify patient care outcomes',
      'Emphasize continuing education'
    ],
    commonMistakes: [
      'Not highlighting certifications',
      'Missing specific clinical experience',
      'Generic job descriptions',
      'Not showing professional development'
    ]
  },
  {
    slug: 'accountant',
    name: 'Accountant',
    industry: 'Finance',
    keywords: ['GAAP', 'Financial Reporting', 'Tax Preparation', 'QuickBooks', 'Excel', 'Audit', 'CPA', 'Reconciliation', 'Financial Analysis'],
    skills: ['Financial Reporting', 'Tax Preparation', 'Audit', 'Financial Analysis', 'Attention to Detail'],
    description: 'Create a professional accountant resume that demonstrates your expertise in financial reporting, tax preparation, and regulatory compliance.',
    tips: [
      'Highlight CPA or other relevant certifications',
      'Show experience with accounting software',
      'Include examples of process improvements',
      'Demonstrate knowledge of GAAP and tax regulations',
      'Quantify financial impact of your work'
    ],
    commonMistakes: [
      'Not highlighting certifications',
      'Missing specific software experience',
      'Generic descriptions',
      'Not showing regulatory knowledge'
    ]
  },
  {
    slug: 'teacher',
    name: 'Teacher',
    industry: 'Education',
    keywords: ['Curriculum Development', 'Classroom Management', 'Student Assessment', 'Lesson Planning', 'Differentiated Instruction', 'State Standards'],
    skills: ['Curriculum Development', 'Classroom Management', 'Student Assessment', 'Communication', 'Patience'],
    description: 'Build an effective teacher resume that highlights your educational background, teaching experience, and impact on student learning.',
    tips: [
      'Highlight teaching certifications and licenses',
      'Include specific grade levels and subjects',
      'Show student achievement improvements',
      'Demonstrate classroom management skills',
      'Mention professional development and training'
    ],
    commonMistakes: [
      'Not highlighting certifications',
      'Missing specific grade/subject experience',
      'Generic teaching descriptions',
      'Not showing student outcomes'
    ]
  },
  {
    slug: 'sales-representative',
    name: 'Sales Representative',
    industry: 'Sales',
    keywords: ['Lead Generation', 'Customer Relationship Management', 'Sales Pipeline', 'Quota Achievement', 'CRM', 'Negotiation', 'B2B Sales'],
    skills: ['Sales', 'Negotiation', 'Customer Relationship Management', 'Communication', 'Goal Achievement'],
    description: 'Create a results-driven sales representative resume that showcases your ability to exceed quotas, build relationships, and drive revenue.',
    tips: [
      'Quantify sales achievements (revenue, quota percentage)',
      'Highlight CRM experience',
      'Show consistent quota achievement',
      'Include examples of relationship building',
      'Demonstrate product knowledge'
    ],
    commonMistakes: [
      'Not quantifying sales results',
      'Missing CRM tool experience',
      'Generic sales descriptions',
      'Not showing consistent performance'
    ]
  },
  {
    slug: 'human-resources',
    name: 'Human Resources Specialist',
    industry: 'Human Resources',
    keywords: ['Recruitment', 'Employee Relations', 'HRIS', 'Benefits Administration', 'Talent Acquisition', 'Onboarding', 'Performance Management'],
    skills: ['Recruitment', 'Employee Relations', 'HR Administration', 'Communication', 'Conflict Resolution'],
    description: 'Develop a comprehensive HR specialist resume that demonstrates your expertise in recruitment, employee relations, and HR administration.',
    tips: [
      'Highlight HR certifications (SHRM, PHR)',
      'Show experience with HRIS systems',
      'Include recruitment metrics',
      'Demonstrate employee relations experience',
      'Mention knowledge of employment law'
    ],
    commonMistakes: [
      'Not highlighting certifications',
      'Missing HRIS experience',
      'Generic HR descriptions',
      'Not showing recruitment success'
    ]
  },
  {
    slug: 'graphic-designer',
    name: 'Graphic Designer',
    industry: 'Creative',
    keywords: ['Adobe Creative Suite', 'Photoshop', 'Illustrator', 'InDesign', 'Brand Identity', 'UI/UX', 'Typography', 'Print Design'],
    skills: ['Graphic Design', 'Adobe Creative Suite', 'Brand Identity', 'Typography', 'Creativity'],
    description: 'Create a creative graphic designer resume that showcases your design skills, portfolio highlights, and ability to create compelling visual content.',
    tips: [
      'Include portfolio link prominently',
      'Highlight proficiency in design software',
      'Show diverse design projects',
      'Demonstrate brand identity work',
      'Include client testimonials if available'
    ],
    commonMistakes: [
      'Not including portfolio link',
      'Missing specific software skills',
      'Generic design descriptions',
      'Not showing design process'
    ]
  },
  {
    slug: 'financial-analyst',
    name: 'Financial Analyst',
    industry: 'Finance',
    keywords: ['Financial Modeling', 'Excel', 'VBA', 'Financial Analysis', 'Forecasting', 'Valuation', 'CFA', 'Bloomberg', 'Financial Reporting'],
    skills: ['Financial Modeling', 'Financial Analysis', 'Excel', 'Data Analysis', 'Valuation'],
    description: 'Build a professional financial analyst resume that highlights your analytical skills, financial modeling expertise, and ability to drive business decisions.',
    tips: [
      'Highlight CFA or relevant certifications',
      'Show experience with financial modeling',
      'Include examples of financial analysis impact',
      'Demonstrate proficiency in Excel and financial tools',
      'Quantify business impact of your analysis'
    ],
    commonMistakes: [
      'Not highlighting certifications',
      'Missing financial modeling examples',
      'Generic descriptions',
      'Not showing analytical impact'
    ]
  },
  {
    slug: 'operations-manager',
    name: 'Operations Manager',
    industry: 'Operations',
    keywords: ['Process Improvement', 'Supply Chain', 'Lean Six Sigma', 'Operations Management', 'Efficiency', 'Cost Reduction', 'Team Leadership'],
    skills: ['Operations Management', 'Process Improvement', 'Team Leadership', 'Supply Chain', 'Problem Solving'],
    description: 'Create a results-oriented operations manager resume that demonstrates your ability to improve efficiency, reduce costs, and lead operations teams.',
    tips: [
      'Quantify process improvements and cost savings',
      'Highlight Lean Six Sigma certifications',
      'Show experience with operations metrics',
      'Demonstrate team leadership',
      'Include examples of efficiency gains'
    ],
    commonMistakes: [
      'Not quantifying improvements',
      'Missing relevant certifications',
      'Generic operations descriptions',
      'Not showing leadership impact'
    ]
  },
  {
    slug: 'customer-service',
    name: 'Customer Service Representative',
    industry: 'Customer Service',
    keywords: ['Customer Support', 'CRM', 'Problem Resolution', 'Communication', 'Customer Satisfaction', 'Call Center', 'Zendesk', 'Ticketing System'],
    skills: ['Customer Support', 'Problem Resolution', 'Communication', 'Patience', 'Product Knowledge'],
    description: 'Build an effective customer service resume that showcases your ability to resolve issues, maintain customer satisfaction, and handle high-volume interactions.',
    tips: [
      'Highlight customer satisfaction metrics',
      'Show experience with CRM systems',
      'Include examples of problem resolution',
      'Demonstrate communication skills',
      'Mention experience with different support channels'
    ],
    commonMistakes: [
      'Not showing customer satisfaction results',
      'Missing CRM experience',
      'Generic descriptions',
      'Not highlighting problem-solving skills'
    ]
  },
  {
    slug: 'business-analyst',
    name: 'Business Analyst',
    industry: 'Business',
    keywords: ['Requirements Gathering', 'Process Analysis', 'Stakeholder Management', 'Data Analysis', 'Agile', 'JIRA', 'Business Process', 'Documentation'],
    skills: ['Requirements Analysis', 'Process Improvement', 'Stakeholder Management', 'Data Analysis', 'Documentation'],
    description: 'Create a professional business analyst resume that demonstrates your ability to analyze business processes, gather requirements, and drive improvements.',
    tips: [
      'Show experience with requirements gathering',
      'Highlight process improvement examples',
      'Demonstrate stakeholder management',
      'Include examples of business impact',
      'Mention experience with Agile methodologies'
    ],
    commonMistakes: [
      'Not showing business impact',
      'Missing stakeholder management examples',
      'Generic descriptions',
      'Not highlighting analytical skills'
    ]
  },
  {
    slug: 'mechanical-engineer',
    name: 'Mechanical Engineer',
    industry: 'Engineering',
    keywords: ['CAD', 'SolidWorks', 'AutoCAD', 'Engineering Design', 'Manufacturing', 'Product Development', 'Prototyping', 'Technical Drawing'],
    skills: ['Engineering Design', 'CAD Software', 'Problem Solving', 'Manufacturing', 'Technical Analysis'],
    description: 'Develop a technical mechanical engineer resume that showcases your design expertise, CAD proficiency, and ability to bring products from concept to production.',
    tips: [
      'Highlight CAD software proficiency',
      'Include specific design projects',
      'Show experience with manufacturing processes',
      'Demonstrate problem-solving with examples',
      'Mention relevant engineering certifications'
    ],
    commonMistakes: [
      'Not highlighting CAD skills',
      'Missing specific project examples',
      'Generic engineering descriptions',
      'Not showing design process'
    ]
  },
  {
    slug: 'social-worker',
    name: 'Social Worker',
    industry: 'Social Services',
    keywords: ['Case Management', 'Client Assessment', 'Crisis Intervention', 'Social Services', 'Counseling', 'Advocacy', 'Documentation', 'Licensed Social Worker'],
    skills: ['Case Management', 'Client Assessment', 'Crisis Intervention', 'Empathy', 'Documentation'],
    description: 'Create a compassionate social worker resume that highlights your case management experience, client advocacy, and commitment to helping others.',
    tips: [
      'Highlight social work license',
      'Show experience with case management',
      'Include examples of client outcomes',
      'Demonstrate crisis intervention skills',
      'Mention knowledge of social services systems'
    ],
    commonMistakes: [
      'Not highlighting license',
      'Missing case management examples',
      'Generic descriptions',
      'Not showing client impact'
    ]
  },
  {
    slug: 'web-developer',
    name: 'Web Developer',
    industry: 'Technology',
    keywords: ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'Responsive Design', 'Frontend', 'Backend', 'Full Stack'],
    skills: ['Web Development', 'Frontend Development', 'Backend Development', 'Problem Solving', 'Code Quality'],
    description: 'Build a technical web developer resume that showcases your coding skills, project portfolio, and ability to create responsive, user-friendly web applications.',
    tips: [
      'Include GitHub portfolio link',
      'Highlight specific technologies and frameworks',
      'Show responsive design projects',
      'Demonstrate full-stack capabilities',
      'Include live project examples'
    ],
    commonMistakes: [
      'Not including portfolio',
      'Missing specific technology details',
      'Generic descriptions',
      'Not showing project diversity'
    ]
  },
  {
    slug: 'pharmacist',
    name: 'Pharmacist',
    industry: 'Healthcare',
    keywords: ['Pharmacy', 'Medication Dispensing', 'Patient Counseling', 'Pharmaceutical Care', 'Drug Interactions', 'PharmD', 'State License'],
    skills: ['Pharmaceutical Care', 'Medication Dispensing', 'Patient Counseling', 'Drug Knowledge', 'Attention to Detail'],
    description: 'Create a professional pharmacist resume that demonstrates your pharmaceutical expertise, patient care skills, and regulatory knowledge.',
    tips: [
      'Highlight PharmD degree and state license',
      'Show experience with medication dispensing',
      'Include patient counseling examples',
      'Demonstrate knowledge of drug interactions',
      'Mention continuing education'
    ],
    commonMistakes: [
      'Not highlighting license',
      'Missing patient care examples',
      'Generic descriptions',
      'Not showing pharmaceutical knowledge'
    ]
  },
  {
    slug: 'electrician',
    name: 'Electrician',
    industry: 'Skilled Trades',
    keywords: ['Electrical Installation', 'Wiring', 'Electrical Code', 'Troubleshooting', 'Electrical Systems', 'Licensed Electrician', 'NEC', 'Safety'],
    skills: ['Electrical Installation', 'Troubleshooting', 'Electrical Code Knowledge', 'Safety', 'Problem Solving'],
    description: 'Develop a skilled electrician resume that highlights your technical expertise, certifications, and experience with electrical systems.',
    tips: [
      'Highlight electrician license',
      'Show experience with different electrical systems',
      'Include safety certifications',
      'Demonstrate troubleshooting skills',
      'Mention knowledge of electrical codes'
    ],
    commonMistakes: [
      'Not highlighting license',
      'Missing specific system experience',
      'Generic descriptions',
      'Not showing safety knowledge'
    ]
  },
  {
    slug: 'chef',
    name: 'Chef',
    industry: 'Hospitality',
    keywords: ['Culinary Arts', 'Menu Development', 'Kitchen Management', 'Food Safety', 'Culinary Techniques', 'Recipe Development', 'Culinary School'],
    skills: ['Culinary Arts', 'Menu Development', 'Kitchen Management', 'Food Safety', 'Creativity'],
    description: 'Create a culinary chef resume that showcases your cooking expertise, menu development skills, and kitchen management experience.',
    tips: [
      'Highlight culinary education',
      'Show experience with different cuisines',
      'Include menu development examples',
      'Demonstrate kitchen management',
      'Mention food safety certifications'
    ],
    commonMistakes: [
      'Not highlighting culinary education',
      'Missing specific cuisine experience',
      'Generic descriptions',
      'Not showing management skills'
    ]
  }
];

/**
 * Get job role by slug
 * @param {string} slug - Job role slug
 * @returns {Object|null} Job role object or null if not found
 */
export const getJobRoleBySlug = (slug) => {
  return JOB_ROLES.find(role => role.slug === slug) || null;
};

/**
 * Get all job role slugs (for sitemap generation)
 * @returns {Array<string>} Array of job role slugs
 */
export const getAllJobRoleSlugs = () => {
  return JOB_ROLES.map(role => role.slug);
};

/**
 * Get top N job roles
 * @param {number} count - Number of roles to return
 * @returns {Array<Object>} Array of job role objects
 */
export const getTopJobRoles = (count = 20) => {
  return JOB_ROLES.slice(0, count);
};

export default JOB_ROLES;


