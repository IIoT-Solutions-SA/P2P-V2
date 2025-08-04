import asyncio
import json
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager, get_db
from app.services.database_service import UserService, ForumService, UseCaseService
from app.models.mongo_models import User as MongoUser, ForumPost, UseCase, ForumReply
from app.models.pg_models import User as PGUser
from app.core.logging import setup_logging
from sqlalchemy import select, delete
import random

async def seed_data():
    """Seed development data from high-quality frontend use-cases.json"""
    logger = setup_logging()
    
    try:
        # Initialize database connections
        await db_manager.init_postgres()
        await db_manager.init_mongodb()
        logger.info("Database connections initialized for seeding")

        # Get PostgreSQL session
        db_session_gen = get_db()
        db = await anext(db_session_gen)

        logger.info("Starting data seeding with high-quality frontend data...")

        # --- Clean up ALL existing users to fix roles ---
        logger.info("🧹 Cleaning up existing users to fix roles...")
        try:
            # Clean up all users (both old test users and current demo users)
            all_user_emails = [
                "ahmed@example.com", "mariam@example.com", "youssef@example.com",  # Old test users
                "ahmed.faisal@advanced-electronics.com", "sara.hassan@advanced-electronics.com", "mohammed.rashid@gulf-plastics.com"  # Demo users
            ]
            
            for email in all_user_emails:
                try:
                    # Remove from MongoDB
                    old_mongo_user = await MongoUser.find_one(MongoUser.email == email)
                    if old_mongo_user:
                        await old_mongo_user.delete()
                        logger.info(f"Removed MongoDB user: {email}")
                    
                    # Remove from PostgreSQL
                    result = await db.execute(select(PGUser).where(PGUser.email == email))
                    old_pg_user = result.scalar_one_or_none()
                    if old_pg_user:
                        await db.execute(delete(PGUser).where(PGUser.email == email))
                        await db.commit()
                        logger.info(f"Removed PostgreSQL user: {email}")
                        
                except Exception as e:
                    logger.warning(f"Error removing user {email}: {e}")
                    
            logger.info("✅ User cleanup completed")
        except Exception as e:
            logger.warning(f"Error during user cleanup: {e}")

        # --- Seed Users (Demo Accounts from Frontend) ---
        test_users = [
            {
                "email": "ahmed.faisal@advanced-electronics.com", 
                "name": "Ahmed Al-Faisal", 
                "role": "admin",
                "company": "Advanced Electronics Co.",
                "title": "Organization Admin"
            },
            {
                "email": "sara.hassan@advanced-electronics.com", 
                "name": "Sara Hassan", 
                "role": "member",
                "company": "Advanced Electronics Co.", 
                "title": "Team Member"
            },
            {
                "email": "mohammed.rashid@gulf-plastics.com", 
                "name": "Mohammed Rashid", 
                "role": "admin",
                "company": "Gulf Plastics Industries",
                "title": "Organization Admin"
            }
        ]

        created_users = []
        for user_data in test_users:
            try:
                # Create in PostgreSQL with correct role
                pg_user = await UserService.create_user_pg(db, name=user_data["name"], email=user_data["email"], role=user_data.get("role", "user"))
                logger.info(f"Created PostgreSQL user: {user_data['name']} (role: {user_data.get('role', 'user')})")

                # Create in MongoDB with additional fields
                mongo_user = await UserService.create_user_mongo(
                    email=user_data["email"],
                    name=user_data["name"],
                    role=user_data.get("role", "user"),
                    industry_sector="Manufacturing",
                    location=user_data.get("company", "Saudi Arabia"),
                    expertise_tags=["4IR", "IoT", "Digital Transformation"]
                )
                created_users.append(mongo_user)
                logger.info(f"Created MongoDB user: {user_data['name']} (role: {user_data.get('role', 'user')})")

            except Exception as e:
                logger.warning(f"Error creating user {user_data['email']}: {e}")

        # --- Seed Use Cases from Frontend JSON ---
        json_path = os.path.join(os.path.dirname(__file__), '..', 'use-cases.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                use_cases_from_json = json.load(f)
            
            logger.info(f"Found {len(use_cases_from_json)} use cases in JSON file")
            
            for use_case_data in use_cases_from_json:
                try:
                    # Check if use case already exists
                    existing_case = await UseCase.find_one(UseCase.title == use_case_data["title"])
                    if not existing_case:
                        # Add a random user as submitter if users exist
                        if created_users:
                            use_case_data["submitted_by"] = str(random.choice(created_users).id)
                        
                        await UseCaseService.create_use_case(use_case_data)
                        logger.info(f"Created use case: {use_case_data['title']}")
                    else:
                        logger.info(f"Use case '{use_case_data['title']}' already exists")
                        
                except Exception as e:
                    logger.error(f"Error creating use case '{use_case_data.get('title', 'Unknown')}': {e}")

            # --- Create 2 Detailed Enterprise Use Cases ---
            # First, let's store references to create detailed_version_id links
            detailed_use_case_titles = {
                "AI Quality Inspection System": "AI Quality Inspection System Reduces Defects by 85%",
                "Predictive Maintenance IoT System": "Predictive Maintenance IoT System Prevents 60% Downtime"
            }
            
            detailed_use_cases = [ 
                {
                # Basic Information
                "submitted_by": str(random.choice(created_users).id) if created_users else "system-seed",
                "title": "AI Quality Inspection System Reduces Defects by 85%",
                "problem_statement": "Computer vision system reduces defects by 85% in electronics manufacturing. Our factory implemented an advanced AI-powered quality inspection system that uses machine learning algorithms to detect microscopic defects in PCB manufacturing, resulting in significant improvements in product quality and customer satisfaction.",
                "solution_description": "Implementation of an AI-powered computer vision quality inspection system with machine learning algorithms for microscopic defect detection",
                "region": "Riyadh",
                "location": {"lat": 24.7136, "lng": 46.6753},
                "industry_tags": ["Quality Control", "Electronics", "AI/ML"],
                "published": True,
                "featured": True,
                
                # Detailed Information
                "subtitle": "Transforming PCB Manufacturing Through Computer Vision and Machine Learning",
                "description_long": "Advanced Electronics Co. faced critical quality control challenges with a 15% defect rate in PCB manufacturing, resulting in significant annual losses and declining customer satisfaction. The implementation of an AI-powered computer vision quality inspection system achieved remarkable results through systematic deployment and optimization.",
                "category": "Quality Control", 
                "factory_name": "Advanced Electronics Co.",
                "implementation_time": "6 months implementation",
                "roi_percentage": "250% ROI in first year",
                
                # Contact & Metadata
                "contact_person": "Ahmed Al-Faisal",
                "contact_title": "Organization Admin",
                "images": [
                    "https://images.unsplash.com/photo-1565043666747-69f6646db940?w=800&h=400&fit=crop",
                    "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=400&fit=crop",
                    "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=400&fit=crop"
                ],
                
                # Executive Summary
                "executive_summary": "Advanced Electronics Co. faced critical quality control challenges with a 15% defect rate in PCB manufacturing, resulting in SAR 450K annual losses and declining customer satisfaction. The implementation of an AI-powered computer vision quality inspection system achieved an 85% reduction in defects, SAR 2.3M in annual cost savings, and 250% ROI in the first year. This case study details the 6-month implementation journey, technical architecture, challenges overcome, and lessons learned.",
                
                # Business Challenge & Context
                "business_challenge": {
                    "industry_context": "The electronics manufacturing industry faces increasing pressure for zero-defect production due to complex PCB designs, miniaturization trends, and stringent quality requirements from automotive and aerospace sectors.",
                    "specific_problems": [
                        "Manual inspection inconsistency across shifts with 15% defect rate",
                        "Microscopic defects undetectable by human inspectors causing field failures",
                        "Production bottlenecks with 40% inspection time overhead",
                        "High customer return rates (12%) damaging brand reputation",
                        "Inability to meet ISO 9001 and automotive IATF 16949 standards"
                    ],
                    "business_impact": {
                        "financial_loss": "SAR 450K annually in waste, rework, and returns",
                        "customer_impact": "12% return rate, declining satisfaction scores",
                        "operational_impact": "40% slower production, inconsistent quality",
                        "compliance_risk": "Risk of losing automotive certification"
                    },
                    "strategic_drivers": [
                        "Pressure from automotive clients for zero-defect delivery",
                        "Need to scale production while maintaining quality",
                        "Regulatory compliance requirements",
                        "Competitive advantage through quality leadership"
                    ]
                },
                
                # Solution Details
                "solution_details": {
                    "selection_criteria": [
                        "Real-time processing capability (>50 units/minute)",
                        "99%+ accuracy for defect detection",
                        "Integration with existing production line",
                        "Scalability across multiple product lines",
                        "ROI achievement within 18 months"
                    ],
                    "vendor_evaluation": {
                        "process": "6-month vendor evaluation process including PoC testing",
                        "vendors_considered": ["VisionTech Systems", "InspectAI Solutions", "QualityVision Pro"],
                        "selected_vendor": "VisionTech Systems",
                        "selection_reasons": [
                            "Superior accuracy in PoC testing (99.7% vs 97.2% average)",
                            "Proven experience in electronics manufacturing",
                            "Comprehensive support and training program",
                            "Flexible licensing model",
                            "Strong reference customers"
                        ]
                    },
                    "technology_components": [
                        {
                            "component": "Hardware Platform",
                            "details": "4x 4K industrial cameras with specialized LED lighting systems and conveyor integration"
                        },
                        {
                            "component": "AI/ML Engine", 
                            "details": "Custom-trained convolutional neural networks using TensorFlow framework with 50,000+ labeled images"
                        },
                        {
                            "component": "Edge Computing",
                            "details": "NVIDIA Jetson AGX Xavier units for real-time processing with <100ms latency"
                        },
                        {
                            "component": "Integration Layer",
                            "details": "RESTful APIs connecting to existing MES and ERP systems for seamless data flow"
                        }
                    ]
                },
                
                # Implementation Details
                "implementation_details": {
                    "methodology": "Agile implementation with weekly sprints and continuous stakeholder feedback",
                    "total_budget": "SAR 285,000",
                    "total_duration": "26 weeks",
                    "project_team": {
                        "internal": [
                            {"role": "Project Sponsor", "name": "Sarah Al-Mahmoud", "title": "Plant Manager"},
                            {"role": "Technical Lead", "name": "Ahmed Al-Faisal", "title": "Operations Manager"},
                            {"role": "Quality Lead", "name": "Mohammed Rashid", "title": "QC Supervisor"},
                            {"role": "IT Integration", "name": "Fatima Hassan", "title": "IT Manager"}
                        ],
                        "vendor": [
                            {"role": "Implementation Manager", "name": "Dr. James Chen", "title": "Senior Solutions Architect"},
                            {"role": "ML Engineer", "name": "Lisa Wang", "title": "AI Specialist"},
                            {"role": "Support Engineer", "name": "Mike Rodriguez", "title": "Technical Support"}
                        ]
                    },
                    "phases": [
                        {
                            "phase": "Phase 1: Discovery & Planning",
                            "duration": "4 weeks",
                            "objectives": ["Current state analysis", "Requirements definition", "Technical architecture design"],
                            "budget": "45,000",
                            "resources": "2 internal + 1 vendor team member"
                        },
                        {
                            "phase": "Phase 2: System Development & Training",
                            "duration": "12 weeks", 
                            "objectives": ["AI model development", "Hardware installation", "System integration"],
                            "budget": "180,000",
                            "resources": "4 internal + 3 vendor team members"
                        },
                        {
                            "phase": "Phase 3: Testing & Validation",
                            "duration": "6 weeks",
                            "objectives": ["System validation", "Performance tuning", "User training"],
                            "budget": "35,000",
                            "resources": "6 internal + 2 vendor team members"
                        },
                        {
                            "phase": "Phase 4: Production Deployment",
                            "duration": "4 weeks",
                            "objectives": ["Full production deployment", "Knowledge transfer", "Support handover"],
                            "budget": "25,000",
                            "resources": "3 internal + 1 vendor team member"
                        }
                    ]
                },
                
                # Challenges & Solutions (Complete from UseCaseDetail.tsx)
                "challenges_and_solutions": [
                    {
                        "challenge": "Data Quality and Labeling",
                        "description": "Initial AI model accuracy was only 89% due to insufficient and poorly labeled training data",
                        "impact": "Delayed timeline by 3 weeks and threatened project success",
                        "solution": "Implemented systematic data collection process with expert labelers and expanded training dataset to 50,000+ images",
                        "outcome": "Achieved 99.7% accuracy and established ongoing data collection process"
                    },
                    {
                        "challenge": "Operator Resistance",
                        "description": "Production operators feared job displacement and were reluctant to adopt the new system",
                        "impact": "Slow adoption and initial resistance to using system outputs",
                        "solution": "Comprehensive change management including training, job role evolution, and involvement in system improvement",
                        "outcome": "High operator engagement and advocacy for system expansion"
                    },
                    {
                        "challenge": "Integration Complexity",
                        "description": "Legacy MES system had limited API capabilities requiring custom integration development",
                        "impact": "Additional development time and complexity in data flow",
                        "solution": "Developed custom middleware with robust error handling and manual fallback procedures",
                        "outcome": "Seamless integration with 99.9% uptime and automatic failover"
                    },
                    {
                        "challenge": "Lighting Variability",
                        "description": "Inconsistent lighting conditions throughout the day affected system accuracy",
                        "impact": "Accuracy dropped to 94% during certain times of day",
                        "solution": "Installed specialized LED lighting system with automated calibration and compensation algorithms",
                        "outcome": "Consistent 99.7% accuracy across all lighting conditions"
                    }
                ],
                
                # Results (Complete from UseCaseDetail.tsx)
                "results": {
                    "quantitative_metrics": [
                        {
                            "metric": "Defect Rate Reduction",
                            "baseline": "15.0%",
                            "current": "2.25%", 
                            "improvement": "85% reduction",
                            "measurement_method": "Monthly quality audits over 12 months"
                        },
                        {
                            "metric": "Customer Returns",
                            "baseline": "12.0%",
                            "current": "2.1%",
                            "improvement": "82.5% reduction",
                            "measurement_method": "Customer return tracking and analysis"
                        },
                        {
                            "metric": "Inspection Speed",
                            "baseline": "20 units/minute",
                            "current": "50 units/minute",
                            "improvement": "150% increase",
                            "measurement_method": "Production line throughput measurement"
                        },
                        {
                            "metric": "Annual Cost Savings",
                            "baseline": "SAR 450K losses",
                            "current": "SAR 2.3M savings",
                            "improvement": "SAR 2.75M swing",
                            "measurement_method": "Financial analysis of waste, rework, and returns"
                        }
                    ],
                    "qualitative_impacts": [
                        "Improved customer satisfaction scores from 7.2 to 9.1",
                        "Enhanced employee confidence in quality processes",
                        "Faster response to quality issues and root cause analysis",
                        "Improved competitive positioning in automotive sector",
                        "Foundation for digital transformation initiatives"
                    ],
                    "roi_analysis": {
                        "total_investment": "SAR 285,000",
                        "annual_savings": "SAR 2,300,000",
                        "payback_period": "1.5 months",
                        "three_year_roi": "2,315%",
                        "npv_calculation": "SAR 6.2M (3-year NPV at 8% discount rate)"
                    }
                },
                
                # Technical Architecture (Complete from UseCaseDetail.tsx)
                "technical_architecture": {
                    "system_overview": "Multi-tier architecture with edge computing for real-time processing and cloud connectivity for monitoring and updates",
                    "components": [
                        {
                            "layer": "Acquisition Layer",
                            "components": ["4K Industrial Cameras", "LED Lighting Systems", "Conveyor Sensors"],
                            "specifications": "Allied Vision Mako cameras, 3000K/5000K LED arrays, photoelectric sensors"
                        },
                        {
                            "layer": "Processing Layer",
                            "components": ["Edge Computing Units", "AI/ML Engine", "Image Processing"],
                            "specifications": "NVIDIA Jetson AGX Xavier, TensorFlow 2.8, OpenCV 4.5"
                        },
                        {
                            "layer": "Integration Layer",
                            "components": ["MES Connector", "ERP Integration", "Quality Database"],
                            "specifications": "RESTful APIs, PostgreSQL database, MQTT messaging"
                        },
                        {
                            "layer": "Monitoring Layer",
                            "components": ["Dashboard", "Analytics", "Alerting"],
                            "specifications": "Real-time web dashboard, Grafana analytics, email/SMS alerts"
                        }
                    ],
                    "security_measures": [
                        "Network segmentation with dedicated VLAN",
                        "Encrypted data transmission using TLS 1.3",
                        "Role-based access control and authentication",
                        "Regular security updates and vulnerability assessments"
                    ],
                    "scalability_design": [
                        "Modular architecture supporting additional production lines",
                        "Cloud-based model training and deployment pipeline",
                        "Containerized deployment using Docker",
                        "Horizontal scaling capability for increased throughput"
                    ]
                },
                
                # Future Roadmap (Complete from UseCaseDetail.tsx)
                "future_roadmap": [
                    {
                        "timeline": "Q2 2024",
                        "initiative": "Expansion to Assembly Line",
                        "description": "Deploy system to final assembly inspection with component placement verification",
                        "expected_benefit": "Additional 30% quality improvement"
                    },
                    {
                        "timeline": "Q3 2024",
                        "initiative": "Predictive Quality Analytics", 
                        "description": "Implement predictive models to forecast quality trends and prevent issues",
                        "expected_benefit": "Proactive quality management"
                    },
                    {
                        "timeline": "Q4 2024",
                        "initiative": "Multi-Site Deployment",
                        "description": "Roll out to 3 additional manufacturing facilities",
                        "expected_benefit": "Enterprise-wide quality standardization"
                    },
                    {
                        "timeline": "Q1 2025",
                        "initiative": "Supplier Network Integration",
                        "description": "Share quality insights with key suppliers for upstream improvement",
                        "expected_benefit": "Supply chain quality enhancement"
                    }
                ],
                
                # Lessons Learned (Complete from UseCaseDetail.tsx)
                "lessons_learned": [
                    {
                        "category": "Technical",
                        "lesson": "Data Quality is Foundation",
                        "description": "Invest heavily in high-quality, diverse training data from the beginning. Poor data quality will undermine even the best algorithms.",
                        "recommendation": "Allocate 30-40% of project time to data collection and labeling"
                    },
                    {
                        "category": "Organizational",
                        "lesson": "Change Management is Critical",
                        "description": "Technical success requires organizational adoption. Early engagement and clear communication about role evolution prevents resistance.",
                        "recommendation": "Include change management specialist in project team from day one"
                    },
                    {
                        "category": "Vendor Management",
                        "lesson": "Proof of Concept is Essential",
                        "description": "Real-world testing with actual production data revealed significant differences between vendor claims and reality.",
                        "recommendation": "Insist on comprehensive PoC with your actual production data"
                    },
                    {
                        "category": "Integration",
                        "lesson": "Legacy System Complexity",
                        "description": "Integration with legacy systems always takes longer than expected. Plan for custom development.",
                        "recommendation": "Add 50% buffer to integration timeline and budget"
                    }
                ],
                
                # Additional Metadata
                "published_date": "March 15, 2024",
                "last_updated": "March 20, 2024",
                "read_time": "18 min read",
                "views": 2847,
                "downloads": 342,
                "status": "verified",
                "verified_by": "Dr. Khalid Al-Rashid, Manufacturing Excellence Institute",
                "technology_tags": ["Computer Vision", "TensorFlow", "Edge Computing", "Industrial IoT"],
                
                # Enhanced impact metrics for basic compatibility
                "impact_metrics": {
                    "benefits": "85% reduction in defects; SAR 2.3M annual cost savings; 40% faster inspection process",
                    "defect_reduction": "85%",
                    "cost_savings": "SAR 2.3M annually",
                    "processing_speed": "150% faster"
                }
            },
            {
                # Second detailed use case - Predictive Maintenance
                "submitted_by": str(random.choice(created_users).id) if created_users else "system-seed",
                "title": "Predictive Maintenance IoT System Prevents 60% Downtime",
                "problem_statement": "Smart sensors prevent equipment failures and reduce downtime significantly through advanced predictive analytics and real-time monitoring of critical manufacturing equipment.",
                "solution_description": "Comprehensive IoT-based predictive maintenance system using vibration analysis, thermal imaging, and machine learning for proactive equipment maintenance",
                "region": "Dammam",
                "location": {"lat": 26.4207, "lng": 50.0888},
                "industry_tags": ["Predictive Maintenance", "IoT", "Manufacturing"],
                "published": True,
                "featured": True,
                
                # Detailed Information
                "subtitle": "Revolutionary Equipment Monitoring Through Industrial IoT and Machine Learning",
                "category": "Predictive Maintenance",
                "factory_name": "Gulf Plastics Industries",
                "implementation_time": "4 months implementation", 
                "roi_percentage": "180% ROI in first year",
                
                # Contact & Metadata
                "contact_person": "Mohammed Rashid",
                "contact_title": "Organization Admin",
                "images": [
                    "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=400&fit=crop",
                    "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=400&fit=crop"
                ],
                
                # Executive Summary
                "executive_summary": "Gulf Plastics Industries faced critical equipment reliability challenges with 35% unplanned downtime affecting production schedules and causing SAR 2.8M annual losses. The implementation of a comprehensive IoT-based predictive maintenance system achieved 60% reduction in unplanned downtime, SAR 1.8M in annual maintenance cost savings, and 25% increase in overall equipment effectiveness (OEE). This case study details the 4-month implementation journey, sensor deployment strategy, challenges overcome, and measurable business outcomes.",
                
                # Business Challenge & Context
                "business_challenge": {
                    "industry_context": "The plastics manufacturing industry operates with complex, high-temperature machinery requiring continuous operation. Equipment failures can result in production line shutdowns, material waste, and significant financial losses due to missed delivery commitments.",
                    "specific_problems": [
                        "Unplanned downtime averaging 35% due to equipment failures",
                        "Reactive maintenance approach causing extended repair times",
                        "Lack of visibility into equipment health and performance trends",
                        "High maintenance costs due to emergency repairs and overtime",
                        "Production schedule disruptions affecting customer deliveries"
                    ],
                    "business_impact": {
                        "financial_loss": "SAR 2.8M annually in downtime and emergency repairs",
                        "customer_impact": "15% delivery delays damaging customer relationships",
                        "operational_impact": "35% equipment availability, inconsistent production",
                        "compliance_risk": "Safety incidents due to unexpected equipment failures"
                    },
                    "strategic_drivers": [
                        "Need for predictable maintenance schedules",
                        "Pressure to improve overall equipment effectiveness",
                        "Regulatory requirements for equipment safety monitoring",
                        "Competitive advantage through operational excellence"
                    ]
                },
                
                # Enhanced impact metrics for basic compatibility
                "impact_metrics": {
                    "benefits": "60% downtime reduction; SAR 1.8M maintenance savings; 25% productivity increase",
                    "downtime_reduction": "60%",
                    "cost_savings": "SAR 1.8M annually",
                    "productivity_increase": "25%"
                },
                
                # Additional Metadata
                "published_date": "February 10, 2024",
                "read_time": "15 min read",
                "views": 1924,
                "downloads": 287,
                "status": "verified",
                "verified_by": "Saudi Industrial IoT Consortium",
                "technology_tags": ["Industrial IoT", "Machine Learning", "Vibration Analysis", "Thermal Imaging"]
            }
            ]
            
            # Store detailed use case IDs for linking
            detailed_case_ids = {}
            
            for detailed_case in detailed_use_cases:
                try:
                    existing_detailed = await UseCase.find_one(UseCase.title == detailed_case["title"])
                    if not existing_detailed:
                        created_detailed = await UseCaseService.create_use_case(detailed_case)
                        detailed_case_ids[detailed_case["title"]] = str(created_detailed.id)
                        logger.info(f"Created detailed use case: {detailed_case['title']}")
                    else:
                        detailed_case_ids[detailed_case["title"]] = str(existing_detailed.id)
                        logger.info(f"Detailed use case '{detailed_case['title']}' already exists")
                except Exception as e:
                    logger.error(f"Error creating detailed use case '{detailed_case.get('title', 'Unknown')}': {e}")

            # --- Update Basic Use Cases with Detailed Version Links ---
            for basic_title, detailed_title in detailed_use_case_titles.items():
                if detailed_title in detailed_case_ids:
                    try:
                        basic_case = await UseCase.find_one(UseCase.title == basic_title)
                        if basic_case:
                            # Add detailed version reference to basic use case
                            basic_case.detailed_version_id = detailed_case_ids[detailed_title]
                            basic_case.has_detailed_view = True
                            await basic_case.save()
                            logger.info(f"Linked basic use case '{basic_title}' to detailed version")
                            
                            # Add basic version reference to detailed use case
                            detailed_case = await UseCase.find_one(UseCase.title == detailed_title)
                            if detailed_case:
                                detailed_case.basic_version_id = str(basic_case.id)
                                detailed_case.is_detailed_version = True
                                await detailed_case.save()
                                logger.info(f"Linked detailed use case '{detailed_title}' to basic version")
                    except Exception as e:
                        logger.error(f"Error linking use cases '{basic_title}' <-> '{detailed_title}': {e}")

        except FileNotFoundError:
            logger.error(f"❌ Could not find use-cases.json at {json_path}")
            logger.info("📋 Creating basic use cases instead...")
            
            # Fallback to basic use cases if JSON file not found
            basic_use_cases = [
                {
                    "title": "Smart Manufacturing Implementation",
                    "problem_statement": "Manual production processes causing inefficiencies",
                    "solution_description": "IoT-enabled automated production line",
                    "region": "Riyadh",
                    "location": {"lat": 24.7136, "lng": 46.6753},
                    "industry_tags": ["manufacturing", "automation"],
                    "published": True
                }
            ]
            
            for basic_case in basic_use_cases:
                if created_users:
                    basic_case["submitted_by"] = str(random.choice(created_users).id)
                await UseCaseService.create_use_case(basic_case)
                logger.info(f"Created basic use case: {basic_case['title']}")

        # --- Clean up existing forum posts first ---
        logger.info("🧹 Cleaning up existing forum posts...")
        try:
            # Delete all existing forum posts and replies to start fresh
            await ForumPost.delete_all()
            await ForumReply.delete_all()
            logger.info("✅ Cleaned up existing forum posts and replies")
        except Exception as e:
            logger.warning(f"Error cleaning up forum posts: {e}")

        # --- Create Comprehensive Forum Posts from Frontend ---
        if created_users:
            # Define specific forum authors (using demo user names for consistency)
            forum_authors = {
                "Sarah Ahmed": {"title": "Production Engineer - Jeddah", "user": None},
                "Mohammed Al-Shahri": {"title": "Operations Manager - Riyadh", "user": None},
                "Fatima Al-Otaibi": {"title": "Factory Owner - Dammam", "user": None},
                "Khalid Al-Ghamdi": {"title": "Quality Engineer - Mecca", "user": None},
                "Mohammed Al-Rashid": {"title": "IoT Specialist - Riyadh", "user": None},
                "Fatima Hassan": {"title": "Quality Manager - Dammam", "user": None},
                "Ahmed Al-Zahrani": {"title": "Factory Owner - Mecca", "user": None}
            }
            
            # Map forum authors to actual demo users (best match)
            for author_name in forum_authors.keys():
                # Find best matching user or use random
                matching_user = None
                for user in created_users:
                    if "Ahmed" in author_name and "Ahmed" in user.name:
                        matching_user = user
                        break
                    elif "Mohammed" in author_name and "Mohammed" in user.name:
                        matching_user = user
                        break
                    elif "Sara" in user.name and "Sarah" in author_name:
                        matching_user = user
                        break
                
                forum_authors[author_name]["user"] = matching_user or random.choice(created_users)

            # Forum posts data from Forum.tsx
            forum_posts_data = [
                {
                    "title": "How to improve production line efficiency using sensors?",
                    "author": "Sarah Ahmed",
                    "category": "Automation",
                    "content": """We're currently operating a medium-scale electronics manufacturing facility and facing several challenges in real-time monitoring of our production lines.

**Current Challenges:**
- Manual quality checks causing delays
- Difficulty tracking production metrics in real-time
- Limited visibility into equipment performance
- High rate of undetected defects reaching final inspection

**What We're Looking For:**
- Sensor recommendations for real-time monitoring
- Integration with existing equipment
- Cost-effective solutions suitable for SMEs
- Success stories from similar implementations

Has anyone successfully implemented IoT sensors in their production lines? What were the key considerations and ROI achieved?""",
                    "tags": ["automation", "sensors", "iot", "quality-control", "sme"],
                    "is_pinned": True,
                    "has_best_answer": False,
                    "views": 234,
                    "likes": 8,
                    "comments": [
                        {
                            "author": "Mohammed Al-Rashid",
                            "content": "We implemented a similar solution last year using industrial-grade sensors from Siemens. The key is to start small with critical points in your production line. We started with temperature and vibration sensors on our most critical machines and expanded from there. ROI was visible within 6 months.",
                            "likes": 5,
                            "replies": [
                                {
                                    "author": "Sarah Ahmed",
                                    "content": "Thanks for sharing! What was the approximate cost per sensor? And did you face any integration challenges with legacy equipment?",
                                    "likes": 2
                                },
                                {
                                    "author": "Mohammed Al-Rashid", 
                                    "content": "Sensors ranged from SAR 500-2000 depending on type. For legacy equipment, we used edge computing devices as intermediaries. Happy to share more details if you DM me.",
                                    "likes": 3
                                }
                            ]
                        },
                        {
                            "author": "Fatima Hassan",
                            "content": "Consider starting with vision-based quality inspection systems. We use cameras with AI models to detect defects. Much more cost-effective than traditional sensors for quality control. Local company TechVision SA provides excellent solutions.",
                            "likes": 4,
                            "replies": []
                        },
                        {
                            "author": "Ahmed Al-Zahrani",
                            "content": "Before investing in sensors, ensure your team is ready for the digital transformation. We made the mistake of implementing too quickly without proper training. Now we have a phased approach: 1) Team training, 2) Pilot project, 3) Full implementation.",
                            "likes": 8,
                            "replies": []
                        }
                    ]
                },
                {
                    "title": "My experience implementing predictive maintenance in a plastic factory",
                    "author": "Mohammed Al-Shahri",
                    "category": "Maintenance",
                    "content": """Sharing my experience implementing a predictive maintenance system and how it saved 30% of maintenance costs.

**Background:**
Our plastic manufacturing facility was experiencing frequent unplanned downtime due to equipment failures. Traditional reactive maintenance was costing us significantly.

**Implementation Journey:**
1. **Assessment Phase** - Identified critical equipment and failure patterns
2. **Sensor Installation** - Deployed vibration, temperature, and acoustic sensors
3. **Data Analytics** - Implemented machine learning models for predictive analysis
4. **Team Training** - Trained maintenance staff on new protocols

**Results After 18 Months:**
- 30% reduction in maintenance costs
- 45% decrease in unplanned downtime
- 25% increase in equipment lifespan
- Significant improvement in production planning

**Key Lessons:**
- Start with your most critical equipment
- Invest in proper training
- Choose sensors wisely based on failure modes
- Integration with existing systems is crucial

Happy to answer any questions about our implementation!""",
                    "tags": ["predictive-maintenance", "plastic-manufacturing", "cost-reduction", "ml"],
                    "is_pinned": False,
                    "has_best_answer": True,
                    "views": 456,
                    "likes": 15,
                    "comments": []
                },
                {
                    "title": "Best smart inventory management systems for small factories?",
                    "author": "Fatima Al-Otaibi",
                    "category": "Quality Management",
                    "content": """Looking for a suitable inventory management system for a small factory that produces electrical equipment.

**Current Situation:**
- Manual tracking causing inventory discrepancies
- Difficulty forecasting raw material needs
- Excess inventory tying up capital
- Occasional stockouts affecting production

**Requirements:**
- Cost-effective for small operations (50-100 employees)
- Easy integration with existing ERP
- Real-time inventory tracking
- Demand forecasting capabilities
- Mobile accessibility for warehouse staff

**Budget Range:** SAR 50,000 - 150,000 for initial setup

Has anyone implemented similar systems? What were your experiences with different vendors?""",
                    "tags": ["inventory-management", "small-factory", "electrical-equipment", "erp"],
                    "is_pinned": False,
                    "has_best_answer": False,
                    "views": 189,
                    "likes": 6,
                    "comments": []
                },
                {
                    "title": "Challenges of implementing AI in quality inspection",
                    "author": "Khalid Al-Ghamdi",
                    "category": "Artificial Intelligence",
                    "content": """We're facing difficulties in training AI models to inspect product defects in our manufacturing process.

**Our Setup:**
- Electronics component manufacturing
- High-resolution cameras for visual inspection
- Various defect types: scratches, discoloration, dimensional issues

**Current Challenges:**
1. **Data Quality:** Insufficient labeled data for training
2. **Model Accuracy:** Current model only achieves 85% accuracy
3. **False Positives:** Too many good products flagged as defective
4. **Integration:** Difficulty integrating with production line speed
5. **Maintenance:** Model performance degrades over time

**Technical Stack:**
- TensorFlow for model training
- OpenCV for image processing
- Industrial cameras with specialized lighting

**Questions:**
- How did you collect and label training data effectively?
- What accuracy levels are considered acceptable in production?
- How do you handle model drift and retraining?
- Any recommendations for local AI consultants in Saudi Arabia?

Looking forward to your insights and experiences!""",
                    "tags": ["artificial-intelligence", "quality-inspection", "computer-vision", "tensorflow"],
                    "is_pinned": False,
                    "has_best_answer": True,
                    "views": 678,
                    "likes": 19,
                    "comments": []
                }
            ]

            # Create forum posts with comments and replies
            created_posts = []
            for post_data in forum_posts_data:
                try:
                    # Create main post
                    author_user = forum_authors[post_data["author"]]["user"]
                    post = await ForumService.create_post(
                        author_id=str(author_user.id),
                        title=post_data["title"],
                        content=post_data["content"],
                        category=post_data["category"],
                        tags=post_data["tags"]
                    )
                    
                    # Update post with additional metadata (views, likes, etc.)
                    post.views = post_data.get("views", 0)
                    post.upvotes = post_data.get("likes", 0)
                    post.is_pinned = post_data.get("is_pinned", False)
                    post.has_best_answer = post_data.get("has_best_answer", False)
                    await post.save()
                    
                    created_posts.append(post)
                    logger.info(f"Created forum post: {post.title}")
                    
                    # Create comments for this post
                    for comment_data in post_data.get("comments", []):
                        try:
                            comment_author_user = forum_authors[comment_data["author"]]["user"]
                            comment = await ForumService.create_reply(
                                post_id=str(post.id),
                                author_id=str(comment_author_user.id),
                                content=comment_data["content"],
                                is_best_answer=comment_data.get("is_best_answer", False)
                            )
                            
                            # Update comment upvotes
                            comment.upvotes = comment_data.get("likes", 0)
                            await comment.save()
                            
                            logger.info(f"Created comment by {comment_data['author']} on '{post.title}'")
                            
                            # Create nested replies
                            for reply_data in comment_data.get("replies", []):
                                try:
                                    reply_author_user = forum_authors[reply_data["author"]]["user"]
                                    reply = await ForumService.create_reply(
                                        post_id=str(post.id),
                                        author_id=str(reply_author_user.id),
                                        content=reply_data["content"]
                                    )
                                    
                                    # Update reply upvotes
                                    reply.upvotes = reply_data.get("likes", 0)
                                    await reply.save()
                                    
                                    logger.info(f"Created reply by {reply_data['author']} to comment on '{post.title}'")
                                    
                                except Exception as e:
                                    logger.error(f"Error creating reply by {reply_data.get('author', 'Unknown')}: {e}")
                                    
                        except Exception as e:
                            logger.error(f"Error creating comment by {comment_data.get('author', 'Unknown')}: {e}")
                            
                except Exception as e:
                    logger.error(f"Error creating forum post '{post_data.get('title', 'Unknown')}': {e}")

            logger.info(f"✅ Created {len(created_posts)} forum posts with comprehensive comments and replies")

        logger.info("✅ Seed data created successfully!")
        use_cases_count = len(use_cases_from_json) if 'use_cases_from_json' in locals() else 0
        detailed_count = 2  # We always create 2 detailed use cases
        linked_count = len([title for title in detailed_use_case_titles.keys() if title in [uc.get('title', '') for uc in use_cases_from_json]]) if 'use_cases_from_json' in locals() else 0
        forum_posts_count = len(created_posts) if 'created_posts' in locals() else 0
        logger.info(f"📊 Summary: {len(test_users)} users, {use_cases_count} basic use cases, {detailed_count} detailed use cases, {linked_count} linked pairs, {forum_posts_count} forum posts with replies")
        logger.info("🔗 Linked use cases: Basic ↔ Detailed versions with detailed_version_id references")

    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        raise
    finally:
        # Clean up database connections
        await db_manager.close_connections()
        logger.info("Database connections closed")

if __name__ == "__main__":
    print("🌱 Starting database seeding with high-quality frontend data...")
    asyncio.run(seed_data())
    print("🎉 Database seeding completed!")