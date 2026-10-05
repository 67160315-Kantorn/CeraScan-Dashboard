"""
CeraScan — สร้างชุดข้อมูลสำหรับ Dashboard
------------------------------------------------
ข้อมูลโรงงานในไฟล์นี้เป็น "ข้อมูลจำลอง" (simulated) ของโรงงานกระเบื้องเซรามิกขนาดกลาง
สร้างขึ้นเพื่อใช้นำเสนอแนวคิดธุรกิจในรายวิชา Business Idea Creation
ค่าตั้งต้น (อัตราการตรวจพบของคน ~80%) อ้างอิงจากงานวิจัยที่ระบุใน data/references.csv

รัน:  python generate_data.py
ผลลัพธ์: data/*.csv และ data/data.js (ไฟล์ที่ Dashboard อ่าน)
"""
import csv, json, random, math
from datetime import date, timedelta
from pathlib import Path

random.seed(2026)
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

def write_csv(name, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

# ---------------------------------------------------------------
# 1) inspection_daily.csv — บันทึกการตรวจรายวัน 2 สายการผลิต 2 กะ 182 วัน
#    13 สัปดาห์แรก: ตรวจด้วยคนทั้ง 2 สาย (baseline)
#    13 สัปดาห์หลัง: Line A ใช้ CeraScan (AI + QC ยืนยัน 1 คน), Line B ตรวจด้วยคนเหมือนเดิม (กลุ่มควบคุม)
# ---------------------------------------------------------------
START = date(2026, 3, 2)          # วันจันทร์
DAYS = 182
PILOT_DAY = 91                     # เริ่ม pilot 1 มิ.ย. 2026
TILES_PER_SHIFT = 6000             # กระเบื้อง 60x60 ซม. ต่อกะ ต่อสาย
DEFECT_RATE = 0.025
MANUAL_DETECT = {"day": 0.81, "night": 0.74}
AI_DETECT_FINAL = 0.962
MANUAL_FALSE_REJECT = 0.012
AI_FALSE_REJECT = 0.0045

daily = []
for d in range(DAYS):
    dt = START + timedelta(days=d)
    for line in ("A", "B"):
        for shift in ("day", "night"):
            produced = int(random.gauss(TILES_PER_SHIFT, 180))
            true_def = max(0, int(random.gauss(produced * DEFECT_RATE, 12)))
            pilot = d >= PILOT_DAY
            ai = pilot and line == "A"
            if ai:
                # ช่วง 3 สัปดาห์แรกของ pilot โมเดลยังเรียนรู้จากข้อมูลหน้างาน
                ramp = min(1.0, (d - PILOT_DAY) / 21)
                p = 0.90 + (AI_DETECT_FINAL - 0.90) * ramp
                fr = 0.008 - (0.008 - AI_FALSE_REJECT) * ramp
                inspectors = 1
            else:
                p = MANUAL_DETECT[shift]
                fr = MANUAL_FALSE_REJECT * (1.1 if shift == "night" else 1.0)
                inspectors = 4
            p = min(0.995, max(0.5, random.gauss(p, 0.012)))
            caught = round(true_def * p)
            good = produced - true_def
            false_rej = max(0, round(random.gauss(good * fr, 6)))
            daily.append({
                "date": dt.isoformat(),
                "week": d // 7 + 1,
                "line": line,
                "shift": shift,
                "phase": "pilot" if pilot else "baseline",
                "method": "ai_assisted" if ai else "manual",
                "tiles_inspected": produced,
                "true_defects": true_def,
                "defects_caught": caught,
                "defects_escaped": true_def - caught,
                "false_rejects": false_rej,
                "inspectors": inspectors,
            })
write_csv("inspection_daily.csv", daily)

# ---------------------------------------------------------------
# 2) defect_breakdown.csv — ตำหนิแต่ละประเภท: สัดส่วน, อัตราตรวจพบของคน vs AI (ชุดทดสอบจำลอง)
# ---------------------------------------------------------------
defects = [
    # th, en, share, manual, ai_recall, ai_precision, test_images
    ("รอยร้าว", "Crack", 0.18, 0.86, 0.975, 0.962, 1200),
    ("ขอบบิ่น", "Edge chip", 0.22, 0.89, 0.981, 0.970, 1450),
    ("รูเข็มบนผิวเคลือบ", "Glaze pinhole", 0.20, 0.63, 0.934, 0.915, 1300),
    ("สีเพี้ยน/เฉดไม่ตรง", "Shade variation", 0.15, 0.70, 0.941, 0.902, 1000),
    ("จุดด่าง/คราบ", "Spot / stain", 0.15, 0.79, 0.958, 0.944, 980),
    ("แผ่นโก่ง/บิด", "Warpage", 0.10, 0.76, 0.872, 0.880, 640),
]
write_csv("defect_breakdown.csv", [{
    "defect_th": a, "defect_en": b, "share_of_defects": c,
    "manual_detect_rate": m, "ai_recall": r, "ai_precision": p, "test_images": n,
} for a, b, c, m, r, p, n in defects])

# ---------------------------------------------------------------
# 3) shift_fatigue.csv — ความแม่นยำการตรวจตามชั่วโมงในกะ (8 ชม.)
# ---------------------------------------------------------------
fatigue = []
for h in range(1, 9):
    manual = 0.87 - 0.019 * (h - 1) - 0.0015 * (h - 1) ** 2
    fatigue.append({"hour_of_shift": h,
                    "manual_accuracy": round(manual, 3),
                    "ai_accuracy": round(0.962 + random.uniform(-0.004, 0.004), 3)})
write_csv("shift_fatigue.csv", fatigue)

# ---------------------------------------------------------------
# 4) roi_assumptions.csv — สมมติฐานต้นทุน/ผลตอบแทน ต่อ 1 สายการผลิต (ปรับได้ใน Dashboard)
# ---------------------------------------------------------------
roi = [
    ("tiles_per_day", 12000, "แผ่น/วัน", "กำลังผลิตต่อสาย (2 กะ)"),
    ("working_days", 330, "วัน/ปี", "วันทำงานต่อปี"),
    ("defect_rate", 0.025, "สัดส่วน", "อัตราตำหนิจริงในสายการผลิต"),
    ("manual_detect", 0.775, "สัดส่วน", "อัตราตรวจพบของคน (เฉลี่ยกะเช้า+ดึก)"),
    ("ai_detect", 0.96, "สัดส่วน", "อัตราตรวจพบของ CeraScan"),
    ("escape_cost", 120, "บาท/แผ่น", "ต้นทุนเมื่อของเสียหลุดถึงลูกค้า (เคลม ขนส่ง เปลี่ยนสินค้า)"),
    ("tile_value", 90, "บาท/แผ่น", "มูลค่ากระเบื้องเกรด A 1 แผ่น"),
    ("false_reject_loss", 0.4, "สัดส่วน", "มูลค่าที่เสียเมื่อของดีถูกตีตก (ลดเกรด)"),
    ("manual_false_reject", 0.0125, "สัดส่วน", "อัตราตีตกผิดของคน"),
    ("ai_false_reject", 0.0045, "สัดส่วน", "อัตราตีตกผิดของ CeraScan"),
    ("inspectors_saved", 6, "คน", "พนักงานตรวจที่ย้ายไปทำงานอื่นได้ (8 → 2 คน/วัน)"),
    ("salary", 15000, "บาท/เดือน", "ค่าแรงพนักงานตรวจ"),
    ("system_price", 1500000, "บาท", "ค่าระบบ + ติดตั้ง ต่อสาย (ครั้งเดียว)"),
    ("subscription", 30000, "บาท/เดือน", "ค่าซอฟต์แวร์ + บำรุงรักษา ต่อสาย"),
]
write_csv("roi_assumptions.csv", [{"key": k, "value": v, "unit": u, "description": d} for k, v, u, d in roi])

# ---------------------------------------------------------------
# 5) business_projection.csv — ประมาณการรายได้ CeraScan 3 ปี (สมมติฐาน)
# ---------------------------------------------------------------
proj = []
cum_lines = 0
for year, new_lines, consult in ((2027, 2, 0.3e6), (2028, 8, 1.2e6), (2029, 20, 3.0e6)):
    prev = cum_lines
    cum_lines += new_lines
    avg_active = prev + new_lines / 2
    proj.append({
        "year": year, "new_lines": new_lines, "active_lines_end": cum_lines,
        "install_revenue": int(new_lines * 1_500_000),
        "subscription_revenue": int(avg_active * 30000 * 12),
        "custom_consulting_revenue": int(consult),
    })
write_csv("business_projection.csv", proj)

# ---------------------------------------------------------------
# 6) references.csv — แหล่งข้อมูลจริงที่ใช้อ้างอิง
# ---------------------------------------------------------------
refs = [
    ("Sandia National Laboratories (See, J.E., 2015) Visual Inspection Reliability for Precision Manufactured Parts",
     "ค่าเฉลี่ยอุตสาหกรรมของการตรวจด้วยสายตาคนพบตำหนิราว 80%",
     "https://www.sandia.gov/research/publications/details/visual-inspection-reliability-for-precision-manufactured-parts-2015-12-01/"),
    ("Sundaram & Zeid (2023), Micromachines — สรุปโดย Food Industry Executive (2026)",
     "คนตรวจเฉลี่ยราว 80% ส่วนโมเดล deep learning ทำได้ถึง 99.86% ในการทดสอบแบบควบคุม",
     "https://foodindustryexecutive.com/2026/05/ai-food-manufacturing-plant-floor-applications-limits/"),
    ("Technavio — AI Visual Inspection System Market 2025-2029",
     "ตลาดระบบ AI ตรวจคุณภาพด้วยภาพคาดว่าโตเพิ่ม 26.84 พันล้านดอลลาร์ CAGR 38.8% (2024-2029)",
     "https://www.technavio.com/report/ai-visual-inspection-system-market-industry-analysis"),
    ("SCG Ceramics — Company history",
     "กำลังการผลิต 94 ล้าน ตร.ม./ปี ส่วนแบ่งตลาด 58% (ข้อมูล มี.ค. 2018)",
     "https://scgceramics.com/en/about-us-scg-ceramics/company-history/"),
]
write_csv("references.csv", [{"source": s, "key_finding": k, "url": u} for s, k, u in refs])

# ---------------------------------------------------------------
# data.js — รวมทุกอย่างให้ Dashboard เปิดได้ทันทีโดยไม่ต้องมีเซิร์ฟเวอร์
# ---------------------------------------------------------------
def read(name):
    with open(OUT / name, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            try:
                r[k] = int(v)
            except ValueError:
                try:
                    r[k] = float(v)
                except ValueError:
                    pass
    return rows

bundle = {n.replace(".csv", ""): read(n) for n in (
    "inspection_daily.csv", "defect_breakdown.csv", "shift_fatigue.csv",
    "roi_assumptions.csv", "business_projection.csv", "references.csv")}
bundle["meta"] = {"pilot_start": (START + timedelta(days=PILOT_DAY)).isoformat(),
                  "pilot_week": PILOT_DAY // 7 + 1}
with open(OUT / "data.js", "w", encoding="utf-8") as f:
    f.write("// สร้างอัตโนมัติจาก generate_data.py — อย่าแก้ไฟล์นี้โดยตรง\n")
    f.write("window.CERASCAN_DATA = " + json.dumps(bundle, ensure_ascii=False) + ";\n")
print("done:", len(daily), "daily rows")
