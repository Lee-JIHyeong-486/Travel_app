from fpdf import FPDF
import os

def generate_schedule_pdf(filename, destination, days, schedule: list):
    pdf = FPDF()
    pdf.add_page()

    # ✅ 폰트 경로 (실행 경로에 따라 상대 경로 대응)
    font_path = "BackEnd/public/NanumGothic.ttf"
    if not os.path.exists(font_path):
        font_path = "fonts/NotoSansCJKjp-Regular.otf"  # fallback
    pdf.add_font("NanumGothic", "", font_path, uni=True)
    pdf.set_font("NanumGothic", "", 12)

    # ✅ 기본 정보
    pdf.cell(200, 10, txt=f"여행지: {destination}", ln=True)
    pdf.cell(200, 10, txt=f"여행 기간: {days}일", ln=True)
    pdf.ln(10)

    # ✅ 일정 출력
    for day in schedule:
        pdf.set_font("NanumGothic", "B", 11)
        pdf.cell(200, 10, txt=f"📅 {day.get('date', '')}", ln=True)
        pdf.set_font("NanumGothic", "", 10)

        for idx, place in enumerate(day.get("place_to_visit", []), 1):
            name = place.get("name", "알 수 없음")
            time_info = place.get("time", f"{9 + idx}:00")
            description = place.get("description", "설명 없음")
            concept = ", ".join(place.get("concept", []))

            pdf.cell(200, 8, txt=f"🕒 {time_info} - {name} ({concept})", ln=True)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(0, 6, txt=f"   {description}")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

        pdf.ln(5)

    # ✅ 저장
    path = os.path.join("BackEnd", "routes", "temp", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pdf.output(path)
    return path
