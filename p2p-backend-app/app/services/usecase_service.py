import re
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from bson import ObjectId
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
                    # Preserve the exact organization name supplied during signup. Domain-derived
                    # identifiers are only a legacy fallback and must never replace brand casing.
                    org_name = (getattr(mongo_user, "company", None) or "").strip() or domain.split(".")[0].replace("-", " ").title()
                    new_org = Organization(name=org_name, domain=domain, country="Saudi Arabia")
                    await new_org.insert()
                    organization_id = str(new_org.id)
                # Persist link on mongo user for future requests
                mongo_user.organization_id = organization_id
                await mongo_user.save()
            if not organization_id:
                raise HTTPException(status_code=400, detail="User is not linked to an organization and auto-link failed")

        # Keep a lowercase slug for URLs and the exact canonical organization name for display.
        # Display text must never be reconstructed from the slug because that destroys brand casing
        # such as IIoT, 3M, e& and iMile.
        title_slug = _slugify(data.title)
        company_slug = None
        organization_name = None
        try:
            org = await Organization.get(organization_id)
            if org and getattr(org, "name", None):
                organization_name = org.name.strip()
                company_slug = _slugify(organization_name)
        except Exception:
            company_slug = None
            organization_name = None

        # Map request to UseCase document
        use_case_doc = UseCase(
            submitted_by=str(mongo_user.id),  # Store MongoDB ID - more stable than SuperTokens session ID
            title=data.title,
            subtitle=data.subtitle,  # FIX: Now saving subtitle
            problem_statement=data.description,  # This is the main description
            executive_summary=data.description,  # FIX: Also save as executive_summary for compatibility
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
            organization_name=organization_name,
            problem=data.problem or data.industryContext,
            technology=data.technology or data.methodology,
            budget=data.budget or data.totalBudget,
            outcomes=data.outcomes or "\n".join(data.qualitativeImpacts or [r.improvement for r in data.quantitativeResults]),
            challenges=data.challenges or "\n\n".join(c.description for c in data.challengesSolutions),
            impact_metrics={
                "benefits": "; ".join(
                    [f"{r.improvement} {r.metric}" for r in data.quantitativeResults if r.improvement and r.metric]
                )
            },
            published=True,
            featured=False,
        )

        # Optional extended sections
        if data.technical_architecture:
            tech_arch = {}
            if hasattr(data.technical_architecture, 'system_overview') and data.technical_architecture.system_overview:
                tech_arch["system_overview"] = data.technical_architecture.system_overview
            # Handle both 'components' and 'architecture_components' field names
            if hasattr(data.technical_architecture, 'architecture_components') and data.technical_architecture.architecture_components:
                tech_arch["architecture_components"] = data.technical_architecture.architecture_components
            elif hasattr(data.technical_architecture, 'components') and data.technical_architecture.components:
                tech_arch["architecture_components"] = data.technical_architecture.components
            if hasattr(data.technical_architecture, 'security_measures') and data.technical_architecture.security_measures:
                tech_arch["security_measures"] = data.technical_architecture.security_measures
            if hasattr(data.technical_architecture, 'scalability_design') and data.technical_architecture.scalability_design:
                tech_arch["scalability_design"] = data.technical_architecture.scalability_design
            if tech_arch:
                use_case_doc.technical_architecture = tech_arch
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

    @staticmethod
    async def update_use_case(
        db: AsyncSession,
        user_supertokens_id: str,
        use_case_id: str,
        update_data: dict
    ) -> UseCase:
        """Update a use case with authorization check"""
        # Lookup submitting user via PG by supertokens id, then resolve Mongo user by email
        pg_user = await UserService.get_user_by_supertokens_id(db, user_supertokens_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Find the use case
        try:
            use_case = await UseCase.find_one(UseCase.id == ObjectId(use_case_id))
        except Exception:
            use_case = None
        if not use_case:
            raise HTTPException(status_code=404, detail="Use case not found")

        # AUTHORIZATION CHECK - only author can edit their use case
        if use_case.submitted_by != str(mongo_user.id):
            raise HTTPException(status_code=403, detail="User not authorized to edit this use case")

        # Map frontend data to MongoDB structure (same mapping as create_use_case)
        mapped_update = {}
        
        # Basic fields
        if "title" in update_data:
            mapped_update["title"] = update_data["title"]
        if "subtitle" in update_data:
            mapped_update["subtitle"] = update_data["subtitle"]
        if "description" in update_data:
            mapped_update["problem_statement"] = update_data["description"]  # Frontend's description
            mapped_update["executive_summary"] = update_data["description"]  # Also save as executive_summary
        if "category" in update_data:
            mapped_update["category"] = update_data["category"]
        if "factoryName" in update_data:
            mapped_update["factory_name"] = update_data["factoryName"]
        if "city" in update_data:
            mapped_update["region"] = update_data["city"]
        if "latitude" in update_data or "longitude" in update_data:
            location = {}
            if "latitude" in update_data:
                location["lat"] = update_data["latitude"]
            if "longitude" in update_data:
                location["lng"] = update_data["longitude"]
            if location:
                mapped_update["location"] = location
        if "implementationTime" in update_data:
            mapped_update["implementation_time"] = update_data["implementationTime"]
        if "roiPercentage" in update_data:
            mapped_update["roi_percentage"] = update_data["roiPercentage"]
        if "contactPerson" in update_data:
            mapped_update["contact_person"] = update_data["contactPerson"]
        if "contactTitle" in update_data:
            mapped_update["contact_title"] = update_data["contactTitle"]
        if "images" in update_data:
            mapped_update["images"] = update_data["images"]

        # Nested structures - business_challenge
        business_challenge_update = {}
        if "industryContext" in update_data:
            business_challenge_update["industry_context"] = update_data["industryContext"]
        if "specificProblems" in update_data:
            business_challenge_update["specific_problems"] = update_data["specificProblems"]
        if "financialLoss" in update_data:
            business_challenge_update["business_impact"] = {"financial_loss": update_data["financialLoss"]}
        if business_challenge_update:
            mapped_update["business_challenge"] = business_challenge_update

        # Nested structures - solution_details
        solution_details_update = {}
        if "selectionCriteria" in update_data:
            solution_details_update["selection_criteria"] = update_data["selectionCriteria"]
        if "selectedVendor" in update_data:
            solution_details_update["vendor_evaluation"] = {"selected_vendor": update_data["selectedVendor"]}
        if "technologyComponents" in update_data:
            solution_details_update["technology_components"] = [
                {"component": f"Component {i+1}", "details": comp}
                for i, comp in enumerate(update_data["technologyComponents"])
            ]
        if solution_details_update:
            mapped_update["solution_details"] = solution_details_update

        # Nested structures - implementation_details
        implementation_details_update = {}
        if "methodology" in update_data:
            implementation_details_update["methodology"] = update_data["methodology"]
        if "totalBudget" in update_data:
            implementation_details_update["total_budget"] = update_data["totalBudget"]
        if "implementationTime" in update_data:
            implementation_details_update["total_duration"] = update_data["implementationTime"]
        if implementation_details_update:
            mapped_update["implementation_details"] = implementation_details_update

        # Nested structures - results
        results_update = {}
        if "quantitativeResults" in update_data:
            results_update["quantitative_metrics"] = [
                {
                    "metric": r.get("metric", ""),
                    "baseline": r.get("baseline", ""),
                    "current": r.get("current", ""),
                    "improvement": r.get("improvement", ""),
                }
                for r in update_data["quantitativeResults"]
            ]
        if "annualSavings" in update_data:
            results_update["roi_analysis"] = {"annual_savings": update_data["annualSavings"]}
        if results_update:
            mapped_update["results"] = results_update

        # Challenges and solutions
        if "challengesSolutions" in update_data:
            mapped_update["challenges_and_solutions"] = [
                {
                    "challenge": c.get("challenge", ""),
                    "description": c.get("description", ""),
                    "solution": c.get("solution", ""),
                    "outcome": c.get("outcome", ""),
                }
                for c in update_data["challengesSolutions"]
            ]

        # Technical Architecture
        if "technical_architecture" in update_data:
            tech_arch = update_data["technical_architecture"]
            if tech_arch:
                mapped_tech = {}
                if "system_overview" in tech_arch:
                    mapped_tech["system_overview"] = tech_arch["system_overview"]
                if "architecture_components" in tech_arch:
                    mapped_tech["architecture_components"] = tech_arch["architecture_components"]
                if "security_measures" in tech_arch:
                    mapped_tech["security_measures"] = tech_arch["security_measures"]
                if "scalability_design" in tech_arch:
                    mapped_tech["scalability_design"] = tech_arch["scalability_design"]
                if mapped_tech:
                    mapped_update["technical_architecture"] = mapped_tech

        # Lessons Learned
        if "lessons_learned" in update_data:
            mapped_update["lessons_learned"] = update_data["lessons_learned"]

        # Future Roadmap
        if "future_roadmap" in update_data:
            mapped_update["future_roadmap"] = update_data["future_roadmap"]

        # ROI fields
        if "roiTotalInvestment" in update_data:
            if "results" not in mapped_update:
                mapped_update["results"] = {}
            if "roi_analysis" not in mapped_update["results"]:
                mapped_update["results"]["roi_analysis"] = {}
            mapped_update["results"]["roi_analysis"]["total_investment"] = update_data["roiTotalInvestment"]

        if "roiThreeYearRoi" in update_data:
            if "results" not in mapped_update:
                mapped_update["results"] = {}
            if "roi_analysis" not in mapped_update["results"]:
                mapped_update["results"]["roi_analysis"] = {}
            mapped_update["results"]["roi_analysis"]["three_year_roi"] = update_data["roiThreeYearRoi"]

        # Optional fields
        if "industryTags" in update_data:
            mapped_update["industry_tags"] = update_data["industryTags"]
        if "technologyTags" in update_data:
            mapped_update["technology_tags"] = update_data["technologyTags"]

        # Update the use case with properly mapped data and edited timestamp
        update_query = {"$set": {**mapped_update, "edited_at": datetime.utcnow(), "updated_at": datetime.utcnow()}}
        await use_case.update(update_query)
        
        # Return the updated use case
        return await UseCase.find_one(UseCase.id == ObjectId(use_case_id))

    @staticmethod
    async def delete_use_case(
        db: AsyncSession,
        user_supertokens_id: str,
        use_case_id: str
    ) -> dict:
        """Soft delete a use case with authorization check"""
        # Lookup submitting user via PG by supertokens id, then resolve Mongo user by email
        pg_user = await UserService.get_user_by_supertokens_id(db, user_supertokens_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Find the use case
        try:
            use_case = await UseCase.find_one(UseCase.id == ObjectId(use_case_id))
        except Exception:
            use_case = None
        if not use_case:
            raise HTTPException(status_code=404, detail="Use case not found")

        # AUTHORIZATION CHECK - only author can delete their use case
        if use_case.submitted_by != str(mongo_user.id):
            raise HTTPException(status_code=403, detail="User not authorized to delete this use case")

        # PERMANENT DELETE: Remove use case from database
        await use_case.delete()

        # Clean up S3 images if any
        if use_case.images:
            import boto3
            from app.core.config import settings
            import logging

            logger = logging.getLogger(__name__)
            s3_client = boto3.client(
                "s3",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                endpoint_url=settings.S3_ENDPOINT_URL,
            )

            for image_url in use_case.images:
                try:
                    # Extract object key from the URL
                    if image_url and "/o/" in image_url:
                        s3_key = image_url.split("/o/")[-1]
                    elif image_url and "amazonaws.com/" in image_url:
                        s3_key = image_url.split("amazonaws.com/")[-1]
                    else:
                        continue
                        s3_client.delete_object(
                            Bucket=settings.S3_USECASE_MEDIA_BUCKET,
                            Key=s3_key
                        )
                        logger.info(f"Deleted S3 use case image: {s3_key}")
                except Exception as e:
                    logger.error(f"Failed to delete S3 image {image_url}: {e}")
                    # Continue with deletion even if S3 cleanup fails

        # Optional: Update user stats to reflect the deletion
        # This could be implemented later if needed

        return {"status": "deleted"}


