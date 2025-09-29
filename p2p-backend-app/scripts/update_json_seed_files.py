#!/usr/bin/env python3
"""
Script to update JSON seed files with missing fields including challenges_and_solutions.

This script:
1. Reads existing JSON seed files
2. Adds missing challenges_and_solutions field if not present
3. Ensures subtitle field exists
4. Saves updated JSON files

Run from scripts directory:
    python update_json_seed_files.py
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any


def generate_subtitle_from_title(title: str) -> str:
    """Generate a subtitle from the title."""
    # Remove common prefixes
    subtitle = title.replace("Implementation of ", "")
    subtitle = subtitle.replace("Case Study: ", "")
    subtitle = subtitle.replace("Use Case: ", "")

    # Truncate if too long
    if len(subtitle) > 150:
        subtitle = subtitle[:147] + "..."

    # Add category prefix based on keywords
    if "ai" in title.lower() or "vision" in title.lower() or "ml" in title.lower():
        return f"AI/ML Solution: {subtitle}"
    elif "iot" in title.lower():
        return f"IoT Integration: {subtitle}"
    elif "automation" in title.lower() or "robot" in title.lower():
        return f"Automation Solution: {subtitle}"
    elif "quality" in title.lower():
        return f"Quality Enhancement: {subtitle}"
    elif "maintenance" in title.lower():
        return f"Maintenance Optimization: {subtitle}"
    elif "digital" in title.lower():
        return f"Digital Transformation: {subtitle}"
    else:
        return f"Manufacturing Innovation: {subtitle}"


def generate_challenges_for_usecase(usecase: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate appropriate challenges based on the use case category."""

    category = usecase.get("category", "").lower()
    title = usecase.get("title", "").lower()

    # Default challenges structure
    challenges = []

    # AI/Vision related challenges
    if "ai" in title or "vision" in title or "quality control" in category:
        challenges.append({
            "challenge": "Model Accuracy Requirements",
            "description": "Achieving the required detection accuracy while maintaining real-time processing speeds for production line integration",
            "solution": "Implemented extensive model training with augmented datasets and optimized inference pipeline using edge computing",
            "outcome": "Achieved 99%+ accuracy with sub-second processing time, meeting all production requirements"
        })
        challenges.append({
            "challenge": "Variable Environmental Conditions",
            "description": "Factory lighting variations and environmental factors affected vision system performance throughout different shifts",
            "solution": "Installed dedicated lighting systems and implemented adaptive algorithms that adjust to environmental changes",
            "outcome": "Consistent performance across all operating conditions with minimal false positives"
        })

    # IoT related challenges
    elif "iot" in title or "monitoring" in title:
        challenges.append({
            "challenge": "Legacy System Integration",
            "description": "Connecting IoT sensors to existing manufacturing equipment without disrupting ongoing operations",
            "solution": "Developed custom adapters and used non-invasive sensor installation methods with phased rollout approach",
            "outcome": "Successfully integrated with all targeted equipment with zero production downtime"
        })
        challenges.append({
            "challenge": "Data Volume Management",
            "description": "Handling large volumes of real-time sensor data without overwhelming network infrastructure",
            "solution": "Implemented edge processing with intelligent data filtering and compression algorithms",
            "outcome": "Reduced network load by 70% while maintaining data quality and real-time insights"
        })

    # Automation/Robotics challenges
    elif "robot" in title or "automation" in category or "amr" in title:
        challenges.append({
            "challenge": "Safety Compliance",
            "description": "Ensuring robotic systems meet all safety standards while operating alongside human workers",
            "solution": "Implemented comprehensive safety zones, sensors, and emergency stop systems with thorough testing protocols",
            "outcome": "Achieved full safety certification with zero incidents during implementation and operation"
        })
        challenges.append({
            "challenge": "Process Synchronization",
            "description": "Coordinating automated systems with existing manual processes and varying production speeds",
            "solution": "Developed adaptive control algorithms and buffer systems to handle variable production rates",
            "outcome": "Seamless integration with 95% efficiency improvement and flexible production capacity"
        })

    # Default challenges for other categories
    else:
        challenges.append({
            "challenge": "Change Management",
            "description": "Getting buy-in from operators and management for new technology implementation",
            "solution": "Conducted comprehensive training programs and demonstrated quick wins through pilot implementation",
            "outcome": "Full adoption achieved with positive feedback from all stakeholders"
        })
        challenges.append({
            "challenge": "ROI Justification",
            "description": "Demonstrating clear return on investment to secure project funding and support",
            "solution": "Developed detailed business case with phased implementation showing incremental benefits",
            "outcome": "Achieved projected ROI within first year, exceeding initial estimates by 20%"
        })

    return challenges


def update_usecase(usecase: Dict[str, Any]) -> Dict[str, Any]:
    """Update a single use case with missing fields."""

    # Add subtitle if missing
    if "subtitle" not in usecase or not usecase.get("subtitle"):
        usecase["subtitle"] = generate_subtitle_from_title(usecase.get("title", "Manufacturing Use Case"))

    # Add challenges_and_solutions if missing
    if "challenges_and_solutions" not in usecase:
        usecase["challenges_and_solutions"] = generate_challenges_for_usecase(usecase)

    # Ensure executive_summary exists
    if "executive_summary" not in usecase or not usecase.get("executive_summary"):
        # Use existing description or generate from title
        if "description" in usecase:
            usecase["executive_summary"] = usecase["description"][:500]
        else:
            usecase["executive_summary"] = f"This use case demonstrates the implementation of {usecase.get('title', 'innovative manufacturing solution')} " \
                                          f"at {usecase.get('factoryName', 'our manufacturing facility')}. " \
                                          f"The solution delivers significant operational improvements and ROI."

    return usecase


def update_json_file(filepath: Path) -> None:
    """Update a JSON seed file with missing fields."""

    print(f"\n📄 Processing: {filepath.name}")

    try:
        # Read existing JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            usecases = json.load(f)

        # Update each use case
        updated_count = 0
        for i, usecase in enumerate(usecases):
            original_keys = set(usecase.keys())
            updated_usecase = update_usecase(usecase)
            new_keys = set(updated_usecase.keys())

            if new_keys != original_keys:
                updated_count += 1
                added_fields = new_keys - original_keys
                print(f"   ✓ Use case {i+1}: Added fields: {', '.join(added_fields)}")

        # Save updated JSON with proper formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(usecases, f, indent=2, ensure_ascii=False)

        if updated_count > 0:
            print(f"   ✅ Updated {updated_count}/{len(usecases)} use cases")
        else:
            print(f"   ✓ All use cases already have required fields")

    except Exception as e:
        print(f"   ❌ Error processing file: {e}")


def main():
    """Main function to update all JSON seed files."""

    print("="*70)
    print("JSON SEED FILES UPDATE SCRIPT")
    print("="*70)

    # Get the usecases directory
    script_dir = Path(__file__).parent
    usecases_dir = script_dir / "usecases"

    if not usecases_dir.exists():
        print(f"❌ Usecases directory not found: {usecases_dir}")
        return 1

    # Find all JSON files
    json_files = list(usecases_dir.glob("*.json"))

    if not json_files:
        print(f"❌ No JSON files found in: {usecases_dir}")
        return 1

    print(f"\n📂 Found {len(json_files)} JSON seed files to process")

    # Update each file
    for json_file in json_files:
        update_json_file(json_file)

    print("\n" + "="*70)
    print("✅ JSON seed files update complete!")
    print("="*70)

    print("\n📋 Next steps:")
    print("1. Review the updated JSON files")
    print("2. Customize the generated challenges_and_solutions if needed")
    print("3. Run seed_usecases.py to update the database")

    return 0


if __name__ == "__main__":
    exit(main())