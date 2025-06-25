from fpdf import FPDF
from pathlib import Path
from components.plan_data import TravelPlan

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        font_path = Path(__file__).parent / "NanumGothic.ttf"
        self.add_font("Nanum", "", str(font_path), uni=True)
        self.set_font("Nanum", size=12)

def generate_schedule_pdf(route: TravelPlan, user_id: str):
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    filename = static_dir / f"schedule_{user_id}.pdf"

    # 여행 날짜 범위 계산
    start_date = route.plans[0].date if route.plans else ""
    end_date = route.plans[-1].date if route.plans else ""
    location = "제주"  # 필요 시 route.location 사용

    title_text = f"여행일정"

    pdf = PDF()
    pdf.add_page()

    # 상단 제목
    pdf.set_font("Nanum", size=14)
    pdf.cell(0, 10, txt=title_text, ln=True, align="C")
    pdf.ln(5)

    # 날짜 + 장소 이름만 출력
    pdf.set_font("Nanum", size=12)
    for day in route.plans:
        pdf.cell(0, 8, txt=f"{day.date}", ln=True)
        for place in day.place_to_visit:
            pdf.cell(0, 8, txt=f"- {place.name}", ln=True)
        pdf.ln(4)

    pdf.output(str(filename))
    return str(filename)


