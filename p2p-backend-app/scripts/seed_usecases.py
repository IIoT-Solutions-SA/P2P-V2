import asyncio
import sys
import os
import json
import random
import re

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.services.database_service import UseCaseService
from app.models.mongo_models import UseCase, User as MongoUser
from app.core.logging import setup_logging

def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.
    Example: "AI Quality Inspection System" -> "ai-quality-inspection-system"
    """
    if not text:
        return ""
    text = text.lower()
    # Remove parentheses
    text = re.sub(r'[\(\)]', '', text)
    # Replace spaces and non-word chars with a hyphen
    text = re.sub(r'[\s\W_]+', '-', text)
    text = text.strip('-')
    return text

async def seed_usecases():
    """Wipes and seeds only the use case data, assuming users already exist."""
    logger = setup_logging()
    
    try:
        await db_manager.init_mongodb()

        logger.info("👥 Fetching existing users from the database...")
        existing_users = await MongoUser.find_all().to_list()
        if not existing_users:
            logger.error("❌ No users found. Please run the `seed_db_users.py` script first.")
            return
        logger.info(f"👍 Found {len(existing_users)} users.")

        logger.info("🧹 Wiping all existing use case data...")
        await UseCase.delete_all()
        logger.info("✅ Use case cleanup complete.")
        
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'use-cases.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                use_cases_from_json = json.load(f)
            logger.info(f"Found {len(use_cases_from_json)} use cases. Seeding from JSON...")

            company_to_user_map = {user.company: user for user in existing_users}

            for case_json in use_cases_from_json:
                submitter = company_to_user_map.get(case_json.get("factoryName"), random.choice(existing_users))
                
                title = case_json.get("title")
                db_case = {
                    "title": title,
                    "title_slug": slugify(title), # Generate and add the slug
                    "company_slug": slugify(case_json.get("factoryName")),
                    "problem_statement": case_json.get("description"),
                    "solution_description": case_json.get("description"),
                    "factory_name": case_json.get("factoryName"),
                    "region": case_json.get("city"),
                    "location": {"lat": case_json.get("latitude"), "lng": case_json.get("longitude")},
                    "category": case_json.get("category"),
                    "implementation_time": case_json.get("implementationTime"),
                    "impact_metrics": {"benefits": "; ".join(case_json.get("benefits", []))},
                    "submitted_by": str(submitter.id),
                    "published": True,
                    "view_count": random.randint(500, 7500),
                    "like_count": random.randint(50, 500),
                    "bookmark_count": random.randint(10, 100)
                }
                await UseCaseService.create_use_case(db_case)
            logger.info("✅ All 15 basic use cases seeded from JSON with slugs.")

        except FileNotFoundError:
            logger.error(f"❌ CRITICAL: Could not find {json_path}. No basic use cases were seeded.")

        logger.info("🌱 Seeding 2 detailed enterprise use cases with FULL data and slugs...")
        author1 = next((user for user in existing_users if "Advanced Electronics Co." in user.company), existing_users[0])
        author2 = next((user for user in existing_users if "Gulf Plastics Industries" in user.company), existing_users[1])

        detailed_use_cases_data = [
    # --- AI Quality Inspection System (Full Details) ---
    {
    "title": "AI Quality Inspection System (Detailed View)",
    "subtitle": "Transforming PCB Manufacturing Through Computer Vision and Machine Learning",
    "problem_statement": "Computer vision system reduces defects by 85% in electronics manufacturing. Our factory implemented an advanced AI-powered quality inspection system that uses machine learning algorithms to detect microscopic defects in PCB manufacturing, resulting in significant improvements in product quality and customer satisfaction.",
    "solution_description": "Implementation of an AI-powered computer vision quality inspection system with machine learning algorithms for microscopic defect detection",
    "category": "Quality Control",
    "factory_name": "Advanced Electronics Co.",
    "implementation_time": "6 months implementation",
    "roi_percentage": "250% ROI in first year",
    "region": "Riyadh", "location": {"lat": 24.7136, "lng": 46.6753},
    "contact_person": "Ahmed Al-Faisal", "contact_title": "Operations Manager",
    "images": [
        "https://images.unsplash.com/photo-1565043666747-69f6646db940?w=800&h=400&fit=crop",
        "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=400&fit=crop",
        "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=400&fit=crop",
        "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=800&h=400&fit=crop"
    ],
    "executive_summary": "Advanced Electronics Co. faced critical quality control challenges with a 15% defect rate in PCB manufacturing, resulting in 450K annual losses and declining customer satisfaction. The implementation of an AI-powered computer vision quality inspection system achieved an 85% reduction in defects, 2.3M in annual cost savings, and 250% ROI in the first year. This case study details the 6-month implementation journey, technical architecture, challenges overcome, and lessons learned.",
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
            "financial_loss": "450K annually in waste, rework, and returns",
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
            {"component": "Hardware Platform", "details": "4x 4K industrial cameras with specialized LED lighting systems and conveyor integration"},
            {"component": "AI/ML Engine", "details": "Custom-trained convolutional neural networks using TensorFlow framework with 50,000+ labeled images"},
            {"component": "Edge Computing", "details": "NVIDIA Jetson AGX Xavier units for real-time processing with <100ms latency"},
            {"component": "Integration Layer", "details": "RESTful APIs connecting to existing MES and ERP systems for seamless data flow"}
        ]
    },
    "implementation_details": {
        "methodology": "Agile implementation with weekly sprints and continuous stakeholder feedback",
        "project_team": {
            "internal": [
                {"role": "Project Sponsor", "name": "Sarah Al-Mahmoud", "title": "Plant Manager"},
                {"role": "Technical Lead", "name": "Ahmed Al-Faisal", "title": "Operations Manager"},
            ],
            "vendor": [
                {"role": "Implementation Manager", "name": "Dr. James Chen", "title": "Senior Solutions Architect"},
                {"role": "ML Engineer", "name": "Lisa Wang", "title": "AI Specialist"},
            ]
        },
        "phases": [
            {"phase": "Phase 1: Discovery & Planning", "duration": "4 weeks", "objectives": ["Current state analysis", "Requirements definition", "Technical architecture design"], "keyActivities": ["Production line analysis", "Stakeholder interviews"], "budget": "45,000"},
            {"phase": "Phase 2: System Development & Training", "duration": "12 weeks", "objectives": ["AI model development", "Hardware installation", "System integration"], "keyActivities": ["Collection and labeling of 50,000+ training images", "AI model development"], "budget": "180,000"},
            {"phase": "Phase 3: Testing & Validation", "duration": "6 weeks", "objectives": ["System validation", "Performance tuning", "User training"], "keyActivities": ["Parallel testing with manual inspection", "Accuracy validation"], "budget": "35,000"},
            {"phase": "Phase 4: Production Deployment", "duration": "4 weeks", "objectives": ["Full production deployment", "Knowledge transfer", "Support handover"], "keyActivities": ["Phased rollout to full production", "Performance monitoring"], "budget": "25,000"}
        ],
        "total_budget": "285,000",
        "total_duration": "26 weeks"
    },
    "challenges_and_solutions": [
        {"challenge": "Data Quality and Labeling", "description": "Initial AI model accuracy was only 89% due to insufficient and poorly labeled training data", "impact": "Delayed timeline by 3 weeks and threatened project success", "solution": "Implemented systematic data collection process with expert labelers and expanded training dataset to 50,000+ images", "outcome": "Achieved 99.7% accuracy and established ongoing data collection process"},
        {"challenge": "Operator Resistance", "description": "Production operators feared job displacement and were reluctant to adopt the new system", "impact": "Slow adoption and initial resistance to using system outputs", "solution": "Comprehensive change management including training, job role evolution, and involvement in system improvement", "outcome": "High operator engagement and advocacy for system expansion"},
        {"challenge": "Integration Complexity", "description": "Legacy MES system had limited API capabilities requiring custom integration development", "impact": "Additional development time and complexity in data flow", "solution": "Developed custom middleware with robust error handling and manual fallback procedures", "outcome": "Seamless integration with 99.9% uptime and automatic failover"},
        {"challenge": "Lighting Variability", "description": "Inconsistent lighting conditions throughout the day affected system accuracy", "impact": "Accuracy dropped to 94% during certain times of day", "solution": "Installed specialized LED lighting system with automated calibration and compensation algorithms", "outcome": "Consistent 99.7% accuracy across all lighting conditions"},
        {"challenge": "Data Security", "description": "Sensitive production data was exposed during initial deployment", "impact": "Potential intellectual property theft and regulatory compliance issues", "solution": "Implemented strict data access controls and encryption protocols", "outcome": "Secure production environment with no data breaches"},
        {"challenge": "Scalability Concerns", "description": "Initial system performance was not scalable for future production expansion", "impact": "Limited ability to handle increased production volumes", "solution": "Designed modular architecture with cloud-based components", "outcome": "Scalable system capable of handling 10x production capacity"},
        {"challenge": "User Adoption", "description": "Initial training sessions were not effective in achieving full system adoption", "impact": "Partial system usage and reduced efficiency", "solution": "Developed interactive training modules with gamification elements", "outcome": "High user engagement and 95% system adoption"}
    ],
    "results": {
        "quantitative_metrics": [
            {"metric": "Defect Rate Reduction", "baseline": "15.0%", "current": "2.25%", "improvement": "85% reduction"},
            {"metric": "Customer Returns", "baseline": "12.0%", "current": "2.1%", "improvement": "82.5% reduction"},
            {"metric": "Inspection Speed", "baseline": "20 units/minute", "current": "50 units/minute", "improvement": "150% increase"},
            {"metric": "Annual Cost Savings", "baseline": "450K losses", "current": "2.3M savings", "improvement": "2.75M swing"}
        ],
        "qualitative_impacts": [
            "Improved customer satisfaction scores from 7.2 to 9.1",
            "Enhanced employee confidence in quality processes",
            "Foundation for digital transformation initiatives"
        ],
        "roi_analysis": { "total_investment": "285,000", "annual_savings": "2,300,000", "payback_period": "1.5 months", "three_year_roi": "2,315%" }
    },
    "technical_architecture": {
        "system_overview": "Multi-tier architecture with edge computing for real-time processing and cloud connectivity for monitoring and updates",
        "components": [
            {"layer": "Acquisition Layer", "components": ["4K Industrial Cameras", "LED Lighting Systems"], "specifications": "Allied Vision Mako cameras, 3000K/5000K LED arrays"},
            {"layer": "Processing Layer", "components": ["Edge Computing Units", "AI/ML Engine"], "specifications": "NVIDIA Jetson AGX Xavier, TensorFlow 2.8, OpenCV 4.5"},
            {"layer": "Integration Layer", "components": ["MES Connector", "ERP Integration"], "specifications": "RESTful APIs, PostgreSQL database, MQTT messaging"},
            {"layer": "Monitoring Layer", "components": ["Dashboard", "Analytics", "Alerting"], "specifications": "Real-time web dashboard, Grafana analytics, email/SMS alerts"}
        ],
        "security_measures": ["Network segmentation with dedicated VLAN", "Encrypted data transmission using TLS 1.3"],
        "scalability_design": ["Modular architecture supporting additional production lines", "Containerized deployment using Docker"]
    },
    "future_roadmap": [
        {"timeline": "Q2 2024", "initiative": "Expansion to Assembly Line", "description": "Deploy system to final assembly inspection.", "expected_benefit": "Additional 30% quality improvement"},
        {"timeline": "Q3 2024", "initiative": "Predictive Quality Analytics", "description": "Implement predictive models to forecast quality trends.", "expected_benefit": "Proactive quality management"},
        {"timeline": "Q4 2024", "initiative": "Multi-Site Deployment", "description": "Roll out to 3 additional manufacturing facilities", "expected_benefit": "Enterprise-wide quality standardization"},
        {"timeline": "Q1 2025", "initiative": "Supplier Network Integration", "description": "Share quality insights with key suppliers for upstream improvement", "expected_benefit": "Supply chain quality enhancement"}
    ],
    "lessons_learned": [
        {"category": "Technical", "lesson": "Data Quality is Foundation", "description": "Invest heavily in high-quality, diverse training data from the beginning.", "recommendation": "Allocate 30-40% of project time to data collection and labeling"},
        {"category": "Organizational", "lesson": "Change Management is Critical", "description": "Technical success requires organizational adoption.", "recommendation": "Include change management specialist in project team from day one"},
        {"category": "Vendor Management", "lesson": "Proof of Concept is Essential", "description": "Real-world testing with actual production data revealed significant differences between vendor claims and reality.", "recommendation": "Insist on comprehensive PoC with your actual production data"},
        {"category": "Integration", "lesson": "Legacy System Complexity", "description": "Integration with legacy systems always takes longer than expected. Plan for custom development.", "recommendation": "Add 50% buffer to integration timeline and budget"}
    ],
    "is_detailed_version": True, "published": True, "featured": True, "submitted_by": str(author1.id),
    "view_count": random.randint(5000, 15000), "like_count": random.randint(500, 1500), "bookmark_count": random.randint(100, 500),
    "published_date": "March 15, 2024",
    "last_updated": "March 20, 2024",
    "read_time": "18 min read",
    "views": random.randint(2000, 10000),
    "downloads": random.randint(100, 1000),
    "status": "verified",   
    "verified_by": "Dr. Khalid Al-Rashid, Manufacturing Excellence Institute",
    "industry_tags": ["Electronics", "PCB Manufacturing", "Quality Control", "AI/ML"],
    "technology_tags": ["Computer Vision", "TensorFlow", "Edge Computing", "Industrial IoT"]
},
    # --- Predictive Maintenance System (Full Details) ---
    {
        "title": "Predictive Maintenance IoT System (Detailed View)",
        "subtitle": "Revolutionary Equipment Monitoring Through Industrial IoT and Machine Learning",
        "problem_statement": "Smart sensors prevent equipment failures and reduce downtime significantly.",
        "solution_description": "Comprehensive IoT-based predictive maintenance system using vibration analysis, thermal imaging, and machine learning.",
        "category": "Predictive Maintenance",
        "factory_name": "Gulf Plastics Industries",
        "implementation_time": "4 months implementation",
        "roi_percentage": "180% ROI in first year",
        "region": "Dammam", "location": {"lat": 26.4207, "lng": 50.0888},
        "contact_person": "Sara Hassan", "contact_title": "Team Member",
        "images": [
            "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=400&fit=crop",
            "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=400&fit=crop"
        ],
        "executive_summary": "Gulf Plastics Industries faced critical equipment reliability challenges with 35% unplanned downtime, causing 2.8M annual losses. The implementation of an IoT-based predictive maintenance system achieved a 60% reduction in downtime and a 25% increase in OEE.",
        "business_challenge": {
            "industry_context": "The plastics manufacturing industry operates with complex, high-temperature machinery requiring continuous operation.",
            "specific_problems": [
                "Unplanned downtime averaging 35% due to equipment failures",
                "Reactive maintenance approach causing extended repair times",
                "Lack of visibility into equipment health and performance trends"
            ],
            "business_impact": {
                "financial_loss": "2.8M annually in downtime and emergency repairs",
                "customer_impact": "15% delivery delays damaging customer relationships",
                "operational_impact": "35% equipment availability, inconsistent production"
            }
        },
        "solution_details": {
            "selection_criteria": ["Real-time anomaly detection", "Integration with CMMS", "Scalability across 200+ assets"],
            "vendor_evaluation": {
                "process": "3-month evaluation with on-site PoC",
                "selected_vendor": "IoT Solutions SA",
                "selection_reasons": ["Superior anomaly detection accuracy", "Strong local support team"]
            },
            "technology_components": [
                {"component": "Sensor Network", "details": "200+ LoRaWAN vibration and temperature sensors"},
                {"component": "Data Platform", "details": "Cloud-based IoT platform with custom machine learning models"}
            ]
        },
        "implementation_details": {
            "methodology": "Phased rollout, starting with most critical machinery",
            "total_budget": "450,000",
            "total_duration": "16 weeks",
            "phases": [
                {"phase": "Phase 1: Critical Asset Monitoring", "duration": "8 weeks", "objectives": ["Install sensors on 50 critical machines", "Establish data pipeline"]},
                {"phase": "Phase 2: Full Factory Rollout", "duration": "8 weeks", "objectives": ["Deploy sensors to all remaining assets", "Integrate with CMMS"]}
            ]
        },
        "challenges_and_solutions": [
            {"challenge": "Network Connectivity", "description": "Poor cellular reception in some parts of the factory.", "solution": "Deployed a private LoRaWAN network for reliable sensor communication."},
            {"challenge": "Alarm Fatigue", "description": "Initial models generated too many false positive alerts.", "solution": "Retrained machine learning models with more historical data to improve accuracy."}
        ],
        "results": {
            "quantitative_metrics": [
                {"metric": "Downtime Reduction", "baseline": "35%", "current": "14%", "improvement": "60% reduction"},
                {"metric": "Maintenance Savings", "baseline": "N/A", "current": "1.8M annually", "improvement": "Significant savings"}
            ],
            "qualitative_impacts": ["Improved production planning", "Increased equipment lifespan", "Proactive maintenance scheduling"],
            "roi_analysis": { "total_investment": "450,000", "annual_savings": "1,800,000", "payback_period": "3 months"}
        },
        "lessons_learned": [
            {"category": "Technical", "lesson": "Start with a Pilot", "description": "Testing on a small set of critical assets first is essential to validate the technology and approach."},
            {"category": "Organizational", "lesson": "Involve Maintenance Teams Early", "description": "Maintenance technicians have invaluable knowledge and their buy-in is critical for success."}
        ],
        "is_detailed_version": True, "published": True, "featured": True, "submitted_by": str(author2.id),
        "view_count": random.randint(4000, 12000), "like_count": random.randint(400, 1200), "bookmark_count": random.randint(80, 400)
    }
]
        
        # Add slugs to detailed cases before creating them
        for detailed_case in detailed_use_cases_data:
            detailed_case["title_slug"] = slugify(detailed_case["title"])
        
        detailed_case_ids = {}
        for detailed_case_data in detailed_use_cases_data:
            created_detailed = await UseCaseService.create_use_case(detailed_case_data)
            detailed_case_ids[detailed_case_data["title"]] = str(created_detailed.id)
        logger.info("✅ Detailed use cases seeded with full data and slugs.")

        logger.info("🔗 Linking basic and detailed use cases...")
        detailed_use_case_titles = { 
            "AI Quality Inspection System": "AI Quality Inspection System (Detailed View)", 
            "Predictive Maintenance IoT System": "Predictive Maintenance IoT System (Detailed View)" 
        }
        
        linked_count = 0
        for basic_title, detailed_title in detailed_use_case_titles.items():
            basic_case = await UseCase.find_one(UseCase.title == basic_title)
            if basic_case and detailed_title in detailed_case_ids:
                basic_case.detailed_version_id = detailed_case_ids[detailed_title]
                basic_case.has_detailed_view = True
                await basic_case.save()
                
                detailed_case = await UseCase.get(detailed_case_ids[detailed_title])
                if detailed_case:
                    detailed_case.basic_version_id = str(basic_case.id)
                    await detailed_case.save()
                
                linked_count += 1
        logger.info(f"✅ Linked {linked_count} pairs of use cases.")

    except Exception as e:
        logger.error(f"❌ Use case seeding script failed: {e}")
        raise
    finally:
        await db_manager.close_connections()
        logger.info("Database connections closed.")

if __name__ == "__main__":
    print("🌱 Starting use case seeding script...")
    asyncio.run(seed_usecases())
    print("🎉 Use case seeding completed!")
