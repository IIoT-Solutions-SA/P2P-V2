import re
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.mongo_models import UseCase, User as MongoUser, Organization
from app.schemas.usecase import UseCaseCreate
from app.services.database_service import UserService


def _slugify(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[\(\)]", "", text)
    text = re.sub(r"[\s\W_]+", "-", text)
    text = text.strip("-")
    return text


class UseCaseSubmissionService:
    @staticmethod
    async def create_use_case(db: AsyncSession, user_supertokens_id: str, data: UseCaseCreate) -> UseCase:
        # Lookup submitting user via PG by supertokens id, then resolve Mongo user by email
        pg_user = await UserService.get_user_by_supertokens_id(db, user_supertokens_id)
        if not pg_user:
            raise HTTPException(status_code=401, detail="Invalid session user")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        organization_id = getattr(mongo_user, "organization_id", None)
        if not organization_id:
            # Auto-link organization for legacy users: derive from email domain
            try:
                domain = (pg_user.email or "").split("@")[1]
            except Exception:
                domain = None
            if domain:
                existing_org = await Organization.find_one(Organization.domain == domain)
                if existing_org:
                    organization_id = str(existing_org.id)
                else:
                    org_name = domain.split(".")[0].replace("-", " ").title()
                    new_org = Organization(name=org_name, domain=domain, country="Saudi Arabia")
                    await new_org.insert()
                    organization_id = str(new_org.id)
                # Persist link on mongo user for future requests
                mongo_user.organization_id = organization_id
                await mongo_user.save()
            if not organization_id:
                raise HTTPException(status_code=400, detail="User is not linked to an organization and auto-link failed")

        # Resolve slugs
        title_slug = _slugify(data.title)
        # Try to read organization name to derive company_slug
        company_slug = None
        try:
            org = await Organization.get(organization_id)
            if org and getattr(org, "name", None):
                company_slug = _slugify(org.name)
        except Exception:
            company_slug = None

        # Map request to UseCase document
        use_case_doc = UseCase(
            submitted_by=str(mongo_user.id),
            title=data.title,
            problem_statement=data.description,
            solution_description=data.methodology,
            factory_name=data.factoryName,
            region=data.city,
            location={"lat": data.latitude, "lng": data.longitude},
            category=data.category,
            implementation_time=data.implementationTime,
            roi_percentage=data.roiPercentage,
            images=data.images or [],
            business_challenge={
                "industry_context": data.industryContext,
                "specific_problems": data.specificProblems,
                "business_impact": {
                    "financial_loss": data.financialLoss
                }
            },
            solution_details={
                "selection_criteria": data.selectionCriteria,
                "vendor_evaluation": {"selected_vendor": data.selectedVendor},
                "technology_components": [
                    {"component": f"Component {i+1}", "details": comp}
                    for i, comp in enumerate(data.technologyComponents)
                ]
            },
            implementation_details={
                "methodology": data.methodology,
                "total_budget": data.totalBudget,
                "total_duration": data.implementationTime
            },
            results={
                "quantitative_metrics": [
                    {
                        "metric": r.metric,
                        "baseline": r.baseline,
                        "current": r.current,
                        "improvement": r.improvement,
                    }
                    for r in data.quantitativeResults
                ],
                "roi_analysis": {
                    "annual_savings": data.annualSavings,
                },
            },
            challenges_and_solutions=[
                {
                    "challenge": c.challenge,
                    "description": c.description,
                    "solution": c.solution,
                    "outcome": c.outcome,
                }
                for c in data.challengesSolutions
            ],
            contact_person=data.contactPerson,
            contact_title=data.contactTitle,
            title_slug=title_slug,
            company_slug=company_slug,
            impact_metrics={
                "benefits": "; ".join(
                    [f"{r.improvement} {r.metric}" for r in data.quantitativeResults if r.improvement and r.metric]
                )
            },
            published=True,
            featured=False,
        )

        # Optional extended sections
        if data.technical_architecture and data.technical_architecture.system_overview:
            use_case_doc.technical_architecture = {
                "system_overview": data.technical_architecture.system_overview,
                "components": data.technical_architecture.components,
                "security_measures": data.technical_architecture.security_measures,
                "scalability_design": data.technical_architecture.scalability_design,
            }
        if data.future_roadmap:
            use_case_doc.future_roadmap = [
                {
                    "timeline": fr.timeline,
                    "initiative": fr.initiative,
                    "description": fr.description,
                    "expected_benefit": fr.expected_benefit,
                }
                for fr in data.future_roadmap
            ]
        if data.lessons_learned:
            use_case_doc.lessons_learned = [
                {
                    "category": ll.category,
                    "lesson": ll.lesson,
                    "description": ll.description,
                    "recommendation": ll.recommendation,
                }
                for ll in data.lessons_learned
            ]

        # Optional extended fields mapping
        if data.industryTags:
            use_case_doc.industry_tags = data.industryTags
        if data.technologyTags:
            use_case_doc.technology_tags = data.technologyTags
        if data.vendorProcess or data.vendorSelectionReasons:
            use_case_doc.solution_details = use_case_doc.solution_details or {}
            if data.vendorProcess:
                use_case_doc.solution_details["vendor_evaluation"] = use_case_doc.solution_details.get("vendor_evaluation", {})
                use_case_doc.solution_details["vendor_evaluation"]["process"] = data.vendorProcess
            if data.vendorSelectionReasons:
                use_case_doc.solution_details = use_case_doc.solution_details or {}
                use_case_doc.solution_details["vendor_evaluation"] = use_case_doc.solution_details.get("vendor_evaluation", {})
                use_case_doc.solution_details["vendor_evaluation"]["selection_reasons"] = data.vendorSelectionReasons
        if data.projectTeamInternal or data.projectTeamVendor:
            use_case_doc.implementation_details = use_case_doc.implementation_details or {}
            use_case_doc.implementation_details["project_team"] = use_case_doc.implementation_details.get("project_team", {})
            if data.projectTeamInternal:
                use_case_doc.implementation_details["project_team"]["internal"] = data.projectTeamInternal
            if data.projectTeamVendor:
                use_case_doc.implementation_details["project_team"]["vendor"] = data.projectTeamVendor
        if data.phases:
            use_case_doc.implementation_details = use_case_doc.implementation_details or {}
            use_case_doc.implementation_details["phases"] = data.phases
        if data.qualitativeImpacts:
            use_case_doc.results = use_case_doc.results or {}
            use_case_doc.results["qualitative_impacts"] = data.qualitativeImpacts
        if data.roiTotalInvestment or data.roiThreeYearRoi:
            use_case_doc.results = use_case_doc.results or {}
            use_case_doc.results["roi_analysis"] = use_case_doc.results.get("roi_analysis", {})
            if data.roiTotalInvestment:
                use_case_doc.results["roi_analysis"]["total_investment"] = data.roiTotalInvestment
            if data.roiThreeYearRoi:
                use_case_doc.results["roi_analysis"]["three_year_roi"] = data.roiThreeYearRoi

        await use_case_doc.create()
        return use_case_doc


