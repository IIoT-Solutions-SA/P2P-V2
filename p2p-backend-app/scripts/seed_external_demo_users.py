"""Add the 18 external demo users without deleting existing team or content data."""

import asyncio
import os
import secrets
import sys
from datetime import datetime, timedelta

import httpx

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.models.mongo_models import Invitation, User


DEMO_USERS = [
    ("ahmed.faisal@advanced-electronics.com", "Ahmed", "Al-Faisal", "Advanced Electronics Co.", "Operations Manager", "Electronics", "500+", "Riyadh"),
    ("sara.hassan@gulf-plastics.com", "Sara", "Hassan", "Gulf Plastics Industries", "Operations Lead", "Plastics & Chemicals", "200+", "Dammam"),
    ("mohammed.rashid@saudi-steel.com", "Mohammed", "Rashid", "Saudi Steel Works", "Factory Manager", "Heavy Industry", "1000+", "Jubail"),
    ("fatima.ali@arabian-food.com", "Fatima", "Ali", "Arabian Food Processing", "Supply Chain Director", "Food & Beverage", "300+", "Jeddah"),
    ("khalid.abdul@precision-mfg.com", "Khalid", "Abdul", "Precision Manufacturing Ltd", "Automation Engineer", "Automotive", "150+", "Riyadh"),
    ("sarah.ahmed@pharma-excellence.com", "Sarah", "Ahmed", "Pharma Excellence Ltd", "Quality Manager", "Pharmaceuticals", "400+", "Riyadh"),
    ("mohammed.alshahri@secure-supply.com", "Mohammed", "Al-Shahri", "Secure Supply Co.", "Logistics Head", "Logistics", "250+", "Dammam"),
    ("fatima.otaibi@safety-first.com", "Fatima", "Al-Otaibi", "Safety First Industries", "Safety Officer", "Safety & Training", "120+", "Riyadh"),
    ("hessa.alsabah@yanbu-smart.com", "Hessa", "Al-Sabah", "Yanbu Smart Industries", "Founder & CEO", "Industrial IoT (IIoT)", "10-50", "Yanbu"),
    ("faisal.alghamdi@redsea-logistics.com", "Faisal", "Al-Ghamdi", "Red Sea Logistics", "Head of Operations", "Logistics", "200-500", "King Abdullah Economic City"),
    ("nouf.almutawa@najd-dates.com", "Nouf", "Al-Mutawa", "Najd Dates Processing", "Production Director", "Food & Beverage", "50-200", "Qassim"),
    ("tarek.mansour@alkhobar-mfg.com", "Tarek", "Mansour", "Al-Khobar Advanced Manufacturing", "Digital Transformation Lead", "Manufacturing", "200-500", "Al-Khobar"),
    ("omar.bakr@ep-construction.com", "Omar", "Bakr", "Eastern Province Construction Materials", "Chief Engineer", "Construction & Building Materials", "500+", "Dammam"),
    ("aisha.aljameel@saudi-retail.com", "Aisha", "Al-Jameel", "Saudi Retail Distribution Co.", "Supply Chain Director", "Retail & FMCG", "1000+", "Jeddah"),
    ("sameer.khan@mea-integrators.com", "Sameer", "Khan", "MEA Systems Integrators", "Senior Project Manager", "Technology & Integration", "50-200", "Riyadh"),
    ("rania.alabdullah@agritech-sa.com", "Rania", "Al-Abdullah", "Agri-Tech Solutions Arabia", "Technical Director", "Agriculture Technology", "10-50", "Al-Kharj"),
    ("bandar.alharbi@gulf-plastics.com", "Bandar", "Al-Harbi", "Gulf Plastics Industries", "General Manager", "Plastics & Chemicals", "200+", "Jubail"),
    ("layla.iskandar@neom-solar.com", "Layla", "Iskandar", "NEOM Solar Power Systems", "Operations Lead", "Renewable Energy", "50-200", "Tabuk"),
]


async def seed_external_demo_users() -> None:
    await db_manager.init_mongodb()
    existing = {user.email.lower() for user in await User.find_all().to_list()}
    created = 0
    skipped = 0
    failures: list[str] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for email, first_name, last_name, company, title, industry, size, city in DEMO_USERS:
            if email.lower() in existing:
                skipped += 1
                continue
            response = await client.post(
                "http://backend:8000/api/v1/auth/custom-signup",
                json={
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "password": "password123",
                    "companyName": company,
                    "industrySector": industry,
                    "companySize": size,
                    "city": city,
                    "title": title,
                },
            )
            if response.status_code == 200 and response.json().get("status") == "OK":
                created += 1
                continue

            # A second person on an existing company domain must join through
            # the same invitation path used by the live application.
            if "An admin already exists for the organization" in response.text:
                inviter = await User.find_one(User.company == company)
                if inviter:
                    token = secrets.token_urlsafe(32)
                    await Invitation(
                        email=email,
                        token=token,
                        invited_by_id=str(inviter.id),
                        invited_by_email=inviter.email,
                        invited_by_name=inviter.name,
                        expires_at=datetime.utcnow() + timedelta(days=7),
                    ).create()
                    invited_payload = {
                        "firstName": first_name,
                        "lastName": last_name,
                        "email": email,
                        "password": "password123",
                        "companyName": company,
                        "industrySector": industry,
                        "companySize": size,
                        "city": city,
                        "title": title,
                        "inviteToken": token,
                    }
                    invited_response = await client.post(
                        "http://backend:8000/api/v1/auth/custom-signup",
                        json=invited_payload,
                    )
                    if invited_response.status_code == 200 and invited_response.json().get("status") == "OK":
                        created += 1
                        continue
                    response = invited_response

            failures.append(f"{email}: {response.status_code} {response.text}")

    await db_manager.close_connections()
    print(f"External demo users: created={created}, skipped={skipped}, failed={len(failures)}")
    for failure in failures:
        print(failure)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(seed_external_demo_users())
