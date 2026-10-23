# Sprint Final — CI/CD, DevOps & Automation

**Goal:** เตรียม source code, automated tests, GitHub Actions และ deployment ไป GitHub Pages. **Reference schedule:** นำเสนอ 6–7 ตุลาคม 2569 / ส่ง 16 ตุลาคม 2569.

## DevOps architecture

```text
GitHub push (main) / PR
  └─ test job
      ├─ Python 3.12 compileall
      ├─ python -m unittest discover -s tests -v
      └─ node --check app.js
            └─ success + push(main) → deploy job
                ├─ configure-pages
                ├─ static _site (index.html, style.css, app.js, battleship.py)
                ├─ upload-pages-artifact
                └─ deploy-pages → GitHub Pages URL
```

**Source of truth:** `.github/workflows/pages.yml`; `PR` runs tests but does **not** deploy; `push main` and manual workflow trigger can deploy. Site has no server-side Python runtime; Pyodide loads in client browser.

## Automated test report

Executed locally in working environment with `python -m unittest discover -s tests -v`; **9 tests passed**. `node --check app.js` completed successfully. These are local test results; GitHub Actions and browser E2E deploy evidence is pending until the owner pushes repository.

| Test | Result |
|---|---|
| 2D grid independence | PASS |
| boundary / overlap / negative input | PASS |
| sink and firepower; duplicate shot | PASS |
| JSON board roundtrip / tampering | PASS |
| auto-placement + turn + duplicate prevention | PASS |
| enemy secrecy | PASS |
| save/load game state | PASS |
| invalid API | PASS |
| score CRUD + search/filter/sort | PASS |

## AI/Automation integration

**Implemented:** AI opponent is a seeded random algorithm that selects from never-targeted coordinates and calculates shot count based on surviving ships; this is an *automated opponent*, not a machine-learning model. GitHub Actions automates tests and deploy. Lessons from AI prompt use in original mini project are preserved in `legacy/LEARNINGLOG.md`. **Future scope:** smart hunt/target opponent, difficulty selection, optional AI insights via safe server gateway (not currently present).

## Deployment checklist

- [x] static assets in repository root
- [x] Python-based game engine (Pyodide-compatible)
- [x] Actions workflow defined
- [x] local unit tests and JS syntax check pass
- [ ] User creates/pushes GitHub repository
- [ ] Configure Settings → Pages → GitHub Actions
- [ ] Actual GitHub Actions green check verified
- [ ] Actual web URL verified on desktop and mobile
- [ ] Screenshot/demo/PR evidence collected

## Five-part presentation talking points

1. **Problem / architecture (20%)** — CLI Battleship → accessible shareable browser game; separation into 3 layers.
2. **Stack (10%)** — Python OOP, browser Pyodide, JS UI, JSON/localStorage, GitHub CI/CD.
3. **Live demo (40%)** — Place (manual and auto), shoot, sink, change shots, computer attacks, win/lose, refresh, records CRUD, filters, backup.
4. **Technical comparison (15%)** — stdout vs DOM; Python server unavailable on Pages; JSON replay validation vs blindly restoring grid.
5. **DevOps & automation (15%)** — CI workflow, unit test logs, build, deployment, random AI behavior + future smarter opponent.

## Retrospective

**Wow:** deployment pipeline tests Python domain logic before publishing and keeps repository static / low-cost. **Whoops:** GitHub Actions workflow can't be verified without account/repository permissions, and automated unit tests do not replace manual cross-browser testing. **Next improvement:** Playwright smoke test, smarter AI, accessibility audit, verified demo link.
