# Sprint 2 — Back-End Business Logic & Data Access

**Goal:** OOP, Core gameplay, persistence, CRUD + search/filter/sort. **Reference schedule:** นำเสนอ 22–23 กันยายน 2569 / ส่ง 25 กันยายน 2569.

## Planning

Refactor mini-project `Board` ไป `battleship.py` ใหม่ แยก `Board` (domain), `BattleshipGame` (turn controller), `RecordStore` (record operations), `api` (JSON bridge). Data Access ผ่าน localStorage/JSON file ใน browser แทน filesystem server-side (GitHub Pages ไม่มี Python backend). DoD: มี unit tests ครอบคลุมเงื่อนไขสำคัญและ persist score/game ใน browser ได้ตาม implementation.

## Data structures / algorithm choices

| Concept | Implementation | Reason |
|---|---|---|
| 2D list | `Board.grid` 10×10 | เข้าถึง `[row][col]` ตรงไปตรงมา |
| Dictionary/list | `SHIP_SPECS`, `ships` | อธิบายชนิด/ความยาว/กำลังยิงได้ |
| Set | `shots_history` | ป้องกันยิงซ้ำ, membership โดยเฉลี่ย O(1) |
| List comprehension | available AI targets | ไม่เลือกซ้ำ, ไม่มี infinite retry |
| Search/filter | `RecordStore.query` | ค้นชื่อแบบ casefold + filter result |
| Sorting | `sorted()` | เรียงตาม date/turns โดยไม่เปลี่ยนข้อมูลหลัก |
| Persistence | `dump/load`, browser localStorage | เก็บ state JSON และ validate ก่อนกู้ข้อมูล |

**CRUD implementation:** Create = `records_add`, Read = `records_query`, Update = `records_rename`, Delete = `records_delete` — ใช้ ID ที่ไม่ซ้ำ แยก record ออกจากเกมปัจจุบัน.

## Execution

- รักษาเรือเดิมทั้ง 6 แบบและ shots 2+2+2+2+1+1 = 10.
- ตรวจ `can_place`, `receive_shot`, `total_shots`, `all_sunk`, `auto_place`, `shoot`.
- เขียน `Board.load()` สร้างกระดานใหม่จากตำแหน่งเรือและ replay `shots_history` เพื่อตรวจความสอดคล้องของ Grid.
- เพิ่ม `RecordStore` สำหรับ CRUD / search / filter / sort; JSON file import/export ทำที่ frontend.

## Review / Test evidence

| Case | Expected | Automated evidence |
|---|---|---|
| BL-01 | ไม่สร้างกระดาน 2D แบบ shared rows | `test_separate_rows` PASSED |
| BL-02 | จมเรือ 1×1 ลดกำลังยิง 2 | `test_sink_decreases_shots` PASSED |
| BL-03 | เกมโหลดจาก JSON ได้ | `test_save_load` PASSED |
| BL-04 | JSON board ถูกแก้ไขแล้ว reject | `test_board_roundtrip_and_tamper` PASSED |
| BL-05 | record CRUD/search/filter/sort | `test_crud_filter_sort` PASSED |

**Wow:** กติกาเกมทดสอบได้ด้วย Python มาตรฐานโดยไม่ต้องเปิดหน้าเว็บ. **Whoops:** Python tuple เปลี่ยนเป็น list เมื่อผ่าน JSON และตอนโหลดต้อง normalize geometry ก่อนเปรียบเทียบ; พบและแก้ไขระหว่างทดสอบ. **Handoff → Sprint 3:** `api(JSON string) → JSON string`, ไม่มี dependency เพิ่มใน engine.
