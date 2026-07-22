"""Add the five canonical simplified answers to existing use cases and seed JSON.

This migration is intentionally non-destructive: IDs, media, interactions, legacy rich
sections, ownership, publication state, and routing slugs remain unchanged.

Usage:
  python scripts/migrate_usecases_to_simplified_fields.py          # preview
  python scripts/migrate_usecases_to_simplified_fields.py --apply  # update MongoDB and seed JSON
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.database import db_manager  # noqa: E402
from app.models.mongo_models import UseCase  # noqa: E402


def text(value: Any) -> str:
    return str(value or "").strip()


def unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        value = text(value)
        if value and value.lower() not in {item.lower() for item in result}:
            result.append(value)
    return result


def sentence(value: str) -> str:
    value = text(value)
    if not value:
        return ""
    return value if value[-1] in ".!?" else f"{value}."


def derive_simplified(source: dict[str, Any]) -> dict[str, str]:
    challenge = source.get("business_challenge") or source.get("businessChallenge") or {}
    solution = source.get("solution_details") or source.get("solutionDetails") or {}
    implementation = source.get("implementation_details") or source.get("implementationDetails") or {}
    results = source.get("results") or {}

    problem = text(source.get("problem"))
    if not problem:
        problems = unique([text(item) for item in challenge.get("specific_problems", challenge.get("specificProblems", []))])
        context = text(challenge.get("industry_context", challenge.get("industryContext")))
        problem = " ".join(sentence(item) for item in problems)
        if not problem:
            problem = context or text(source.get("problem_statement")) or text(source.get("description")) or text(source.get("executive_summary"))

    technology = text(source.get("technology"))
    if not technology:
        components: list[str] = []
        for item in solution.get("technology_components", solution.get("technologyComponents", [])) or []:
            if isinstance(item, str):
                components.append(item)
            elif isinstance(item, dict):
                name = text(item.get("component"))
                details = text(item.get("details"))
                components.append(": ".join(part for part in (name, details) if part))
        technology = "\n".join(unique(components))
        if not technology:
            technology = text(implementation.get("methodology")) or text(source.get("solution_description")) or text(source.get("subtitle"))

    budget = text(source.get("budget")) or text(implementation.get("total_budget", implementation.get("totalBudget"))) or text(source.get("cost_estimate")) or "Not disclosed"

    outcomes = text(source.get("outcomes"))
    if not outcomes:
        outcome_lines = unique([text(item) for item in results.get("qualitative_impacts", results.get("qualitativeImpacts", [])) or []])
        for metric in results.get("quantitative_metrics", results.get("quantitativeMetrics", [])) or []:
            if not isinstance(metric, dict):
                continue
            name = text(metric.get("metric"))
            improvement = text(metric.get("improvement"))
            baseline = text(metric.get("baseline"))
            current = text(metric.get("current"))
            line = ": ".join(part for part in (name, improvement or current) if part)
            if baseline and current:
                line += f" (from {baseline} to {current})"
            if line:
                outcome_lines.append(sentence(line))
        roi = results.get("roi_analysis", results.get("roiAnalysis", {})) or {}
        annual_savings = text(roi.get("annual_savings", roi.get("annualSavings")))
        if annual_savings:
            outcome_lines.append(sentence(f"Estimated annual savings: {annual_savings}"))
        outcomes = "\n".join(unique(outcome_lines)) or text(source.get("executive_summary")) or text(source.get("impact_metrics", {}).get("benefits"))

    challenges = text(source.get("challenges"))
    if not challenges:
        entries = source.get("challenges_and_solutions", source.get("challengesSolutions", [])) or []
        challenge_lines: list[str] = []
        for item in entries:
            if not isinstance(item, dict):
                continue
            parts = unique([
                sentence(text(item.get("challenge"))),
                sentence(text(item.get("description"))),
                sentence(f"Response: {text(item.get('solution'))}") if text(item.get("solution")) else "",
                sentence(f"Outcome: {text(item.get('outcome'))}") if text(item.get("outcome")) else "",
            ])
            if parts:
                challenge_lines.append(" ".join(parts))
        challenges = "\n\n".join(challenge_lines)

    return {
        "problem": problem[:5000],
        "technology": technology[:5000],
        "budget": budget[:120],
        "outcomes": outcomes[:5000],
        "challenges": challenges[:2000],
    }


def seed_files() -> list[Path]:
    candidates = [ROOT / "use-cases.json", *sorted((ROOT / "scripts" / "usecases").glob("*_usecases.json"))]
    return [path for path in candidates if path.exists()]


def update_seed_file(path: Path, apply: bool) -> tuple[int, int]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, list):
        return 0, 0
    changed = 0
    for item in payload:
        if not isinstance(item, dict):
            continue
        derived = derive_simplified(item)
        if any(item.get(key) != value for key, value in derived.items()):
            item.update(derived)
            changed += 1
    if apply and changed:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(payload), changed


async def migrate(apply: bool) -> None:
    await db_manager.init_mongodb()
    try:
        cases = await UseCase.find_all().to_list()
        changed = 0
        complete = 0
        for case in cases:
            source = case.model_dump()
            derived = derive_simplified(source)
            if all(derived.values()):
                complete += 1
            if any(text(getattr(case, key, None)) != value for key, value in derived.items()):
                changed += 1
                if apply:
                    for key, value in derived.items():
                        setattr(case, key, value)
                    await case.save()
        print(json.dumps({"database_total": len(cases), "database_changed": changed, "all_five_fields_populated": complete, "mode": "apply" if apply else "preview"}, indent=2))
    finally:
        await db_manager.close_connections()

    seed_summary = []
    for path in seed_files():
        total, changed = update_seed_file(path, apply)
        seed_summary.append({"file": str(path.relative_to(ROOT)), "total": total, "changed": changed})
    print(json.dumps({"seed_files": seed_summary, "mode": "apply" if apply else "preview"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply additive updates to MongoDB and seed JSON files")
    args = parser.parse_args()
    asyncio.run(migrate(args.apply))
