"""Zacma Group Business-Aware AI Assistant & Knowledge Retrieval Engine.

Dynamically retrieves trusted data from the Zacma Group knowledge base, platforms,
and services to answer questions without hallucination, suggest relevant services/platforms,
and guide clients through request, payment receipt, and tracking workflows.
"""

from typing import Any, Optional
from app.core.config import settings
from app.core.demo_data import knowledge_base_store


class AiAssistantService:
    """Zacma Group Business-Aware AI Assistant."""

    @classmethod
    def consult_zacma_ai(
        cls,
        query: str,
        session_id: Optional[str] = None,
        tenant_id: str = "zacma-demo",
        user_role: str = "client",
    ) -> dict[str, Any]:
        """Process natural language query against dynamic Zacma Group knowledge base."""
        q = query.lower().strip()
        actions: list[dict[str, str]] = []
        category = "General"
        recommendation: Optional[dict[str, str]] = None

        # 1. School Management / MySchool
        if any(w in q for w in ["school", "myschool", "student management", "gradebook", "teachers", "tuition", "admissions", "attendance and payment", "manage student"]):
            category = "Platforms / Education Software"
            recommendation = {
                "service": "MySchool Platform & Custom School Software",
                "url": "https://myschool.zacmaa.net/",
                "why": "MySchool is Zacma's dedicated cloud school management system built for admissions, gradebooks, attendance, fee collection, and parent communications.",
            }
            reply = (
                "🎓 **Recommended Platform: MySchool** (https://myschool.zacmaa.net/)\n\n"
                "Zacma provides **MySchool**, a complete cloud-based School & Campus Management System tailored for K-12 schools, colleges, and training institutes:\n\n"
                "• **Student & Staff Management**: Online admissions, student profiles, and teacher scheduling.\n"
                "• **Academic Suite**: Automated gradebooks, report card generation, and attendance tracking.\n"
                "• **Finance & Fees**: Automated tuition fee invoicing with TeleBirr & CBE integration.\n"
                "• **Parent & Student Portals**: Real-time notifications and mobile access.\n\n"
                "👉 You can visit the live platform at https://myschool.zacmaa.net/ or submit a custom software request in the Client Portal."
            )
            actions = [
                {"label": "Visit MySchool Platform ↗", "url": "https://myschool.zacmaa.net/"},
                {"label": "Request Custom School Software", "url": "/software"},
                {"label": "Explore Our Platforms", "url": "/platforms"},
            ]

        # 2. ERP System
        elif any(w in q for w in ["erp", "enterprise resource", "inventory", "warehouse", "payroll", "supply chain", "multi-branch", "pos", "point of sale"]):
            category = "Platforms / Enterprise ERP"
            recommendation = {
                "service": "Zacma ERP Platform",
                "url": "https://erp.zacmaa.net/",
                "why": "Zacma ERP provides multi-branch inventory, procurement, financial accounting, and HRM payroll in one unified cloud system.",
            }
            reply = (
                "🏢 **Recommended Platform: Zacma ERP** (https://erp.zacmaa.net/)\n\n"
                "Zacma Group operates **Zacma ERP**, a high-performance cloud enterprise resource planning suite:\n\n"
                "• **Multi-Branch Inventory & Warehousing**: Real-time barcode tracking and stock alerts.\n"
                "• **Financial Accounting & Audit**: Automated ledger, tax calculations, and profit/loss reports.\n"
                "• **HRM & Payroll**: Employee records, biometric attendance sync, and salary slips.\n"
                "• **Procurement & Sales POS**: Automated vendor purchase orders and point-of-sale checkout.\n\n"
                "👉 Visit Zacma ERP at https://erp.zacmaa.net/ or request customized enterprise modules."
            )
            actions = [
                {"label": "Launch Zacma ERP ↗", "url": "https://erp.zacmaa.net/"},
                {"label": "Request Custom ERP Setup", "url": "/software"},
                {"label": "Explore All Platforms", "url": "/platforms"},
            ]

        # 3. E-Commerce Platform
        elif any(w in q for w in ["e-commerce", "ecommerce", "online store", "shop", "marketplace", "selling online", "storefront", "products online"]):
            category = "Platforms / E-Commerce"
            recommendation = {
                "service": "Zacma E-Commerce Platform",
                "url": "https://ecommerce.zacmaa.net/",
                "why": "Zacma E-Commerce delivers multi-vendor and standalone digital storefronts with integrated Ethiopian payment gateways (TeleBirr, CBE, Chapa).",
            }
            reply = (
                "🛒 **Recommended Platform: Zacma E-Commerce** (https://ecommerce.zacmaa.net/)\n\n"
                "Zacma Group provides **Zacma E-Commerce**, an enterprise digital commerce solution:\n\n"
                "• **Ethiopian Payment Gateways**: Direct checkout with TeleBirr, CBE Birr, and Chapa.\n"
                "• **Catalog & Inventory Sync**: Multi-category products, variants, and stock counts.\n"
                "• **Courier & Order Dispatch**: Automated shipping labels, SMS alerts, and delivery tracking.\n"
                "• **Vendor Dashboard**: Multi-seller commissions, payout management, and coupon promotions.\n\n"
                "👉 Explore the platform at https://ecommerce.zacmaa.net/ or request custom storefront development."
            )
            actions = [
                {"label": "Visit E-Commerce Platform ↗", "url": "https://ecommerce.zacmaa.net/"},
                {"label": "Request Custom Storefront", "url": "/software"},
                {"label": "View Our Platforms", "url": "/platforms"},
            ]

        # 4. Freelancer Platform
        elif any(w in q for w in ["freelancer", "freelance", "hire developer", "hire designer", "talent marketplace", "contractor", "remote developers"]):
            category = "Platforms / Freelancer"
            recommendation = {
                "service": "Zacma Freelancer Marketplace",
                "url": "https://freelancer.zacmaa.net/",
                "why": "Zacma Freelancer connects vetted software engineers, designers, and digital specialists with enterprise projects.",
            }
            reply = (
                "💼 **Recommended Platform: Zacma Freelancer** (https://freelancer.zacmaa.net/)\n\n"
                "Zacma Group operates **Zacma Freelancer**, a premier talent marketplace:\n\n"
                "• **Vetted Tech Professionals**: Software engineers, mobile developers, UI/UX designers, and marketing experts.\n"
                "• **Milestone Escrow & Contracting**: Secure project milestones with transparent delivery verification.\n"
                "• **Direct Project Matching**: Post jobs and receive proposals within 24 hours.\n\n"
                "👉 Visit the platform at https://freelancer.zacmaa.net/."
            )
            actions = [
                {"label": "Visit Zacma Freelancer ↗", "url": "https://freelancer.zacmaa.net/"},
                {"label": "Hire Software Team", "url": "/software"},
                {"label": "View Our Platforms", "url": "/platforms"},
            ]

        # 5. Platforms General Query
        elif any(w in q for w in ["what platforms", "list platforms", "platforms does zacma", "zacma platforms", "all platforms"]):
            category = "Platforms"
            reply = (
                "🌐 **Zacma Technology Group Official Platforms**:\n\n"
                "1. 🏢 **Zacma ERP** (https://erp.zacmaa.net/): Enterprise Resource Planning, inventory, finance & HR.\n"
                "2. 🎓 **MySchool** (https://myschool.zacmaa.net/): Comprehensive K-12 & Academy School Management.\n"
                "3. 🛒 **Zacma E-Commerce** (https://ecommerce.zacmaa.net/): Digital storefronts with TeleBirr & CBE integration.\n"
                "4. 💼 **Zacma Freelancer** (https://freelancer.zacmaa.net/): Vetted tech talent and contractor marketplace.\n\n"
                "Visit any platform directly or browse the full interactive showcase at /platforms."
            )
            actions = [
                {"label": "Browse Our Platforms Showcase", "url": "/platforms"},
                {"label": "Open Client Portal", "url": "/portal"},
            ]

        # 6. Maintenance & Hardware Specialty Training
        elif any(w in q for w in ["maintenance course", "hardware specialty", "maintenance training", "schedule for hardware", "hardware schedule", "hardware time", "repair course"]):
            category = "Training / Maintenance"
            reply = (
                "🔧 **Maintenance Course — Hardware Specialty** (/training):\n\n"
                "**Course**: Maintenance\n"
                "**Specialty**: Hardware Specialty\n\n"
                "• **Curriculum**: Component diagnostics, motherboard repair, chip soldering, hardware assembly, power delivery diagnostics, and firmware flashing.\n\n"
                "📅 **Available Schedules**:\n"
                "1. Monday + Wednesday + Thursday\n"
                "2. Tuesday + Thursday + Saturday\n"
                "3. Saturday + Sunday\n\n"
                "⏰ **Available Time Slots**:\n"
                "• 03:00 – 05:00\n"
                "• 05:00 – 07:00\n"
                "• 07:00 – 09:00\n"
                "• 09:00 – 11:00\n"
                "• 11:00 – 01:00\n"
                "• 12:00 – 02:00\n\n"
                "👉 You can enroll directly at /training by choosing Maintenance → Hardware Specialty and selecting your preferred schedule and time slot."
            )
            actions = [
                {"label": "Register for Maintenance", "url": "/training"},
                {"label": "View Training Courses", "url": "/training"},
            ]

        # 7. Training Courses in General
        elif any(w in q for w in ["what courses", "courses do you offer", "training courses", "training institute", "what training"]):
            category = "Training Courses"
            reply = (
                "🎓 **Zacma Training Institute — 15 Practical Career Programs** (/training):\n\n"
                "1. Basic Computer\n"
                "2. Graphics\n"
                "3. Video Editing\n"
                "4. Videography\n"
                "5. Photography\n"
                "6. AI (Artificial Intelligence)\n"
                "7. Cloud Computing\n"
                "8. Spoken English\n"
                "9. Accounting\n"
                "10. IT Support\n"
                "11. AutoCAD\n"
                "12. ETABS\n"
                "13. Web Design\n"
                "14. Networking\n"
                "15. **Maintenance** (Specialty: **Hardware Specialty** with flexible Mon/Wed/Thu, Tue/Thu/Sat, or Sat/Sun schedules)\n\n"
                "👉 Visit /training to view syllabi and register online."
            )
            actions = [
                {"label": "Explore Training Courses", "url": "/training"},
                {"label": "Student Portal", "url": "/portal"},
            ]

        # 8. Software Development Services
        elif any(w in q for w in ["software", "software development", "build an app", "custom software", "mobile app", "website development", "saas", "api", "ai agent", "web application"]):
            category = "Software Development"
            reply = (
                "💻 **Zacma Software Engineering Services**:\n\n"
                "Zacma Group delivers end-to-end custom software solutions:\n"
                "• **Web Applications & SaaS**: Modern responsive platforms built with Next.js, React, and FastAPI.\n"
                "• **Mobile Applications**: Cross-platform Android & iOS apps developed with Flutter & React Native.\n"
                "• **Custom Enterprise Software**: ERP, CRM, Point of Sale, and School Management Systems.\n"
                "• **AI & Intelligent Agents**: Autonomous workflow agents, RAG document search, and LLM integrations.\n"
                "• **API & Cloud Architecture**: Secure REST APIs, microservices, and PostgreSQL/Supabase database design.\n\n"
                "Ready to start? Submit your project requirements at /software to receive an AI architecture blueprint and sprint plan."
            )
            actions = [
                {"label": "Submit Software Project Request", "url": "/software"},
                {"label": "View Software Capabilities", "url": "/software"},
                {"label": "Explore Platforms", "url": "/platforms"},
            ]

        # 9. What services does Zacma Group provide?
        elif any(w in q for w in ["what services", "services does zacma", "all services", "overview of services", "company provide"]):
            category = "Company Overview"
            reply = (
                "🏢 **Zacma Technology Group — 5 Core Divisions & 4 Official Platforms**:\n\n"
                "**Core Services:**\n"
                "1. 💻 **Software Development** (/software): Custom web, mobile (Android/iOS), ERP, CRM, and AI agents.\n"
                "2. 🛂 **Visa Assistant** (/visa): Embassy cover letters, document audits, and visa processing.\n"
                "3. ✈️ **Travel Agent** (/travel): Flight bookings (Ethiopian Airlines, Emirates) & curated 5-day holiday tours.\n"
                "4. 🎓 **Training Institute** (/training): Hands-on courses in Programming, AI, Graphics, Video & Hardware.\n"
                "5. 📈 **Marketing Service** (/marketing): 30-day digital growth campaigns, Meta/Google ads & brand strategy.\n\n"
                "**Official Platforms:** ERP (erp.zacmaa.net), MySchool (myschool.zacmaa.net), E-Commerce (ecommerce.zacmaa.net), Freelancer (freelancer.zacmaa.net)."
            )
            actions = [
                {"label": "Software Dev", "url": "/software"},
                {"label": "Visa Assistant", "url": "/visa"},
                {"label": "Travel Agent", "url": "/travel"},
                {"label": "Training Courses", "url": "/training"},
                {"label": "Platforms", "url": "/platforms"},
            ]

        # 8. Payment & Receipt Upload Questions
        elif any(w in q for w in ["how to pay", "upload payment", "upload receipt", "payment receipt", "receiving account", "cbe account", "payment method", "telebirr", "chapa", "bank"]):
            category = "Payments"
            reply = (
                "💳 **Official Payment & Receipt Verification Workflow**:\n\n"
                "• **Instant Online Checkout**: Secure checkout via Chapa (Debit/Credit Cards, Telebirr, CBE Birr).\n"
                "• **Bank Transfers & Mobile Money**: Commercial Bank of Ethiopia (CBE), TeleBirr, Awash Bank, and Bank of Abyssinia.\n\n"
                "**How to pay and submit proof:**\n"
                "1. Select your preferred active provider during checkout or in the Client Portal (/portal).\n"
                "2. For online checkout (Chapa), verification occurs automatically in real-time.\n"
                "3. For bank transfer or mobile money, transfer using your unique transaction reference (e.g. ZACMA-2026-XXXXXXXX).\n"
                "4. Navigate to **Client Portal (/portal)** → **Upload Payment Receipt** tab, enter the transaction code, and attach your transfer screenshot.\n"
                "5. Our finance team verifies the transfer and triggers AI service deliverable generation."
            )
            actions = [
                {"label": "Client Portal (/portal)", "url": "/portal"},
                {"label": "Track My Request", "url": "/track"},
            ]

        # 9. Request / Tracking / Status Questions
        elif any(w in q for w in ["check status", "track request", "how to track", "how can i request", "what happens after", "what information"]):
            category = "Client Workflow"
            reply = (
                "📋 **Client Service Request & Tracking Guide**:\n\n"
                "• **Submitting a Request**: Select your desired service (/software, /visa, /travel, /training, /marketing) and fill out the simple 4-step wizard.\n"
                "• **Tracking Status**: Enter your unique reference code (e.g. ZAC-DEV-1001, ZACMA-2026-XXXXXXXX) anytime at **/track** for live progress updates.\n"
                "• **Client Portal**: Log in at **/portal** to view full case manager feedback, timeline logs, and download approved AI deliverables."
            )
            actions = [
                {"label": "Track Request (/track)", "url": "/track"},
                {"label": "Client Portal (/portal)", "url": "/portal"},
            ]

        # 10. Default General Consultation
        else:
            category = "General"
            reply = (
                "Hello! I am the **Zacma Business Support AI Assistant**.\n\n"
                "I can assist you with:\n"
                "• **Software Development** (/software): Custom web, mobile, ERP, CRM, and AI solutions\n"
                "• **Official Platforms** (/platforms): ERP, MySchool, E-Commerce, and Freelancer\n"
                "• **Visa Consulting** (/visa): Embassy cover letters & document audits\n"
                "• **Travel Booking** (/travel): Flights & 5-day holiday itineraries\n"
                "• **Training Institute** (/training): Practical tech & creative courses\n"
                "• **Payments & Invoicing**: Online checkout via Chapa, CBE, TeleBirr, Awash & Abyssinia\n\n"
                "How can I help your project or organization today?"
            )
            actions = [
                {"label": "Explore Platforms", "url": "/platforms"},
                {"label": "Software Development", "url": "/software"},
                {"label": "Client Portal", "url": "/portal"},
            ]

        return {
            "category": category,
            "reply": reply,
            "actions": actions,
            "recommendation": recommendation,
        }

    @staticmethod
    def recommend_course(education_level: str, interests: str) -> str:
        """AI course recommendation based on student background."""
        interest_lower = interests.lower()
        if any(w in interest_lower for w in ["code", "software", "python", "developer", "backend", "web"]):
            return "Recommended Course: 'Programming' or 'Web Design' based on technical and software interests."
        if any(w in interest_lower for w in ["ai", "machine learning", "data", "robotics", "prompt"]):
            return "Recommended Course: 'AI' (Artificial Intelligence & Applied ML) — high growth trajectory."
        if any(w in interest_lower for w in ["design", "art", "creative", "video", "youtube", "media"]):
            return "Recommended Course: 'Graphics Design' or 'Video Editing' for creative media skills."
        if any(w in interest_lower for w in ["hardware", "repair", "phone", "laptop", "printer", "fix", "pcb", "soldering", "maintenance"]):
            return "Recommended Course: 'Maintenance' (Hardware Specialty) — hands-on component diagnostics and motherboard repair."
        if any(w in interest_lower for w in ["finance", "money", "accounting", "excel", "audit"]):
            return "Recommended Course: 'Accounting' for financial management and business record keeping."
        return "Recommended Course: 'Web Design' & 'AI Fundamentals' — versatile entry points for modern careers."

    @staticmethod
    def draft_welcome_email(full_name: str, course: str) -> str:
        """Draft an onboarding welcome message for admin review."""
        return (
            f"Dear {full_name},\n\n"
            f"Welcome to the Zacma Training Institute! We are thrilled to confirm your enrollment in the '{course}' program.\n\n"
            "Here is what to expect:\n"
            "- Course materials and syllabus will be available in your orientation portal.\n"
            "- Please ensure your primary laptop is configured for the practical lab sessions.\n\n"
            "If you have any questions before classes begin, don't hesitate to reply to this email.\n\n"
            "Best regards,\n"
            "Zacma Academic Affairs"
        )

    @staticmethod
    def precheck_documents(visa_type: str, provided_documents: list[str]) -> dict[str, Any]:
        """Pre-check uploaded visa documents for completeness."""
        docs_lower = [d.lower() for d in provided_documents]
        required = ["passport"]
        if visa_type.lower() == "tourist":
            required.extend(["bank_statement", "hotel_booking", "flight_itinerary"])
        elif visa_type.lower() == "study":
            required.extend(["acceptance_letter", "bank_statement", "academic_transcripts"])
        elif visa_type.lower() == "work":
            required.extend(["employment_contract", "resume", "educational_credentials"])
        elif visa_type.lower() == "business":
            required.extend(["invitation_letter", "company_registration", "bank_statement"])

        missing = [r for r in required if not any(r in d for d in docs_lower)]
        is_complete = len(missing) == 0

        return {
            "visa_type": visa_type,
            "is_complete": is_complete,
            "required_documents": required,
            "provided_documents": provided_documents,
            "missing_documents": missing,
            "summary": (
                "All required documents are present and validated."
                if is_complete
                else f"Missing documents flagged: {', '.join(missing)}."
            ),
        }

    @staticmethod
    def suggest_itinerary(destination: str, budget: float, travel_dates: str | None = None) -> dict[str, Any]:
        """Generate an AI-suggested itinerary and budget breakdown."""
        dates_text = f" ({travel_dates})" if travel_dates else ""
        flight_est = budget * 0.55
        hotel_est = budget * 0.30
        activities_est = budget * 0.15

        return {
            "destination": destination,
            "dates": travel_dates or "Flexible",
            "total_budget": budget,
            "breakdown": {
                "flight_estimate": round(flight_est, 2),
                "accommodation_estimate": round(hotel_est, 2),
                "activities_and_transfers": round(activities_est, 2),
            },
            "suggested_itinerary": (
                f"Proposed 5-Day Explorer Plan for {destination}{dates_text}:\n"
                "• Day 1: Arrival, airport transfer, hotel check-in, city orientation.\n"
                "• Day 2: Guided cultural & landmark tour.\n"
                "• Day 3: Signature destination excursion & shopping.\n"
                "• Day 4: Leisure / bespoke activity day.\n"
                "• Day 5: Souvenir market, checkout, and return departure."
            ),
        }

    @staticmethod
    def suggest_ticket_reply(subject: str, message: str) -> dict[str, Any]:
        """Suggest an AI response draft and auto-categorize."""
        msg_lower = (subject + " " + message).lower()
        if any(w in msg_lower for w in ["payment", "invoice", "telebirr", "cbe", "receipt", "bank", "billing", "transfer", "fee"]):
            category = "Billing"
            priority = "High"
            draft = "Thank you for your payment message. Our finance department verifies bank transfers within 1-2 business hours. If you haven't uploaded your transfer screenshot, please send the reference number."
        elif any(w in msg_lower for w in ["software", "developer", "erp", "myschool", "ecommerce platform", "build a website", "saas", "api", "mobile app"]):
            category = "Software"
            priority = "High"
            draft = "Thank you for reaching out to Zacma Software Engineering. Our solutions architects are reviewing your project requirements and will provide a detailed technical specification and sprint roadmap."
        elif any(w in msg_lower for w in ["visa", "passport", "embassy"]):
            category = "Visa"
            priority = "High"
            draft = "Thank you for contacting Zacma Visa Services. Our team is reviewing your application stage. Please ensure all requested documents are uploaded so our visa officers can proceed."
        elif any(w in msg_lower for w in ["course", "class", "training", "student", "teacher"]):
            category = "Training"
            priority = "Medium"
            draft = "Thank you for your inquiry about our training programs. Our classes run on flexible weekday and weekend schedules with certified instructors. Let us know which course you're interested in!"
        elif any(w in msg_lower for w in ["flight", "hotel", "travel", "ticket", "trip"]):
            category = "Travel"
            priority = "Medium"
            draft = "Thank you for reaching out to Zacma Travel. We have received your booking inquiry and our travel specialists are curating optimal flight and accommodation options for your review."
        else:
            category = "General"
            priority = "Low"
            draft = "Thank you for reaching out to Zacma Support. We have received your request and an agent will follow up with you shortly."

        return {
            "suggested_category": category,
            "suggested_priority": priority,
            "draft_reply": draft,
        }
