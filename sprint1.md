# Sprint 1 — Front-End App Development

**Goal:** จาก CLI menu/print-based UI เปลี่ยนเป็น browser UI ที่รองรับ input validation และการเล่นผ่านเมาส์/สัมผัส. **Reference schedule:** นำเสนอ 15–16 กันยายน 2569 / ส่ง 18 กันยายน 2569 (วันตามเอกสารรายวิชา; มิใช่การอ้างว่าทำเสร็จทันกำหนด)

## Planning

- กำหนด UX flows: Loading → Place fleet → Battle → Result → New/Restore.
- สร้าง `index.html`, `style.css` และ `app.js` ในเลเยอร์ Presentation.
- DoD: ผู้ใช้เห็นกระดาน 10×10 ทั้งสองฝั่ง, ปุ่มวางเรือ/เริ่มใหม่, แสดงคำสั่ง, ไม่เปิดเผยเรือศัตรู และหน้าจอเล็กใช้งานได้.

## Execution

- สร้าง HTML semantics, aria labels, loading/status messages และตัวกรองประวัติ.
- ใช้ CSS Grid แสดง 10×10 พร้อม header พิกัด และ responsive design.
- Event handlers ส่ง action เป็น JSON ไปยัง Python engine; UI ไม่แตะ business rules.
- Validation ฝั่ง business รับพิกัด 0–9 เท่านั้น; ป้องกันซ้อน/เกินขอบ และ disable ปุ่มตาม phase.

## Review / Test cases

| Case | Input / Action | Expected | Evidence |
|---|---|---|---|
| UI-01 | แสดงหน้าเว็บ | กระดานสองแผง 10×10 | markup + renderer `app.js` (ยังไม่ผ่าน visual E2E browser) |
| UI-02 | วางเรือทะลุขอบ | ปฏิเสธ, ไม่พัง | `test_placement_boundary_overlap_and_negative` PASSED |
| UI-03 | วางเรือทับช่องเก่า | ปฏิเสธ | `test_placement_boundary_overlap_and_negative` PASSED |
| UI-04 | การคลิกยิงใน phase setup | ไม่ยิง | action gating ใน `app.js` + Python `shoot` guard (review; ยังไม่ผ่าน E2E) |

## Sprint retrospective

**Wow:** เห็นกระดานทั้งสองฝั่งและสถานะเทิร์นได้ในหน้าเดียว ไม่ต้องป้อนคำสั่งแถว/คอลัมน์ด้วยมือ. **Whoops:** เดิม `input()` และ `print()` เชื่อมกับ browser โดยตรงไม่ได้ จึงแยก UI ออกจาก Python และใช้ JSON API. **Follow-up:** browser-based visual verification บน GitHub Pages ต้องทำหลัง push.

**Handoff → Sprint 2:** frontend ส่ง `action`, `row`, `col`; Python engine รับและส่ง `game`, `save`, `records`, `filtered`.
