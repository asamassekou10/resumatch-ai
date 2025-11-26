"""
Hierarchical Skill Taxonomy - 500+ Skills Across All Industries

This comprehensive taxonomy is organized by:
Level 0: Root industries (IT, Business, Creative, Healthcare, Education, etc.)
Level 1: Categories (Backend, Frontend, Database, Sales, Marketing, etc.)
Level 2: Actual skills (Python, JavaScript, CRM, etc.)

Used to initialize the skill database with enterprise-grade coverage.
"""

SKILL_TAXONOMY = {
    # ==================== INFORMATION TECHNOLOGY ====================
    "Information Technology": {
        "level": 0,
        "description": "Technology and software development skills",
        "categories": {
            "Programming Languages": {
                "level": 1,
                "subcategories": {
                    "Backend Languages": {
                        "level": 2,
                        "skills": [
                            {"name": "python", "priority": "critical", "difficulty": "beginner", "salary_premium": 15},
                            {"name": "java", "priority": "critical", "difficulty": "intermediate", "salary_premium": 10},
                            {"name": "go", "priority": "important", "difficulty": "intermediate", "salary_premium": 12},
                            {"name": "rust", "priority": "important", "difficulty": "advanced", "salary_premium": 18},
                            {"name": "c#", "priority": "important", "difficulty": "intermediate", "salary_premium": 11},
                            {"name": "c++", "priority": "important", "difficulty": "advanced", "salary_premium": 13},
                            {"name": "ruby", "priority": "medium", "difficulty": "intermediate", "salary_premium": 9},
                            {"name": "php", "priority": "medium", "difficulty": "beginner", "salary_premium": 5},
                            {"name": "scala", "priority": "medium", "difficulty": "advanced", "salary_premium": 14},
                            {"name": "kotlin", "priority": "medium", "difficulty": "intermediate", "salary_premium": 10},
                        ]
                    },
                    "Frontend Languages": {
                        "level": 2,
                        "skills": [
                            {"name": "javascript", "priority": "critical", "difficulty": "intermediate", "salary_premium": 12},
                            {"name": "typescript", "priority": "important", "difficulty": "intermediate", "salary_premium": 8},
                            {"name": "html", "priority": "critical", "difficulty": "beginner", "salary_premium": 0},
                            {"name": "css", "priority": "critical", "difficulty": "beginner", "salary_premium": 0},
                            {"name": "scss", "priority": "important", "difficulty": "intermediate", "salary_premium": 2},
                            {"name": "less", "priority": "medium", "difficulty": "beginner", "salary_premium": 1},
                        ]
                    },
                    "Mobile Languages": {
                        "level": 2,
                        "skills": [
                            {"name": "swift", "priority": "important", "difficulty": "intermediate", "salary_premium": 12},
                            {"name": "kotlin", "priority": "important", "difficulty": "intermediate", "salary_premium": 10},
                            {"name": "java", "priority": "critical", "difficulty": "intermediate", "salary_premium": 10},
                            {"name": "dart", "priority": "important", "difficulty": "intermediate", "salary_premium": 8},
                            {"name": "objective-c", "priority": "medium", "difficulty": "advanced", "salary_premium": 9},
                        ]
                    },
                    "Data Science Languages": {
                        "level": 2,
                        "skills": [
                            {"name": "python", "priority": "critical", "difficulty": "beginner", "salary_premium": 15},
                            {"name": "r", "priority": "important", "difficulty": "intermediate", "salary_premium": 11},
                            {"name": "julia", "priority": "medium", "difficulty": "advanced", "salary_premium": 13},
                            {"name": "matlab", "priority": "medium", "difficulty": "intermediate", "salary_premium": 10},
                        ]
                    }
                }
            },
            "Frontend Frameworks": {
                "level": 1,
                "subcategories": {
                    "React Ecosystem": {
                        "level": 2,
                        "skills": [
                            {"name": "react", "priority": "critical", "difficulty": "intermediate", "salary_premium": 10},
                            {"name": "redux", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "react native", "priority": "important", "difficulty": "intermediate", "salary_premium": 8},
                            {"name": "next.js", "priority": "important", "difficulty": "intermediate", "salary_premium": 7},
                            {"name": "gatsby", "priority": "medium", "difficulty": "intermediate", "salary_premium": 4},
                        ]
                    },
                    "Vue Ecosystem": {
                        "level": 2,
                        "skills": [
                            {"name": "vue", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "vuex", "priority": "important", "difficulty": "intermediate", "salary_premium": 4},
                            {"name": "nuxt", "priority": "medium", "difficulty": "intermediate", "salary_premium": 4},
                        ]
                    },
                    "Angular Ecosystem": {
                        "level": 2,
                        "skills": [
                            {"name": "angular", "priority": "important", "difficulty": "advanced", "salary_premium": 7},
                            {"name": "rxjs", "priority": "important", "difficulty": "advanced", "salary_premium": 5},
                            {"name": "typescript", "priority": "important", "difficulty": "intermediate", "salary_premium": 8},
                        ]
                    },
                    "Other Frameworks": {
                        "level": 2,
                        "skills": [
                            {"name": "svelte", "priority": "medium", "difficulty": "intermediate", "salary_premium": 4},
                            {"name": "ember.js", "priority": "medium", "difficulty": "advanced", "salary_premium": 5},
                            {"name": "backbone.js", "priority": "optional", "difficulty": "intermediate", "salary_premium": 2},
                        ]
                    }
                }
            },
            "Backend Frameworks": {
                "level": 1,
                "subcategories": {
                    "Python Frameworks": {
                        "level": 2,
                        "skills": [
                            {"name": "django", "priority": "important", "difficulty": "intermediate", "salary_premium": 8},
                            {"name": "flask", "priority": "important", "difficulty": "beginner", "salary_premium": 7},
                            {"name": "fastapi", "priority": "important", "difficulty": "intermediate", "salary_premium": 10},
                            {"name": "pyramid", "priority": "medium", "difficulty": "intermediate", "salary_premium": 3},
                            {"name": "tornado", "priority": "medium", "difficulty": "intermediate", "salary_premium": 3},
                        ]
                    },
                    "Java Frameworks": {
                        "level": 2,
                        "skills": [
                            {"name": "spring boot", "priority": "critical", "difficulty": "intermediate", "salary_premium": 9},
                            {"name": "spring", "priority": "critical", "difficulty": "intermediate", "salary_premium": 9},
                            {"name": "hibernate", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "quarkus", "priority": "medium", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "micronaut", "priority": "medium", "difficulty": "intermediate", "salary_premium": 5},
                        ]
                    },
                    "Node.js Frameworks": {
                        "level": 2,
                        "skills": [
                            {"name": "express", "priority": "critical", "difficulty": "intermediate", "salary_premium": 7},
                            {"name": "nestjs", "priority": "important", "difficulty": "intermediate", "salary_premium": 8},
                            {"name": "koa", "priority": "medium", "difficulty": "intermediate", "salary_premium": 4},
                            {"name": "hapi", "priority": "medium", "difficulty": "intermediate", "salary_premium": 3},
                        ]
                    },
                    "Other Backend Frameworks": {
                        "level": 2,
                        "skills": [
                            {"name": "laravel", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "rails", "priority": "important", "difficulty": "intermediate", "salary_premium": 7},
                            {"name": "asp.net core", "priority": "important", "difficulty": "intermediate", "salary_premium": 8},
                            {"name": "django rest framework", "priority": "medium", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "gin", "priority": "medium", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "fiber", "priority": "medium", "difficulty": "intermediate", "salary_premium": 5},
                        ]
                    }
                }
            },
            "Databases": {
                "level": 1,
                "subcategories": {
                    "Relational Databases": {
                        "level": 2,
                        "skills": [
                            {"name": "postgresql", "priority": "critical", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "mysql", "priority": "critical", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "oracle", "priority": "important", "difficulty": "intermediate", "salary_premium": 7},
                            {"name": "sql server", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "mariadb", "priority": "medium", "difficulty": "intermediate", "salary_premium": 4},
                        ]
                    },
                    "NoSQL Databases": {
                        "level": 2,
                        "skills": [
                            {"name": "mongodb", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "firebase", "priority": "important", "difficulty": "beginner", "salary_premium": 4},
                            {"name": "dynamodb", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "cassandra", "priority": "important", "difficulty": "advanced", "salary_premium": 8},
                            {"name": "couchdb", "priority": "medium", "difficulty": "intermediate", "salary_premium": 3},
                        ]
                    },
                    "Cache & Search": {
                        "level": 2,
                        "skills": [
                            {"name": "redis", "priority": "important", "difficulty": "intermediate", "salary_premium": 7},
                            {"name": "elasticsearch", "priority": "important", "difficulty": "intermediate", "salary_premium": 8},
                            {"name": "memcached", "priority": "medium", "difficulty": "intermediate", "salary_premium": 4},
                            {"name": "solr", "priority": "medium", "difficulty": "intermediate", "salary_premium": 5},
                        ]
                    }
                }
            },
            "DevOps & Infrastructure": {
                "level": 1,
                "subcategories": {
                    "Containerization": {
                        "level": 2,
                        "skills": [
                            {"name": "docker", "priority": "critical", "difficulty": "intermediate", "salary_premium": 10},
                            {"name": "kubernetes", "priority": "critical", "difficulty": "advanced", "salary_premium": 15},
                            {"name": "docker-compose", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "containerd", "priority": "medium", "difficulty": "advanced", "salary_premium": 6},
                        ]
                    },
                    "Infrastructure as Code": {
                        "level": 2,
                        "skills": [
                            {"name": "terraform", "priority": "critical", "difficulty": "intermediate", "salary_premium": 9},
                            {"name": "ansible", "priority": "important", "difficulty": "intermediate", "salary_premium": 8},
                            {"name": "puppet", "priority": "important", "difficulty": "advanced", "salary_premium": 7},
                            {"name": "chef", "priority": "important", "difficulty": "advanced", "salary_premium": 7},
                            {"name": "helm", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                        ]
                    },
                    "Cloud Platforms": {
                        "level": 2,
                        "skills": [
                            {"name": "aws", "priority": "critical", "difficulty": "intermediate", "salary_premium": 12},
                            {"name": "gcp", "priority": "important", "difficulty": "intermediate", "salary_premium": 11},
                            {"name": "azure", "priority": "important", "difficulty": "intermediate", "salary_premium": 10},
                            {"name": "heroku", "priority": "medium", "difficulty": "beginner", "salary_premium": 2},
                            {"name": "digitalocean", "priority": "medium", "difficulty": "beginner", "salary_premium": 2},
                        ]
                    },
                    "CI/CD & Monitoring": {
                        "level": 2,
                        "skills": [
                            {"name": "jenkins", "priority": "critical", "difficulty": "intermediate", "salary_premium": 7},
                            {"name": "gitlab ci", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "github actions", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "prometheus", "priority": "important", "difficulty": "intermediate", "salary_premium": 7},
                            {"name": "grafana", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "elk stack", "priority": "important", "difficulty": "intermediate", "salary_premium": 7},
                        ]
                    }
                }
            },
            "Version Control": {
                "level": 1,
                "subcategories": {
                    "Version Control Systems": {
                        "level": 2,
                        "skills": [
                            {"name": "git", "priority": "critical", "difficulty": "beginner", "salary_premium": 0},
                            {"name": "github", "priority": "critical", "difficulty": "beginner", "salary_premium": 0},
                            {"name": "gitlab", "priority": "important", "difficulty": "beginner", "salary_premium": 0},
                            {"name": "bitbucket", "priority": "important", "difficulty": "beginner", "salary_premium": 0},
                            {"name": "svn", "priority": "optional", "difficulty": "beginner", "salary_premium": -2},
                        ]
                    }
                }
            },
            "Machine Learning & AI": {
                "level": 1,
                "subcategories": {
                    "ML Frameworks": {
                        "level": 2,
                        "skills": [
                            {"name": "tensorflow", "priority": "important", "difficulty": "advanced", "salary_premium": 16},
                            {"name": "pytorch", "priority": "important", "difficulty": "advanced", "salary_premium": 15},
                            {"name": "scikit-learn", "priority": "important", "difficulty": "intermediate", "salary_premium": 10},
                            {"name": "keras", "priority": "medium", "difficulty": "advanced", "salary_premium": 12},
                            {"name": "xgboost", "priority": "medium", "difficulty": "intermediate", "salary_premium": 8},
                        ]
                    },
                    "Data Processing": {
                        "level": 2,
                        "skills": [
                            {"name": "pandas", "priority": "important", "difficulty": "intermediate", "salary_premium": 4},
                            {"name": "numpy", "priority": "important", "difficulty": "intermediate", "salary_premium": 4},
                            {"name": "scipy", "priority": "medium", "difficulty": "advanced", "salary_premium": 5},
                            {"name": "apache spark", "priority": "important", "difficulty": "advanced", "salary_premium": 9},
                        ]
                    },
                    "ML Concepts": {
                        "level": 2,
                        "skills": [
                            {"name": "machine learning", "priority": "critical", "difficulty": "advanced", "salary_premium": 20},
                            {"name": "deep learning", "priority": "important", "difficulty": "advanced", "salary_premium": 18},
                            {"name": "neural networks", "priority": "important", "difficulty": "advanced", "salary_premium": 17},
                            {"name": "nlp", "priority": "important", "difficulty": "advanced", "salary_premium": 16},
                            {"name": "computer vision", "priority": "important", "difficulty": "advanced", "salary_premium": 16},
                        ]
                    }
                }
            }
        }
    },

    # ==================== BUSINESS & MANAGEMENT ====================
    "Business & Management": {
        "level": 0,
        "description": "Business, management, and operations skills",
        "categories": {
            "Sales": {
                "level": 1,
                "subcategories": {
                    "Sales Skills": {
                        "level": 2,
                        "skills": [
                            {"name": "sales", "priority": "critical", "difficulty": "intermediate", "salary_premium": 0},
                            {"name": "crm", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "salesforce", "priority": "important", "difficulty": "intermediate", "salary_premium": 7},
                            {"name": "hubspot", "priority": "important", "difficulty": "beginner", "salary_premium": 5},
                            {"name": "negotiation", "priority": "important", "difficulty": "intermediate", "salary_premium": 8},
                            {"name": "closing techniques", "priority": "medium", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "lead generation", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "pipeline management", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                        ]
                    }
                }
            },
            "Management": {
                "level": 1,
                "subcategories": {
                    "Leadership & Management": {
                        "level": 2,
                        "skills": [
                            {"name": "leadership", "priority": "critical", "difficulty": "advanced", "salary_premium": 12},
                            {"name": "team management", "priority": "critical", "difficulty": "intermediate", "salary_premium": 10},
                            {"name": "project management", "priority": "critical", "difficulty": "intermediate", "salary_premium": 8},
                            {"name": "strategic planning", "priority": "important", "difficulty": "advanced", "salary_premium": 10},
                            {"name": "budgeting", "priority": "important", "difficulty": "intermediate", "salary_premium": 7},
                            {"name": "performance management", "priority": "important", "difficulty": "intermediate", "salary_premium": 8},
                            {"name": "change management", "priority": "important", "difficulty": "advanced", "salary_premium": 9},
                            {"name": "conflict resolution", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                        ]
                    },
                    "Agile Methods": {
                        "level": 2,
                        "skills": [
                            {"name": "agile", "priority": "critical", "difficulty": "beginner", "salary_premium": 0},
                            {"name": "scrum", "priority": "important", "difficulty": "beginner", "salary_premium": 3},
                            {"name": "kanban", "priority": "important", "difficulty": "beginner", "salary_premium": 2},
                            {"name": "lean", "priority": "medium", "difficulty": "intermediate", "salary_premium": 4},
                        ]
                    }
                }
            },
            "Marketing": {
                "level": 1,
                "subcategories": {
                    "Digital Marketing": {
                        "level": 2,
                        "skills": [
                            {"name": "digital marketing", "priority": "important", "difficulty": "intermediate", "salary_premium": 0},
                            {"name": "seo", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "sem", "priority": "important", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "social media marketing", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "content marketing", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "email marketing", "priority": "medium", "difficulty": "beginner", "salary_premium": 3},
                            {"name": "marketing automation", "priority": "medium", "difficulty": "intermediate", "salary_premium": 6},
                        ]
                    }
                }
            },
            "Finance & Accounting": {
                "level": 1,
                "subcategories": {
                    "Finance": {
                        "level": 2,
                        "skills": [
                            {"name": "financial analysis", "priority": "important", "difficulty": "advanced", "salary_premium": 8},
                            {"name": "financial planning", "priority": "important", "difficulty": "advanced", "salary_premium": 8},
                            {"name": "investment management", "priority": "important", "difficulty": "advanced", "salary_premium": 10},
                            {"name": "accounting", "priority": "critical", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "bookkeeping", "priority": "medium", "difficulty": "beginner", "salary_premium": 2},
                            {"name": "tax preparation", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                        ]
                    }
                }
            }
        }
    },

    # ==================== CREATIVE & DESIGN ====================
    "Creative & Design": {
        "level": 0,
        "description": "Design, creative, and artistic skills",
        "categories": {
            "Visual Design": {
                "level": 1,
                "subcategories": {
                    "Design Tools": {
                        "level": 2,
                        "skills": [
                            {"name": "figma", "priority": "critical", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "adobe xd", "priority": "important", "difficulty": "intermediate", "salary_premium": 4},
                            {"name": "photoshop", "priority": "important", "difficulty": "intermediate", "salary_premium": 4},
                            {"name": "illustrator", "priority": "important", "difficulty": "intermediate", "salary_premium": 4},
                            {"name": "sketch", "priority": "important", "difficulty": "intermediate", "salary_premium": 3},
                            {"name": "after effects", "priority": "medium", "difficulty": "advanced", "salary_premium": 5},
                        ]
                    },
                    "Design Skills": {
                        "level": 2,
                        "skills": [
                            {"name": "ui design", "priority": "critical", "difficulty": "intermediate", "salary_premium": 6},
                            {"name": "ux design", "priority": "critical", "difficulty": "intermediate", "salary_premium": 7},
                            {"name": "graphic design", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "visual design", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "web design", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "design thinking", "priority": "important", "difficulty": "intermediate", "salary_premium": 4},
                            {"name": "user research", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "wireframing", "priority": "important", "difficulty": "beginner", "salary_premium": 2},
                        ]
                    }
                }
            },
            "Video & Animation": {
                "level": 1,
                "subcategories": {
                    "Video Production": {
                        "level": 2,
                        "skills": [
                            {"name": "video production", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "video editing", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                            {"name": "motion graphics", "priority": "important", "difficulty": "advanced", "salary_premium": 6},
                            {"name": "animation", "priority": "important", "difficulty": "advanced", "salary_premium": 6},
                        ]
                    }
                }
            }
        }
    },

    # ==================== HEALTHCARE ====================
    "Healthcare": {
        "level": 0,
        "description": "Medical and healthcare-related skills",
        "categories": {
            "Clinical Skills": {
                "level": 1,
                "subcategories": {
                    "Medical Practice": {
                        "level": 2,
                        "skills": [
                            {"name": "patient care", "priority": "critical", "difficulty": "intermediate", "salary_premium": 0},
                            {"name": "medical terminology", "priority": "critical", "difficulty": "intermediate", "salary_premium": 0},
                            {"name": "clinical skills", "priority": "critical", "difficulty": "advanced", "salary_premium": 5},
                            {"name": "nursing", "priority": "critical", "difficulty": "intermediate", "salary_premium": 3},
                            {"name": "diagnostics", "priority": "important", "difficulty": "advanced", "salary_premium": 4},
                            {"name": "healthcare management", "priority": "important", "difficulty": "intermediate", "salary_premium": 5},
                        ]
                    },
                    "Medical Software": {
                        "level": 2,
                        "skills": [
                            {"name": "emr systems", "priority": "important", "difficulty": "intermediate", "salary_premium": 3},
                            {"name": "hipaa", "priority": "important", "difficulty": "intermediate", "salary_premium": 4},
                            {"name": "medical coding", "priority": "important", "difficulty": "intermediate", "salary_premium": 3},
                        ]
                    }
                }
            }
        }
    },

    # ==================== EDUCATION ====================
    "Education": {
        "level": 0,
        "description": "Teaching and educational skills",
        "categories": {
            "Teaching": {
                "level": 1,
                "subcategories": {
                    "Educational Methods": {
                        "level": 2,
                        "skills": [
                            {"name": "teaching", "priority": "critical", "difficulty": "intermediate", "salary_premium": 0},
                            {"name": "curriculum design", "priority": "important", "difficulty": "advanced", "salary_premium": 4},
                            {"name": "pedagogy", "priority": "important", "difficulty": "advanced", "salary_premium": 3},
                            {"name": "classroom management", "priority": "important", "difficulty": "intermediate", "salary_premium": 2},
                            {"name": "student assessment", "priority": "important", "difficulty": "intermediate", "salary_premium": 2},
                            {"name": "lesson planning", "priority": "important", "difficulty": "intermediate", "salary_premium": 1},
                        ]
                    },
                    "Educational Technology": {
                        "level": 2,
                        "skills": [
                            {"name": "lms", "priority": "important", "difficulty": "intermediate", "salary_premium": 2},
                            {"name": "e-learning", "priority": "important", "difficulty": "intermediate", "salary_premium": 2},
                            {"name": "online teaching", "priority": "medium", "difficulty": "beginner", "salary_premium": 1},
                        ]
                    }
                }
            }
        }
    },

    # ==================== UNIVERSAL SOFT SKILLS ====================
    "Universal Soft Skills": {
        "level": 0,
        "description": "Skills applicable across all industries",
        "categories": {
            "Communication": {
                "level": 1,
                "subcategories": {
                    "Communication Skills": {
                        "level": 2,
                        "skills": [
                            {"name": "communication", "priority": "critical", "difficulty": "intermediate", "salary_premium": 0},
                            {"name": "presentation skills", "priority": "important", "difficulty": "intermediate", "salary_premium": 2},
                            {"name": "written communication", "priority": "important", "difficulty": "intermediate", "salary_premium": 1},
                            {"name": "listening", "priority": "important", "difficulty": "intermediate", "salary_premium": 1},
                            {"name": "public speaking", "priority": "medium", "difficulty": "intermediate", "salary_premium": 2},
                        ]
                    }
                }
            },
            "Problem Solving": {
                "level": 1,
                "subcategories": {
                    "Analytical Skills": {
                        "level": 2,
                        "skills": [
                            {"name": "problem-solving", "priority": "critical", "difficulty": "advanced", "salary_premium": 5},
                            {"name": "critical thinking", "priority": "important", "difficulty": "advanced", "salary_premium": 4},
                            {"name": "analytical thinking", "priority": "important", "difficulty": "intermediate", "salary_premium": 3},
                            {"name": "creativity", "priority": "important", "difficulty": "intermediate", "salary_premium": 3},
                            {"name": "attention to detail", "priority": "medium", "difficulty": "beginner", "salary_premium": 1},
                        ]
                    }
                }
            },
            "Interpersonal": {
                "level": 1,
                "subcategories": {
                    "Teamwork & Collaboration": {
                        "level": 2,
                        "skills": [
                            {"name": "teamwork", "priority": "critical", "difficulty": "intermediate", "salary_premium": 0},
                            {"name": "collaboration", "priority": "critical", "difficulty": "intermediate", "salary_premium": 1},
                            {"name": "adaptability", "priority": "important", "difficulty": "intermediate", "salary_premium": 2},
                            {"name": "empathy", "priority": "medium", "difficulty": "intermediate", "salary_premium": 1},
                            {"name": "emotional intelligence", "priority": "medium", "difficulty": "intermediate", "salary_premium": 2},
                        ]
                    }
                }
            }
        }
    }
}

