#!/usr/bin/env python3
"""
Script to update all JSON seed files with actual challenges from MD files.
"""

import json
import os

# Define the actual challenges extracted from MD files
CHALLENGES_MAP = {
    "amro_usecases.json": [
        {
            "title": "Assembly Workstation",
            "challenges": [
                {
                    "challenge": "Instruction Version Control",
                    "description": "Operators sometimes followed outdated paper SOPs during early transition.",
                    "solution": "Enforced 'single source of truth' with digital release workflow and QR access per station.",
                    "outcome": "100% adherence to latest instructions; paper eliminated."
                },
                {
                    "challenge": "Tool Communication Reliability",
                    "description": "Intermittent connectivity between smart torque tools and the workstation.",
                    "solution": "Hardened industrial Wi-Fi, local edge cache, and automatic retry logic.",
                    "outcome": "99.8% tool data capture rate; all critical fasteners tracked."
                }
            ]
        },
        {
            "title": "Demanufacturing Workstation",
            "challenges": [
                {
                    "challenge": "Damage During Teardown",
                    "description": "Early teardowns occasionally damaged connectors and flex cables.",
                    "solution": "Added tool-specific steps, torque/sequence guidance, and connector fixtures.",
                    "outcome": "Secondary damage incidents reduced by 85%."
                },
                {
                    "challenge": "Inconsistent Grading Criteria",
                    "description": "Different shifts graded parts differently.",
                    "solution": "Standardized A/B/C rubric with photos, auto-linked to test results.",
                    "outcome": "98% grading consistency across operators."
                }
            ]
        }
    ],
    "aadil_usecases.json": [
        {
            "title": "Robotic 3D Printer Farm for Drone Arm Production",
            "challenges": [
                {
                    "challenge": "Universal Gripper Design",
                    "description": "Designing a single robotic gripper that could reliably pick finished parts from different models of 3D printers and place them accurately on the conveyor without causing damage.",
                    "solution": "A custom, 3D-printed soft-jaw gripper with integrated pressure sensors was developed. The soft jaws prevent cosmetic damage, while the sensors confirm a successful grip before the robot moves.",
                    "outcome": "A single, universal gripper now services the entire farm, providing reliable, damage-free part handling."
                },
                {
                    "challenge": "Printer Status Integration",
                    "description": "Getting reliable 'print complete' signals from a mix of different 3D printer brands and models was challenging.",
                    "solution": "Instead of relying on native APIs, each printer was connected to a smart plug monitored by the Raspberry Pi. The Node-RED workflow monitors the power consumption of each printer; a significant drop in power indicates a finished print, triggering the robot.",
                    "outcome": "A universal and reliable method for detecting print completion across a heterogeneous fleet of printers."
                }
            ]
        },
        {
            "title": "Digital Simulation for Drone Production Line Optimization",
            "challenges": [
                {
                    "challenge": "Inaccurate Initial Data",
                    "description": "Gathering accurate cycle time and failure rate data from all equipment vendors proved difficult, as initial estimates were often overly optimistic.",
                    "solution": "We conducted workshops with each vendor to establish realistic performance ranges and used industry benchmark data as a starting point. The model was designed to easily update these parameters as real-world data became available.",
                    "outcome": "The final model had a high degree of fidelity, predicting actual throughput within 5% of the real-world results."
                },
                {
                    "challenge": "Scope Creep",
                    "description": "Stakeholders continuously requested adding more detail and secondary processes to the model, which threatened the project timeline.",
                    "solution": "A strict gating process was established by the Project Lead. All change requests had to be submitted with a clear business justification and were evaluated based on their impact on the project's primary objectives.",
                    "outcome": "The project remained focused on the most critical path, allowing it to be completed on time and within budget."
                }
            ]
        }
    ],
    "abdulrahman_usecases.json": [
        {
            "title": "Smart Factory OEE Revolution with Real-Time IoT Analytics",
            "challenges": [
                {
                    "challenge": "Legacy Machine Integration",
                    "description": "Connecting sensors to 30-year-old equipment without disrupting production or voiding warranties.",
                    "solution": "Developed non-invasive magnetic current sensors and optical encoders that attach externally without any machine modifications.",
                    "outcome": "Successfully integrated all legacy equipment with zero production downtime."
                },
                {
                    "challenge": "Data Accuracy Validation",
                    "description": "Initial sensor readings showed 15% variance from manual counts, creating trust issues with operators.",
                    "solution": "Implemented dual-sensor validation with machine learning algorithms to filter noise and detect anomalies.",
                    "outcome": "Achieved 99.7% accuracy in production counting, gaining full operator confidence."
                }
            ]
        },
        {
            "title": "AI-Driven Performance Command Center for Manufacturing Excellence",
            "challenges": [
                {
                    "challenge": "Information Overload",
                    "description": "Initial dashboards displayed too much data, overwhelming operators and managers.",
                    "solution": "Implemented role-based views with progressive disclosure - showing only critical KPIs first with drill-down capability.",
                    "outcome": "90% reduction in time to identify issues, with operators reporting improved focus."
                },
                {
                    "challenge": "Predictive Model Accuracy",
                    "description": "Early AI predictions had only 60% accuracy for equipment failures.",
                    "solution": "Collected 6 months of failure data and retrained models with domain-specific features including vibration patterns and temperature trends.",
                    "outcome": "Improved prediction accuracy to 92%, preventing 8 major breakdowns in first quarter."
                }
            ]
        }
    ],
    "firas_usecases.json": [
        {
            "title": "Real-Time Production Visibility Dashboard",
            "challenges": [
                {
                    "challenge": "Real-Time Data Latency",
                    "description": "Initial system had 30-second delays in data updates, missing critical production events.",
                    "solution": "Implemented edge computing with MQTT protocol for sub-second data transmission and local caching for network resilience.",
                    "outcome": "Achieved real-time updates with <500ms latency, capturing 100% of production events."
                },
                {
                    "challenge": "Cross-Shift Communication",
                    "description": "Important production issues were lost during shift changes, causing repeated problems.",
                    "solution": "Created digital shift handover module with mandatory acknowledgment and automated escalation for unresolved issues.",
                    "outcome": "Zero critical issues lost between shifts, 70% reduction in repeated problems."
                }
            ]
        },
        {
            "title": "Smart Energy Analytics for Sustainable Manufacturing",
            "challenges": [
                {
                    "challenge": "Granular Energy Attribution",
                    "description": "Couldn't determine which specific processes consumed the most energy within shared production lines.",
                    "solution": "Installed sub-meters at process level and developed ML algorithms to disaggregate shared consumption based on production patterns.",
                    "outcome": "Achieved 95% accuracy in energy attribution, identifying top 3 energy waste sources."
                },
                {
                    "challenge": "Behavioral Change Resistance",
                    "description": "Operators continued energy-wasteful practices despite having data showing inefficiencies.",
                    "solution": "Gamified energy savings with team competitions, real-time scoreboards, and monthly recognition programs.",
                    "outcome": "67% increase in operator-initiated energy saving actions, 12% overall energy reduction."
                }
            ]
        }
    ],
    "hamad_usecases.json": [
        {
            "title": "AI-Powered Quality Assurance Revolution",
            "challenges": [
                {
                    "challenge": "False Positive Rate",
                    "description": "Initial vision system flagged 30% good products as defective, causing unnecessary rework.",
                    "solution": "Implemented ensemble learning with multiple AI models voting on defects, plus continuous learning from operator feedback.",
                    "outcome": "Reduced false positive rate to 2%, saving 120 hours monthly in unnecessary inspections."
                },
                {
                    "challenge": "Multi-Surface Inspection",
                    "description": "Single camera couldn't detect defects on all surfaces of complex 3D parts.",
                    "solution": "Designed multi-angle camera array with synchronized capture and 3D reconstruction for complete surface coverage.",
                    "outcome": "100% surface inspection coverage, detecting previously missed underside defects."
                }
            ]
        },
        {
            "title": "Intelligent Safety Monitoring & Compliance System",
            "challenges": [
                {
                    "challenge": "Privacy Concerns",
                    "description": "Workers worried about constant video surveillance affecting their privacy and job security.",
                    "solution": "Implemented edge AI processing with no video storage - only safety events recorded, with transparent policies and worker council involvement.",
                    "outcome": "95% worker acceptance rate with union endorsement of the system."
                },
                {
                    "challenge": "Environmental False Alarms",
                    "description": "System triggered false safety alerts from shadows, reflections, and normal work movements.",
                    "solution": "Trained models on 6 months of annotated footage specific to our facility, including various lighting conditions and typical work patterns.",
                    "outcome": "Reduced false alarms by 94%, maintaining high sensitivity for real safety violations."
                }
            ]
        }
    ]
}

def update_json_file(filepath, file_key):
    """Update a JSON file with real challenges."""

    print(f"\n📄 Updating: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        challenges_data = CHALLENGES_MAP.get(file_key, [])

        # Update each use case in the JSON
        for use_case in data:
            # Find matching challenges by title
            for challenge_set in challenges_data:
                if challenge_set["title"].lower() in use_case["title"].lower():
                    use_case["challenges_and_solutions"] = challenge_set["challenges"]
                    print(f"   ✓ Updated challenges for: {use_case['title']}")
                    break

        # Save the updated JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"   ✅ Successfully updated {filepath}")

    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    """Update all JSON files with real challenges."""

    print("="*70)
    print("UPDATING ALL JSON FILES WITH REAL CHALLENGES FROM MD FILES")
    print("="*70)

    base_dir = "/mnt/c/Users/hamza/Documents/P2P-V2/p2p-backend-app/scripts/usecases"

    # Update each JSON file
    for filename in CHALLENGES_MAP.keys():
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            update_json_file(filepath, filename)
        else:
            print(f"⚠️  File not found: {filepath}")

    print("\n" + "="*70)
    print("✅ All JSON files updated with real challenges!")
    print("="*70)


if __name__ == "__main__":
    main()