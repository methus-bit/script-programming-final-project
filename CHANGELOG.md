# CHANGELOG — Battleship Multi-Shot Web Final

This changelog describes delivered source artifacts; dates below are not claims of GitHub merges or completed course presentations. Original mini-project history retained at `legacy/CHANGELOG_mini.md`.

## [2.0.0] — Web Final Project (2026-10-24)

### Added
- Responsive playable two-board GUI (`index.html`, `style.css`, `app.js`).
- Python-only rules engine (`battleship.py`) executed in-browser via Pyodide.
- OOP classes `Board`, `BattleshipGame`, `RecordStore`; JSON API for frontend integration.
- Manual placement, automatic fleet placement, live hit/miss/sunk updates and random computer opponent.
- Browser localStorage save/restore, JSON export/import and persistent score records.
- Record CRUD, player-name search, outcome filtering and chronological/turn-count sorting.
- Automated Python unit tests, JavaScript syntax check and GitHub Actions Pages workflow.
- Sprint reports, planning documentation, demo checklist and copied original CLI/learning documents.

### Changed
- Replaced blocking terminal `input()` / `print()` gameplay with click-driven UI while preserving ship dimensions and multi-shot rules.
- Computer chooses from remaining target cells rather than repeatedly retrying random coordinates.
- All game-state mutations occur in Python business layer; JavaScript handles UI and file/browser persistence.

### Fixed
- Explicit rejection of invalid/negative coordinates, overlaps, out-of-range shots and duplicate targeting.
- Restore of tuple coordinates serialized to JSON lists.
- Prevent enemy ship disclosure in public view state.

### Known limitations
- GitHub Pages hosting requires push to user's repo, Pages configuration and deployed-browser verification.
- Runtime fetched from an external Pyodide CDN on first load; online connection required.
- Scores live on each browser only; no central anti-cheat database or account synchronization.
- Smart/LLM-powered AI and automated browser E2E tests are not implemented.
