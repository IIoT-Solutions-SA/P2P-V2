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
    "subtitle": "Revolutionizing Equipment Monitoring Through Industrial IoT and Machine Learning",
    "problem_statement": "An IoT-based predictive maintenance system, leveraging smart sensors and machine learning, reduced unplanned equipment downtime by 60% and cut maintenance costs by 1.8M annually at a major plastics manufacturer.",
    "solution_description": "Implementation of a comprehensive IoT-based predictive maintenance system using vibration analysis, thermal imaging, and machine learning to forecast equipment failures.",
    "category": "Predictive Maintenance",
    "factory_name": "Gulf Plastics Industries",
    "implementation_time": "4 months implementation",
    "roi_percentage": "180% ROI in first year",
    "region": "Dammam", "location": {"lat": 26.4207, "lng": 50.0888},
    "contact_person": "Sara Hassan", "contact_title": "Maintenance Supervisor",
    "images": [
        "https://images.unsplash.com/photo-1621905252507-b25492cc2692?w=800&h=400&fit=crop",
        "https://images.unsplash.com/photo-1555529393-399a3f9a721d?w=800&h=400&fit=crop",
        "https://images.unsplash.com/photo-1616443536831-a8493b8d4b2b?w=800&h=400&fit=crop",
        "https://images.unsplash.com/photo-1563216397-d62137538528?w=800&h=400&fit=crop"
    ],
    "executive_summary": "Gulf Plastics Industries faced critical equipment reliability challenges with 35% unplanned downtime, causing 2.8M annual losses in lost production and emergency repairs. The implementation of an IoT-based predictive maintenance system over 4 months achieved a 60% reduction in downtime, a 25% increase in Overall Equipment Effectiveness (OEE), and 1.8M in annual maintenance savings, delivering a 180% ROI in the first year. This case study details the technology selection, phased implementation, challenges overcome, and future roadmap.",
    "business_challenge": {
        "industry_context": "The plastics manufacturing industry operates with complex, high-temperature machinery like extruders and injection molding machines, which require continuous operation. Unplanned downtime directly impacts production targets and profitability.",
        "specific_problems": [
            "Unplanned downtime averaging 35% due to catastrophic equipment failures (e.g., bearings, motors).",
            "Reactive, 'run-to-failure' maintenance approach causing extended repair times and higher costs.",
            "Lack of visibility into real-time equipment health and performance trends.",
            "Excessive spending on emergency spare parts and overtime for maintenance crews.",
            "Inability to accurately forecast maintenance budgets and production capacity."
        ],
        "business_impact": {
            "financial_loss": "2.8M annually in lost production, emergency repairs, and expedited shipping of parts.",
            "customer_impact": "15% order delivery delays, damaging long-term customer relationships and brand trust.",
            "operational_impact": "Low equipment availability (OEE at 60%), inconsistent production schedules, and high stress on maintenance teams.",
            "compliance_risk": "Potential safety and environmental risks from unpredicted catastrophic failures."
        },
        "strategic_drivers": [
            "Mandate to improve Overall Equipment Effectiveness (OEE) by 20%.",
            "Need to reduce operational risk and improve workplace safety.",
            "Strategic shift from a reactive to a proactive, data-driven operational model.",
            "Desire to gain a competitive advantage through higher reliability and on-time delivery."
        ]
    },
    "solution_details": {
        "selection_criteria": [
            "Real-time anomaly detection with less than 5% false positives.",
            "Seamless integration with existing Computerized Maintenance Management System (CMMS).",
            "Proven scalability across 200+ critical assets of varying types.",
            "Actionable insights and clear dashboards for maintenance teams.",
            "Demonstrable ROI within 24 months."
        ],
        "vendor_evaluation": {
            "process": "3-month evaluation process including on-site Proof of Concept (PoC) on 10 critical extruders.",
            "vendors_considered": ["PredictiveSense Corp", "IoT Solutions SA", "AssetGuard Analytics"],
            "selected_vendor": "IoT Solutions SA",
            "selection_reasons": [
                "Superior anomaly detection accuracy in PoC (98.5% vs. 95% average).",
                "Strong local support team based in the Eastern Province, ensuring quick response times.",
                "Intuitive user interface that was highly rated by maintenance technicians during the PoC.",
                "Flexible and transparent pricing model.",
                "Excellent references from other heavy industrial clients in the region."
            ]
        },
        "technology_components": [
            {"component": "Sensor Network", "details": "200+ LoRaWAN-enabled vibration, acoustic, and temperature sensors. Thermal imaging cameras for critical switchgear."},
            {"component": "Data Platform", "details": "Cloud-based IoT platform (Azure IoT Hub) with custom-trained machine learning models (using Azure ML) for failure prediction."},
            {"component": "Edge Computing", "details": "Local gateways for data aggregation, filtering, and high-frequency analysis before cloud transmission."},
            {"component": "Integration Layer", "details": "Bi-directional API integration with the factory's SAP PM module for automated work order generation."}
        ]
    },
    "implementation_details": {
        "methodology": "Phased rollout using an Agile approach, starting with the most critical and failure-prone machinery.",
        "project_team": {
            "internal": [
                {"role": "Project Sponsor", "name": "Fahad Al-Qahtani", "title": "Plant Director"},
                {"role": "Project Lead", "name": "Sara Hassan", "title": "Maintenance Supervisor"}
            ],
            "vendor": [
                {"role": "Project Manager", "name": "David Miller", "title": "Senior Project Manager"},
                {"role": "Lead Data Scientist", "name": "Dr. Aisha Khan", "title": "IoT Analytics Specialist"}
            ]
        },
        "phases": [
            {"phase": "Phase 1: Critical Asset Pilot", "duration": "8 weeks", "objectives": ["Install sensors on 50 most critical machines", "Establish data pipeline and baseline performance", "Validate ML model accuracy"], "keyActivities": ["Sensor installation", "Data pipeline configuration", "Initial model training"], "budget": "175,000"},
            {"phase": "Phase 2: Full Factory Rollout & Integration", "duration": "8 weeks", "objectives": ["Deploy sensors to all remaining 150+ assets", "Integrate with CMMS for automated work orders", "Full user training"], "keyActivities": ["Mass sensor deployment", "CMMS API development", "User training workshops"], "budget": "275,000"}
        ],
        "total_budget": "450,000",
        "total_duration": "16 weeks"
    },
    "challenges_and_solutions": [
        {"challenge": "Network Connectivity", "description": "Poor cellular and Wi-Fi reception in dense, metallic areas of the factory floor.", "impact": "Intermittent data loss from sensors, compromising the reliability of the system.", "solution": "Deployed a private LoRaWAN network with dedicated gateways, providing robust, low-power, long-range coverage throughout the entire facility.", "outcome": "Achieved 99.9% data transmission reliability from all sensors."},
        {"challenge": "Alarm Fatigue", "description": "Initial ML models generated a high volume of false positive alerts, causing technicians to ignore notifications.", "impact": "Reduced trust in the system and risk of missing genuine alerts.", "solution": "Retrained machine learning models with more historical and labeled failure data. Implemented a tiered alerting system (e.g., 'Warning' vs. 'Critical').", "outcome": "Reduced false positives by 90% and increased technician confidence and response rates."},
        {"challenge": "Lack of Historical Data", "description": "The factory had limited historical sensor data tied to specific failure modes, making initial model training difficult.", "impact": "Delayed the development of accurate predictive models.", "solution": "Ran the system in 'learning mode' for 4 weeks to collect baseline data. Supplemented with physics-based models and simulated data before fine-tuning with real-world data.", "outcome": "Developed highly accurate models within the project timeline."},
        {"challenge": "Technician Buy-In", "description": "Experienced maintenance technicians were skeptical of the technology, viewing it as a threat or a 'black box' they couldn't trust.", "impact": "Slow adoption and resistance to data-driven work orders.", "solution": "Conducted hands-on workshops involving technicians in the sensor placement and alert validation process. Emphasized that the tool augments their skills, not replaces them.", "outcome": "Transformed technicians into system champions who provided valuable feedback for improvements."}
    ],
    "results": {
        "quantitative_metrics": [
            {"metric": "Unplanned Downtime", "baseline": "35%", "current": "14%", "improvement": "60% reduction"},
            {"metric": "Overall Equipment Effectiveness (OEE)", "baseline": "60%", "current": "75%", "improvement": "25% increase"},
            {"metric": "Maintenance Costs", "baseline": "2.8M losses", "current": "1.8M savings", "improvement": "Reduced reactive maintenance spend"},
            {"metric": "Mean Time To Repair (MTTR)", "baseline": "8 hours", "current": "2 hours", "improvement": "75% reduction"}
        ],
        "qualitative_impacts": [
            "Shift from a reactive 'firefighting' culture to a proactive, planned maintenance environment.",
            "Improved production planning and forecasting accuracy.",
            "Increased lifespan of critical equipment.",
            "Enhanced safety by preventing catastrophic failures."
        ],
        "roi_analysis": { "total_investment": "450,000", "annual_savings": "1,800,000", "payback_period": "3 months", "three_year_roi": "1,100%" }
    },
    "technical_architecture": {
        "system_overview": "A multi-tier IoT architecture featuring edge data pre-processing and a cloud-based analytics and machine learning platform, integrated with the on-premise CMMS.",
        "components": [
            {"layer": "Acquisition Layer", "components": ["LoRaWAN Vibration & Temperature Sensors", "Thermal Cameras", "Acoustic Sensors"], "specifications": "Banner Engineering sensors, FLIR thermal cameras, private LoRaWAN network."},
            {"layer": "Processing Layer", "components": ["Edge Gateways", "Cloud IoT Platform", "ML Engine"], "specifications": "Dell Edge Gateway 3000, Azure IoT Hub, Azure Machine Learning Studio."},
            {"layer": "Integration Layer", "components": ["CMMS Connector", "Messaging Queue"], "specifications": "Custom REST API for SAP PM, MQTT messaging protocol for data ingestion."},
            {"layer": "Monitoring Layer", "components": ["Technician Dashboard", "Management Analytics", "Alerting System"], "specifications": "Real-time dashboards in Grafana, BI reports in Power BI, SMS/email alerts via Azure Functions."}
        ],
        "security_measures": ["End-to-end encryption from sensor to cloud (AES-128)", "Network isolation for the IoT gateways", "Role-based access control (RBAC) on the cloud platform."],
        "scalability_design": ["Cloud-native serverless architecture for auto-scaling", "Containerized microservices for easy updates and deployment (Docker, Kubernetes)."]
    },
    "future_roadmap": [
        {"timeline": "Q3 2024", "initiative": "Integrate Spare Parts Inventory", "description": "Automatically trigger spare part orders in SAP based on failure predictions.", "expected_benefit": "Optimize inventory levels and eliminate stock-outs for critical parts."},
        {"timeline": "Q4 2024", "initiative": "Prescriptive Analytics", "description": "Upgrade ML models to not only predict a failure but also recommend the specific repair action needed.", "expected_benefit": "Reduce diagnostic time and improve first-time fix rate."},
        {"timeline": "Q2 2025", "initiative": "Energy Consumption Monitoring", "description": "Add power quality sensors to correlate energy usage with equipment health.", "expected_benefit": "Reduce energy costs and identify electrical issues."},
        {"timeline": "Q4 2025", "initiative": "Rollout to Sister Plant", "description": "Replicate the system and learnings at the Jeddah manufacturing facility.", "expected_benefit": "Standardize maintenance excellence across the enterprise."}
    ],
    "lessons_learned": [
        {"category": "Technical", "lesson": "Start with a Pilot on Critical Assets", "description": "Testing on a small set of the most important and problematic assets is essential to validate the technology, demonstrate value quickly, and refine the approach before a full-scale rollout.", "recommendation": "Select 10-15 assets for the pilot that are well-understood by the team and have a clear business impact."},
        {"category": "Organizational", "lesson": "Involve Maintenance Teams from Day One", "description": "Maintenance technicians possess invaluable tacit knowledge. Their buy-in and active participation are the most critical factors for success, as they are the ultimate end-users of the system.", "recommendation": "Form a joint project team with technicians. Involve them in sensor placement, alert configuration, and feedback sessions."},
        {"category": "Vendor Management", "lesson": "Prioritize Local Support and UX", "description": "While many vendors claimed high accuracy, the ability to get quick, on-site support and the user-friendliness of the system for technicians proved to be the most important differentiators.", "recommendation": "Weight local support and user experience as 40% of the vendor selection score."},
        {"category": "Integration", "lesson": "Budget for CMMS Integration Complexity", "description": "Integrating with an older, customized SAP PM system was more complex than anticipated. Standard connectors did not work out-of-the-box.", "recommendation": "Double the initial time and cost estimates for any integration with legacy enterprise systems."}
    ],
    "is_detailed_version": True,
    "published": True,
    "featured": True,
    "submitted_by": str(author2.id),
    "view_count": random.randint(4000, 12000),
    "like_count": random.randint(400, 1200),
    "bookmark_count": random.randint(80, 400),
    "published_date": "April 22, 2024",
    "last_updated": "April 28, 2024",
    "read_time": "15 min read",
    "views": random.randint(2000, 10000),
    "downloads": random.randint(100, 1000),
    "status": "verified",
    "verified_by": "Industrial IoT Council",
    "industry_tags": ["Plastics Manufacturing", "Heavy Industry", "Predictive Maintenance", "Industrial IoT"],
    "technology_tags": ["IoT Sensors", "Machine Learning", "Azure IoT", "LoRaWAN", "CMMS Integration"]
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
