# Sprint 3 — Full-Stack Integration

**Goal:** เชื่อม Python back-end เข้ากับ HTML/CSS/JS front-end, synchronize state และรองรับ edge cases. **Reference schedule:** นำเสนอ 29–30 กันยายน 2569 / ส่ง 2 ตุลาคม 2569.

## Planning & integration contract

- `index.html` โหลด Pyodide จาก CDN; `app.js` fetch `./battleship.py` แล้วรัน `import battleship` ใน virtual Python filesystem.
- JS ส่ง JSON request ผ่าน global variable `web_request` และ Python `api()` คืน JSON response.
- Browser render เฉพาะ `game.view()` ซึ่งทำ masking เรือฝ่ายตรงข้ามก่อนส่งให้ JS.
- Data access: auto-save หลัง mutation, restore ตอนเริ่มหน้าเว็บ, JSON export/import.

```text
Browser button → JS event → JSON request → Python api → Board/Game/RecordStore
      ↑                                   ↓
   render(state) ← JSON response ← business rules
      ↓
  localStorage / downloaded JSON backup
```

## Execution and consistency

- Flow: `new → place × 6` (หรือ auto) `→ shoot × shots_left → computer shoots → next turn → finished`.
- เมื่อเรือลำใดจม shots ของฝ่ายนั้นจะลดในเทิร์นถัดไป.
- UI ปิดปุ่มตอนยังไม่ใช่ phase ที่เหมาะสม; Python guard ซ้ำเพื่อไม่ให้ bypass ผ่าน API.
- Import JSON จำกัดไฟล์ 300 KB, ตรวจชนิดและ schema และพยายาม rollback state ถ้า records validation ไม่ผ่าน.
- Score records เก็บหลังเกมจบ; CRUD update จะแสดงรายการและ sync browser storage ใหม่.

## Edge cases / QA report

| ID | Observation / Input | Expected | Actual evidence |
|---|---|---|---|
| INT-01 | ยิงตำแหน่งซ้ำ | ไม่ให้ยิง | `test_sink_decreases_shots` PASSED |
| INT-02 | AI ยิงครบเทิร์น | ไม่ยิงซ้ำ, เปลี่ยน turn | `test_autoplace_and_no_shot_duplicates` PASSED |
| INT-03 | อ่าน enemy board ระหว่าง setup | ไม่เปิดเผยเรือ | `test_no_enemy_reveal` PASSED |
| INT-04 | API ไม่รู้จักคำสั่ง | คืน `{ok:false}` ไม่ throw | `test_api_invalid` PASSED |
| INT-05 | ปิด/เปิดหน้าเว็บ | โหลด auto-save | Implementation done, browser persistence manual test pending |
| INT-06 | ไฟล์ import ผิดรูปแบบ | แสดง error, ไม่ crash | Implementation done, browser E2E manual test pending |

**Wow:** ทำให้ business logic ยังคงเป็น Python จริงและ deploy เป็นไฟล์ static ได้. **Whoops:** GitHub Pages ไม่รองรับเซิร์ฟเวอร์ Python; เลือก Pyodide แทน Flask และปรับ persistence จาก server files เป็น browser localStorage. **Limitation:** ข้อมูลคะแนนไม่ซิงก์ข้ามเบราว์เซอร์ และยังไม่ได้ทดสอบ URL deploy จริง.

**Handoff → Final Sprint:** automated tests, static asset build, GitHub Pages deployment workflow และ demo script.
