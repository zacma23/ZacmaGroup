from fastapi import APIRouter, Depends, HTTPException, status

from app.core.db import supabase
from app.core.demo_data import courses_store
from app.core.tenancy import get_tenant_id
from app.models import CourseCreate, CourseUpdate

TRAINING_COURSE_STRUCTURE = [
    {"id": "basic_computer", "name": "Basic Computer", "category": "General IT", "description": "Fundamentals of computing, Windows OS, Office Suite & Internet skills."},
    {"id": "graphics", "name": "Graphics", "category": "Design", "description": "Photoshop, Illustrator, vector branding & visual communication."},
    {"id": "video_editing", "name": "Video Editing", "category": "Media", "description": "Premiere Pro, DaVinci Resolve, video transitions & color grading."},
    {"id": "videography", "name": "Videography", "category": "Media", "description": "Studio camera setups, commercial videography & lighting."},
    {"id": "photography", "name": "Photography", "category": "Media", "description": "DSLR photography, studio lighting & professional portraiture."},
    {"id": "ai", "name": "AI", "category": "Emerging Tech", "description": "Artificial Intelligence, LLM prompting & automation pipelines."},
    {"id": "cloud_computing", "name": "Cloud Computing", "category": "Cloud & Infra", "description": "AWS, Docker containerization, Azure & DevOps basics."},
    {"id": "spoken_english", "name": "Spoken English", "category": "Languages", "description": "Workplace English communication, presentation skills & fluency."},
    {"id": "accounting", "name": "Accounting", "category": "Business", "description": "Financial accounting principles, computerized accounting & payroll."},
    {"id": "it_support", "name": "IT Support", "category": "Technical", "description": "Helpdesk diagnostics, OS installation & enterprise hardware support."},
    {"id": "autocad", "name": "AutoCAD", "category": "Engineering", "description": "2D Drafting, architectural layouts & 3D CAD modeling."},
    {"id": "etabs", "name": "ETABS", "category": "Engineering", "description": "Structural analysis, concrete & steel building design."},
    {"id": "web_design", "name": "Web Design", "category": "Software", "description": "HTML5, Tailwind CSS, JavaScript & modern responsive design."},
    {"id": "networking", "name": "Networking", "category": "Technical", "description": "Cisco routing, switching, IP subnetting & network security."},
    {
        "id": "maintenance",
        "name": "Maintenance",
        "category": "Hardware & Repair",
        "description": "Component-level hardware diagnostics, device repair & maintenance.",
        "specialties": [
            {
                "id": "hardware_specialty",
                "name": "Hardware Specialty",
                "description": "Component diagnostics, motherboard repair, chip soldering, hardware assembly & firmware flashing.",
                "schedules": [
                    {
                        "id": "sch_1",
                        "label": "Monday + Wednesday + Thursday",
                        "days": ["Monday", "Wednesday", "Thursday"],
                    },
                    {
                        "id": "sch_2",
                        "label": "Tuesday + Thursday + Saturday",
                        "days": ["Tuesday", "Thursday", "Saturday"],
                    },
                    {
                        "id": "sch_3",
                        "label": "Saturday + Sunday",
                        "days": ["Saturday", "Sunday"],
                    },
                ],
                "time_slots": [
                    "03:00 – 05:00",
                    "05:00 – 07:00",
                    "07:00 – 09:00",
                    "09:00 – 11:00",
                    "11:00 – 01:00",
                    "12:00 – 02:00",
                ],
            }
        ],
    },
]


router = APIRouter(prefix="/training", tags=["training"])


# ---------------------------------------------------------------------------
# STRUCTURE
# ---------------------------------------------------------------------------
@router.get("/structure")
def get_training_structure():
    """Return the official hierarchical Zacma Training Course & Specialty structure."""
    return TRAINING_COURSE_STRUCTURE


# ---------------------------------------------------------------------------
# LIST
# ---------------------------------------------------------------------------
@router.get("/courses")
def list_courses(tenant_id: str = Depends(get_tenant_id)):
    if supabase is None:
        return courses_store.list_all(tenant_id)
    result = supabase.table("courses").select("*").eq("tenant_id", tenant_id).execute()
    return result.data


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------
@router.post("/courses", status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, tenant_id: str = Depends(get_tenant_id)):
    data = payload.model_dump()
    if supabase is None:
        return courses_store.create(data, tenant_id)
    data["tenant_id"] = tenant_id
    result = supabase.table("courses").insert(data).execute()
    return result.data


# ---------------------------------------------------------------------------
# GET BY ID
# ---------------------------------------------------------------------------
@router.get("/courses/{course_id}")
def get_course(course_id: str, tenant_id: str = Depends(get_tenant_id)):
    if supabase is None:
        record = courses_store.get(course_id, tenant_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return record
    result = (
        supabase.table("courses")
        .select("*")
        .eq("id", course_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return result.data[0]


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------
@router.put("/courses/{course_id}")
def update_course(course_id: str, payload: CourseUpdate, tenant_id: str = Depends(get_tenant_id)):
    updates = payload.model_dump(exclude_unset=True)
    if supabase is None:
        record = courses_store.update(course_id, updates, tenant_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return record
    result = (
        supabase.table("courses")
        .update(updates)
        .eq("id", course_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return result.data[0]


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------
@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: str, tenant_id: str = Depends(get_tenant_id)):
    if supabase is None:
        deleted = courses_store.delete(course_id, tenant_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return
    result = (
        supabase.table("courses")
        .delete()
        .eq("id", course_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
