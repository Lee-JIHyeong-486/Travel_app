from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from components.plan_data import get_plan_by_id, TravelPlan
from modules.common.export_pdf import generate_schedule_pdf

router = APIRouter()

@router.get("/download_plan_pdf")
async def download_plan_pdf(plan_id: str):
    plan_dict = await get_plan_by_id(plan_id)
    if not plan_dict:
        raise HTTPException(status_code=404, detail="Plan not found")

    travel_plan = TravelPlan(**plan_dict["travel_plan"])
    pdf_path = generate_schedule_pdf(route=travel_plan, user_id=travel_plan.user_id)

    # ✅ 사용자 다운로드용 파일명 생성
    location = plan_dict.get("location", "여행지")
    start = plan_dict.get("startDate", "")
    end = plan_dict.get("endDate", "")
    download_filename = f"여행일정({location}, {start}~{end}).pdf"

    return FileResponse(
        path=pdf_path,
        filename=download_filename,
        media_type="application/pdf",
        headers={"Access-Control-Allow-Origin": "*"}
    )
