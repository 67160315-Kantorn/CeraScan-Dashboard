# CeraScan — Dashboard เชิงเล่าเรื่อง: AI ตรวจจับตำหนิผลิตภัณฑ์เซรามิก

Mini Project (Week 11) รายวิชา **Business Idea Creation** — กลุ่มอุตสาหกรรมเซรามิก

## รายชื่อกลุ่ม

| ชื่อ-นามสกุล | รหัสนักศึกษา |
|---|---|
| กันต์ธร ใจใหญ่ | 67160315 |

## เปิดดู Dashboard

- **ออนไลน์:** เปิด GitHub Pages ของ repository นี้ (Settings → Pages → Branch `main` / root)
- **ในเครื่อง:** ดับเบิลคลิก `index.html` ได้เลย ไม่ต้องติดตั้งอะไร (Chart.js อยู่ใน `assets/` แล้ว จึงเปิดได้แม้ไม่มีอินเทอร์เน็ต)
- **ตอนนำเสนอ:** กดลูกศร ← → หรือ PageUp/PageDown เพื่อเลื่อนไปทีละบท

## เรื่องที่ Dashboard เล่า

| บท | คำถาม | สิ่งที่แสดง |
|---|---|---|
| 1. ปัญหา | ทำไมการตรวจด้วยคนไม่พอ | อัตราตรวจพบ ~77% ลดลงตามชั่วโมงในกะ ตำหนิเล็กอย่างรูเข็มและสีเพี้ยนตรวจพบยากที่สุด |
| 2. ทางแก้ | CeraScan ทำงานอย่างไร | กล้องอุตสาหกรรม → AI ตีกรอบตำหนิ → คัดแยกอัตโนมัติ → QC ยืนยันเคสก้ำกึ่ง → รายงานคุณภาพ |
| 3. หลักฐาน | รู้ได้อย่างไรว่าทำได้ | Pilot แบบมีกลุ่มเปรียบเทียบ (สาย A ใช้ AI / สาย B ใช้คน) และงานวิจัยอ้างอิง |
| 4. ทำอย่างไร | จะทำให้เกิดขึ้นจริงอย่างไร | แผน 12 เดือน และ 4M (Man, Machine, Material, Method) |
| 5. โอกาสธุรกิจ | คุ้มไหม ใครจ่าย | ขนาดตลาด, เครื่องคำนวณจุดคืนทุนของโรงงาน (ปรับค่าได้), ประมาณการรายได้ 3 ปี |
| 6. ข้อเสนอแนะ | ควรทำอะไรต่อ | ข้อเสนอสำหรับโรงงานและสำหรับทีม CeraScan |

## โครงสร้าง Repository

```
├── index.html              Dashboard
├── assets/chart.umd.js     ไลบรารีกราฟ Chart.js 4.4.1
├── data/
│   ├── inspection_daily.csv     บันทึกการตรวจรายวัน (728 แถว)
│   ├── defect_breakdown.csv     ประเภทตำหนิ: สัดส่วน, อัตราตรวจพบคน vs AI
│   ├── shift_fatigue.csv        ความแม่นยำตามชั่วโมงในกะ
│   ├── roi_assumptions.csv      สมมติฐานต้นทุน/ผลตอบแทนต่อ 1 สายการผลิต
│   ├── business_projection.csv  ประมาณการรายได้ 3 ปี
│   ├── references.csv           แหล่งข้อมูลจริงที่อ้างอิง
│   └── data.js                  ข้อมูลทั้งหมดรวมให้ Dashboard อ่าน (สร้างอัตโนมัติ)
└── generate_data.py        สคริปต์สร้างข้อมูล
```

## ที่มาของข้อมูล

**ข้อมูลโรงงานเป็นข้อมูลจำลอง (simulated)** ของโรงงานกระเบื้องขนาดกลาง 2 สายการผลิต สายละ 12,000 แผ่น/วัน ช่วง 2 มี.ค. – 30 ส.ค. 2026 สร้างเพื่อนำเสนอแนวคิดธุรกิจ โดยตั้งค่าเริ่มต้นให้สอดคล้องกับงานวิจัย (คนตรวจพบตำหนิเฉลี่ยราว 80%) ข้อมูลตลาดเป็นข้อมูลจริงจากแหล่งอ้างอิงใน `data/references.csv`

แก้สมมติฐานใน `generate_data.py` แล้วรัน `python generate_data.py` เพื่อสร้างข้อมูลใหม่ได้

### คำอธิบายคอลัมน์ `inspection_daily.csv`

| คอลัมน์ | ความหมาย |
|---|---|
| date, week | วันที่ และสัปดาห์ที่ (1–26) |
| line | สายการผลิต A หรือ B |
| shift | กะ day / night |
| phase | baseline (13 สัปดาห์แรก) หรือ pilot (13 สัปดาห์หลัง) |
| method | manual = คนตรวจ, ai_assisted = CeraScan + QC 1 คน |
| tiles_inspected | จำนวนแผ่นที่ตรวจ |
| true_defects | จำนวนแผ่นที่มีตำหนิจริง |
| defects_caught / defects_escaped | ตำหนิที่ตรวจพบ / ที่หลุดออกไป |
| false_rejects | แผ่นดีที่ถูกตีตกผิด |
| inspectors | จำนวนพนักงานตรวจในกะนั้น |

## แหล่งอ้างอิง

1. Sandia National Laboratories (See, J.E., 2015). *Visual Inspection Reliability for Precision Manufactured Parts.*
2. Sundaram, S. & Zeid, A. (2023). *Micromachines* — สรุปโดย Food Industry Executive (2026)
3. Technavio. *AI Visual Inspection System Market 2025–2029.*
4. SCG Ceramics. *Company history.*
