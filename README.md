# ⚓ Battleship: Multi-Shot Edition — Python Web Final Project

A responsive Battleship web game based on the original Python CLI mini-project. **Game mechanics really run in Python** inside the browser using Pyodide; static HTML/CSS/JS provides the frontend, so it can be deployed on **GitHub Pages** without a Python server.

## Features

- Two 10×10 boards; 6 ship shapes exactly matching the original mini-project (1×1, 1×1, 1×3, 3×1, 1×5, 5×1).
- Manual/auto ship placement with validation, hit/miss/sunk feedback, hidden enemy fleet.
- Dynamic multi-shot combat: initially **10 shots per round**; surviving ships determine available shots.
- Automated computer attacks; no duplicate targeting; win/lose detection.
- Save/resume, JSON backup & restore, and browser-local scoreboard (CRUD, search/filter/sort).
- CI on push/PR and GitHub Actions deployment on `main`.

## Play locally

Requires Python 3 (for web server) and an internet connection (for Pyodide CDN).

```bash
python -m http.server 8000
```

Visit `http://localhost:8000/` in a web browser. **Do not double-click** `index.html` and open `file://`: `fetch('./battleship.py')` may be blocked by browser security. The web game is not launched using `python battleship.py`; that file is the domain engine. To run the **old CLI version**, use `python legacy/battleship_cli.py`.

## Deploy to GitHub Pages

1. Create a new GitHub repository (for example `battleship-web`), default branch named `main`.
2. Upload **all project files preserving their folders**, including `.github/workflows/pages.yml`, `.nojekyll`, `index.html`, `app.js`, `style.css`, `battleship.py`.
3. In the repository select **Settings → Pages → Build and deployment → Source → GitHub Actions**.
4. Push to `main` (or manually run the Pages workflow in the **Actions** tab). Confirm **test** and **deploy** jobs succeed.
5. Visit `https://methus-bit.github.io/script-programming-final-project/` (the actual URL is also shown in the deployment run).

> GitHub Pages serves static files only. Pyodide downloads WebAssembly Python runtime to the visitor's browser. There is no Flask server to deploy and no GitHub token/secret needed for gameplay. Site will not function offline on first load without caching.

### Git commands example

```bash
git init
git add .
git commit -m "Build Battleship Python web final project"
git branch -M main
git remote add origin https://github.com/methus-bit/script-programming-final-project.git
git push -u origin main
```

Create the empty repository on GitHub **before** `git push` and replace placeholders; do not run `git init` within an existing repository.

## Run automated tests

```bash
python -m unittest discover -s tests -v
node --check app.js
```

The Python engine has no third-party CPython dependency. JavaScript is checked by Node. The current local test suite contains **9 Python tests**, passing at creation time; the site must still be browser-tested after publishing.

## Project structure

```text
battleship-final/
├── index.html                     # Presentation HTML
├── style.css                      # Responsive UI
├── app.js                         # JS renderer + localStorage DAL
├── battleship.py                  # Python OOP domain + JSON API
├── tests/test_battleship.py       # unittest
├── .github/workflows/pages.yml    # test + Pages deployment
├── .nojekyll
├── PLAN.md
├── sprint1.md
├── sprint2.md
├── sprint3.md
├── sprintfinal.md
├── CHANGELOG.md
├── docs/final_project_script_programming.md
└── legacy/                       # Preserved original mini-project source/docs
```

## Game play

1. Click player board to place each ship in given fixed orientation, or select **สุ่มวางเรือ**.
2. Click enemy board to shoot. The current `shots_left` counter decreases for each shot; after last shot computer fires back.
3. When a whole ship is hit it sinks, reducing its owner's firing power; match ends when one fleet is destroyed.
4. Reload the page to resume the automatically saved game. Results are saved to **localStorage**; update/delete names and search/filter/sort history.
5. Export a JSON backup to migrate records to another browser; import to restore. This is browser-local, not a synchronized multiplayer leaderboard.

## Architecture & requirements

See [`PLAN.md`](PLAN.md) for UML, schema, 3-layer separation, sprint schedule, test criteria, risks and presentation outline. See `sprint1.md` through `sprintfinal.md` for implementation logs. The older original learning reflection is in `legacy/LEARNINGLOG.md`.

**AI disclosure:** The in-game bot uses *random automated targeting*, **not ML/LLM**. AI-related lessons from the mini-project are preserved; richer smart-agent functionality is a proposed enhancement, not a delivered feature.
