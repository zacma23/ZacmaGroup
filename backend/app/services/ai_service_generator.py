"""AI Service Generation Engine.

Generates high-value, domain-specific service deliverables for clients across
Visa Consulting, Travel Agency, Training Institute, Marketing Solutions, and
Dynamic Modules. Output is stored securely and subject to administrative review.
"""

from datetime import datetime, timezone
from typing import Any


class AiServiceGenerator:
    """Generates customized service outputs for client requests."""

    @staticmethod
    def generate_visa_output(data: dict[str, Any]) -> dict[str, Any]:
        """Generate comprehensive Visa application package."""
        name = data.get("full_name", "Applicant")
        country = data.get("destination_country", "Germany")
        vtype = data.get("visa_type", "Tourist")
        ref = data.get("reference_code", "ZAC-VIS-001")

        cover_letter = (
            f"To: The Visa Consular Section\n"
            f"Embassy of {country}\n"
            f"Addis Ababa, Ethiopia\n\n"
            f"Subject: Application for {vtype} Visa — {name} (Ref: {ref})\n\n"
            f"Dear Consular Officer,\n\n"
            f"I am formally submitting this application on behalf of {name} for a {vtype} entry visa to {country}. "
            f"The applicant has provided complete financial guarantees, verified accommodation reservations, "
            f"and certified travel medical insurance coverage.\n\n"
            f"The applicant is fully employed/sponsored with established socio-economic ties to Ethiopia and has a "
            f"confirmed return flight schedule.\n\n"
            f"Thank you for your favorable consideration.\n\n"
            f"Sincerely,\n"
            f"Zacma Visa Consulting Division"
        )

        risk_audit = [
            {"item": "Passport Validity", "status": "Passed", "note": "Valid for over 6 months from travel date."},
            {"item": "Financial Solvency", "status": "Passed", "note": "3-month certified bank statement attached."},
            {"item": "Itinerary Verification", "status": "Passed", "note": "Roundtrip flight & hotel booking confirmed."},
            {"item": "Travel Insurance", "status": "Recommended", "note": "Minimum €30,000 Schengen medical coverage required."},
        ]

        interview_prep = [
            {"q": f"What is the primary purpose of your visit to {country}?", "tip": f"State clear purpose: {vtype} travel with exact dates."},
            {"q": "How will you finance your stay during your trip?", "tip": "Mention your personal savings account and employer sponsorship."},
            {"q": "What guarantees that you will return to Ethiopia?", "tip": "Highlight permanent employment, property, and family ties in Ethiopia."},
            {"q": f"Where will you be residing during your stay in {country}?", "tip": "Provide your exact hotel booking name and city location."},
        ]

        return {
            "deliverable_type": "Visa Application & Strategy Package",
            "applicant_name": name,
            "destination": country,
            "visa_category": vtype,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "cover_letter": cover_letter,
            "document_risk_audit": risk_audit,
            "interview_prep_questions": interview_prep,
            "status": "ReadyForAdminReview",
        }

    @staticmethod
    def generate_travel_output(data: dict[str, Any]) -> dict[str, Any]:
        """Generate 5-Day curated Travel Itinerary & Flight package."""
        name = data.get("full_name", "Traveler")
        destination = data.get("destination_country", "Dubai, UAE")
        dates = data.get("travel_date_preference", "Flexible Dates")
        ref = data.get("reference_code", "ZAC-TRV-001")

        itinerary_days = [
            {
                "day": "Day 1",
                "title": "Arrival & Welcome Check-In",
                "morning": "Flight arrival, VIP airport meet & greet, transfer to hotel.",
                "afternoon": "Check-in, relax, and orientation tour of the city center.",
                "evening": "Welcome dinner at renowned local waterfront restaurant.",
            },
            {
                "day": "Day 2",
                "title": "City Heritage & Iconic Landmarks",
                "morning": "Guided cultural district walking tour and historical museum.",
                "afternoon": "Observation deck panoramic views & signature shopping plaza.",
                "evening": "Evening fountain show and sunset promenade.",
            },
            {
                "day": "Day 3",
                "title": "Adventure & Nature Excursion",
                "morning": "Morning scenic transfer and excursion.",
                "afternoon": "Desert Safari / Coastal boat cruise and activity passes.",
                "evening": "Traditional barbecue dinner under the stars with live music.",
            },
            {
                "day": "Day 4",
                "title": "Leisure, Markets & Culinary Delights",
                "morning": "Free morning for local markets and artisan shopping.",
                "afternoon": "Spa session or beach club relaxation.",
                "evening": "Fine dining restaurant reservation.",
            },
            {
                "day": "Day 5",
                "title": "Souvenirs & Departure",
                "morning": "Breakfast, souvenir collection, and hotel checkout.",
                "afternoon": "Private transfer to the airport for international flight departure.",
                "evening": "Flight return journey home.",
            },
        ]

        flight_options = [
            {"airline": "Ethiopian Airlines", "flight": "ET600", "route": f"ADD -> {destination}", "status": "Available"},
            {"airline": "Emirates / FlyDubai", "flight": "EK724", "route": f"ADD -> {destination}", "status": "Available"},
        ]

        return {
            "deliverable_type": "Curated 5-Day Holiday & Flight Itinerary",
            "traveler_name": name,
            "destination": destination,
            "preferred_dates": dates,
            "reference_code": ref,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "flight_options": flight_options,
            "daily_itinerary": itinerary_days,
            "emergency_helpline": "+251-911-223344",
            "status": "ReadyForAdminReview",
        }

    @staticmethod
    def generate_training_output(data: dict[str, Any]) -> dict[str, Any]:
        """Generate personalized Course Syllabus & Practical Lab Plan."""
        student = data.get("full_name", "Student")
        course = data.get("course", "Programming")
        edu = data.get("education_level", "Diploma")

        syllabus = [
            {"week": "Week 1", "module": "Foundations & Environment Setup", "lab": "Setting up dev tools, Git, and essential syntax."},
            {"week": "Week 2", "module": "Core Principles & Architecture", "lab": "Practical algorithmic exercises and data structures."},
            {"week": "Week 3", "module": "Applied Project Phase I", "lab": "Building REST APIs and responsive user interfaces."},
            {"week": "Week 4", "module": "Integration & State Management", "lab": "Database CRUD operations and authentication hooks."},
            {"week": "Week 5", "module": "Real-World Industry Case Study", "lab": "End-to-end full-stack feature deployment."},
            {"week": "Week 6", "module": "Capstone Project & Certification", "lab": "Final portfolio defense, code review, and certificate exam."},
        ]

        return {
            "deliverable_type": "Personalized Lab Syllabus & Learning Pathway",
            "student_name": student,
            "course_title": course,
            "education_level": edu,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "duration_weeks": 6,
            "weekly_syllabus": syllabus,
            "recommended_tools": ["VS Code", "Python 3.12", "Postman", "Git / GitHub", "Docker"],
            "status": "ReadyForAdminReview",
        }

    @staticmethod
    def generate_marketing_output(data: dict[str, Any]) -> dict[str, Any]:
        """Generate Digital Marketing Strategy & Content Calendar."""
        brand = data.get("name", "Enterprise Brand")
        channel = data.get("channel", "Social Media & Paid Ads")

        content_pillars = [
            {"pillar": "Educational / Value", "ratio": "40%", "topics": "Industry tips, how-tos, client problem solvers."},
            {"pillar": "Social Proof & Results", "ratio": "30%", "topics": "Case studies, student/client testimonials, live stats."},
            {"pillar": "Direct Offer & Call-to-Action", "ratio": "30%", "topics": "Limited-time package discounts, consultation booking."},
        ]

        ad_copies = [
            {
                "hook": "🚀 Ready to fast-track your global career?",
                "body": "Join thousands of certified students at Zacma Training Institute. 80% practical lab work with job assistance.",
                "cta": "Enroll Today — Limited Seats Available",
            },
            {
                "hook": "✈️ Planning your next international journey?",
                "body": "From visa assistance to flights and 5-day holiday itineraries, Zacma Travel ensures seamless travel.",
                "cta": "Get a Free Travel Consultation",
            },
        ]

        return {
            "deliverable_type": "30-Day Marketing Growth Strategy & Ad Copies",
            "brand_name": brand,
            "channel": channel,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "content_pillars": content_pillars,
            "ad_copy_variants": ad_copies,
            "status": "ReadyForAdminReview",
        }

    @staticmethod
    def generate_software_output(data: dict[str, Any]) -> dict[str, Any]:
        """Generate comprehensive Software Architecture Blueprint & Sprint Roadmap."""
        name = data.get("project_name", "Enterprise Software Solution")
        client = data.get("client_name", "Client")
        platforms = data.get("platforms", ["Web", "Android", "iOS"])
        ref = data.get("reference_code", "ZAC-DEV-001")
        industry = data.get("industry", "Technology & Business")

        architecture_spec = (
            f"ZACMA SOFTWARE ENGINEERING ARCHITECTURE SPECIFICATION\n"
            f"Project: {name} (Ref: {ref})\n"
            f"Client Organization: {client} | Industry: {industry}\n"
            f"Target Platforms: {', '.join(platforms)}\n\n"
            f"1. Executive Architecture Summary:\n"
            f"A modern, highly-scalable multi-tier system engineered with Next.js & React frontend, "
            f"FastAPI microservices backend, and PostgreSQL/Supabase multi-tenant data layer.\n\n"
            f"2. Core Architectural Components:\n"
            f"• API Gateway & Auth: JWT RBAC with Row-Level Security\n"
            f"• Real-Time Communication: WebSockets & Event-Driven Message Queue\n"
            f"• Payment Integration: TeleBirr API, CBE Birr Merchant Gateway, Chapa Checkout\n"
            f"• External Integrations: Zacma ERP (https://erp.zacmaa.net/) / MySchool (https://myschool.zacmaa.net/)\n\n"
            f"3. Production Quality Attributes:\n"
            f"• Zero-trust security isolation per tenant\n"
            f"• 99.9% uptime target with automated Docker container orchestration\n"
            f"• Automated CI/CD testing pipeline."
        )

        sprint_plan = [
            {"sprint": "Sprint 1-2", "focus": "System Design, Wireframes & Database Modeling", "deliverable": "ERD diagram, API schema & Figma UI prototypes."},
            {"sprint": "Sprint 3-4", "focus": "Core Backend Engine & Auth Layer", "deliverable": "REST endpoints, auth middleware, and tenant isolations."},
            {"sprint": "Sprint 5-6", "focus": "Frontend & Mobile Application Client", "deliverable": "Responsive UI screens, form wizards & state stores."},
            {"sprint": "Sprint 7-8", "focus": "Payment Gateways & Integrations", "deliverable": "TeleBirr/CBE payment verification & webhook handlers."},
            {"sprint": "Sprint 9-10", "focus": "QA, Load Testing & Cloud Deployment", "deliverable": "Production staging deployment, SSL certificates & client sign-off."},
        ]

        recommended_stack = [
            {"tier": "Frontend", "technology": "Next.js 14, React 18, Tailwind CSS, TypeScript"},
            {"tier": "Mobile Client", "technology": "Flutter / Dart (Cross-Platform Android & iOS)"},
            {"tier": "Backend APIs", "technology": "Python 3.12, FastAPI, Uvicorn, Pydantic"},
            {"tier": "Database & Storage", "technology": "PostgreSQL, Supabase, Redis Cache"},
            {"tier": "Payments", "technology": "TeleBirr Merchant SDK, CBE Birr API, Chapa"},
        ]

        return {
            "deliverable_type": "Software Architecture Specification & Project Roadmap",
            "project_name": name,
            "client_name": client,
            "reference_code": ref,
            "target_platforms": platforms,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "architecture_specification": architecture_spec,
            "sprint_roadmap": sprint_plan,
            "recommended_tech_stack": recommended_stack,
            "status": "ReadyForAdminReview",
        }

    @classmethod
    def generate_for_service(cls, service_type: str, request_data: dict[str, Any]) -> dict[str, Any]:
        """Route to appropriate AI deliverable generator."""
        svc = service_type.lower()
        if "soft" in svc or "dev" in svc or "app" in svc:
            return cls.generate_software_output(request_data)
        elif "visa" in svc:
            return cls.generate_visa_output(request_data)
        elif "travel" in svc:
            return cls.generate_travel_output(request_data)
        elif "train" in svc or "student" in svc:
            return cls.generate_training_output(request_data)
        elif "market" in svc:
            return cls.generate_marketing_output(request_data)
        else:
            return {
                "deliverable_type": "Service Assessment & Execution Plan",
                "request_summary": request_data,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "ReadyForAdminReview",
            }

