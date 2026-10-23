"""Battleship Multi-Shot: deterministic, browser-compatible Python domain layer.

The browser runs this module with Pyodide; standard CPython can run its tests.
"""
import json
import random
from copy import deepcopy

SIZE = 10
SHIP_SPECS = [
    {"name": "เรือจู่โจม A", "r": 1, "c": 1, "shots": 2},
    {"name": "เรือจู่โจม B", "r": 1, "c": 1, "shots": 2},
    {"name": "เรือพิฆาตแนวนอน", "r": 1, "c": 3, "shots": 2},
    {"name": "เรือพิฆาตแนวตั้ง", "r": 3, "c": 1, "shots": 2},
    {"name": "เรือประจัญบานแนวนอน", "r": 1, "c": 5, "shots": 1},
    {"name": "เรือประจัญบานแนวตั้ง", "r": 5, "c": 1, "shots": 1},
]


class GameError(ValueError):
    """Recoverable input or game-state error."""


def coordinate(row, col):
    """Reject booleans/non-integers and out-of-bound positions."""
    if type(row) is not int or type(col) is not int or not (0 <= row < SIZE and 0 <= col < SIZE):
        raise GameError("พิกัดไม่ถูกต้อง ต้องเป็นตัวเลข 1–10")


class Board:
    """Ship placement, hit detection, and available firepower."""

    def __init__(self):
        self.grid = [[0] * SIZE for _ in range(SIZE)]
        self.ships = []
        self.shots_history = set()

    def can_place(self, row, col, spec):
        coordinate(row, col)
        if row + spec["r"] > SIZE or col + spec["c"] > SIZE:
            return False
        return all(self.grid[r][c] == 0 for r in range(row, row + spec["r"])
                   for c in range(col, col + spec["c"]))

    def place_ship(self, row, col, spec):
        if not self.can_place(row, col, spec):
            raise GameError("เรือเกินขอบกระดานหรือทับเรือเดิม")
        coords = [(r, c) for r in range(row, row + spec["r"])
                  for c in range(col, col + spec["c"])]
        for r, c in coords:
            self.grid[r][c] = 1
        self.ships.append({"name": spec["name"], "coords": coords,
                           "shots": spec["shots"], "hits": []})

    def total_shots(self):
        return sum(ship["shots"] for ship in self.ships if len(ship["hits"]) < len(ship["coords"]))

    def all_sunk(self):
        return bool(self.ships) and all(len(ship["hits"]) == len(ship["coords"]) for ship in self.ships)

    def receive_shot(self, row, col):
        coordinate(row, col)
        if (row, col) in self.shots_history:
            raise GameError("พิกัดนี้เคยยิงแล้ว")
        self.shots_history.add((row, col))
        if self.grid[row][col] != 1:
            self.grid[row][col] = 2
            return {"type": "miss", "message": "พลาดเป้า!"}
        self.grid[row][col] = 3
        for ship in self.ships:
            if (row, col) in ship["coords"]:
                ship["hits"].append((row, col))
                if len(ship["hits"]) == len(ship["coords"]):
                    for r, c in ship["coords"]:
                        self.grid[r][c] = 4
                    return {"type": "sunk", "message": f"จม {ship['name']} สำเร็จ!"}
                return {"type": "hit", "message": "ยิงโดนเรือ!"}
        raise RuntimeError("Board ship consistency error")

    def dump(self):
        return {"grid": deepcopy(self.grid), "ships": deepcopy(self.ships),
                "shots_history": [list(p) for p in sorted(self.shots_history)]}

    @classmethod
    def load(cls, data):
        """Rebuild grid strictly from ship geometry and recorded shots."""
        if not isinstance(data, dict) or not isinstance(data.get("ships"), list):
            raise GameError("ข้อมูลกระดานเสียหาย")
        if len(data["ships"]) > len(SHIP_SPECS):
            raise GameError("จำนวนเรือไม่ถูกต้อง")
        board = cls()
        for index, ship in enumerate(data["ships"]):
            spec = SHIP_SPECS[index]
            coords = ship.get("coords", [])
            if (not isinstance(coords, list) or len(coords) != spec["r"] * spec["c"]
                    or any(not isinstance(pos, (tuple, list)) or len(pos) != 2 for pos in coords)):
                raise GameError("ข้อมูลเรือเสียหาย")
            row, col = coords[0]
            board.place_ship(row, col, spec)
            if [tuple(p) for p in board.ships[-1]["coords"]] != [tuple(p) for p in coords]:
                raise GameError("รูปทรงเรือไม่ถูกต้อง")
        history = data.get("shots_history", [])
        if not isinstance(history, list) or len(history) > 100:
            raise GameError("ประวัติการยิงเสียหาย")
        for p in history:
            if not isinstance(p, list) or len(p) != 2:
                raise GameError("พิกัดในประวัติเสียหาย")
            board.receive_shot(*p)
        if board.dump()["grid"] != data.get("grid"):
            raise GameError("ข้อมูลตารางไม่ตรงกับประวัติ")
        return board


class BattleshipGame:
    """Game state and AI turn controller (model/business layer)."""

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.player = Board()
        self.enemy = Board()
        self.phase = "setup"
        self.turn = 1
        self.shots_left = 0
        self.winner = None
        self.last_events = []
        for spec in SHIP_SPECS:
            choices = [(r, c) for r in range(SIZE) for c in range(SIZE)
                       if self.enemy.can_place(r, c, spec)]
            self.enemy.place_ship(*self.rng.choice(choices), spec)

    def place(self, row, col):
        if self.phase != "setup":
            raise GameError("ไม่สามารถวางเรือในช่วงนี้")
        index = len(self.player.ships)
        if index >= len(SHIP_SPECS):
            raise GameError("วางเรือครบแล้ว")
        self.player.place_ship(row, col, SHIP_SPECS[index])
        self.last_events = [{"type": "place", "message": f"วาง {SHIP_SPECS[index]['name']} สำเร็จ"}]
        if len(self.player.ships) == len(SHIP_SPECS):
            self.phase = "battle"
            self.shots_left = self.player.total_shots()
            self.last_events.append({"type": "start", "message": "เริ่มการรบ! เลือกช่องบนกระดานศัตรู"})

    def auto_place(self):
        if self.phase != "setup":
            raise GameError("ไม่สามารถสุ่มวางเรือในช่วงนี้")
        while len(self.player.ships) < len(SHIP_SPECS):
            spec = SHIP_SPECS[len(self.player.ships)]
            choices = [(r, c) for r in range(SIZE) for c in range(SIZE)
                       if self.player.can_place(r, c, spec)]
            self.place(*self.rng.choice(choices))
        self.last_events = [{"type": "start", "message": "สุ่มวางกองเรือสำเร็จ! เริ่มการรบ"}]

    def shoot(self, row, col):
        if self.phase != "battle" or self.shots_left <= 0:
            raise GameError("ตอนนี้ยังยิงไม่ได้")
        result = self.enemy.receive_shot(row, col)
        self.shots_left -= 1
        self.last_events = [{**result, "actor": "player", "row": row + 1, "col": col + 1}]
        if self.enemy.all_sunk():
            self.phase = "finished"
            self.winner = "player"
            self.shots_left = 0
            return
        if self.shots_left == 0:
            self._computer_turn()

    def _computer_turn(self):
        shots = self.enemy.total_shots()
        possible = [(r, c) for r in range(SIZE) for c in range(SIZE)
                    if (r, c) not in self.player.shots_history]
        for _ in range(min(shots, len(possible))):
            row, col = self.rng.choice(possible)
            possible.remove((row, col))
            result = self.player.receive_shot(row, col)
            self.last_events.append({**result, "actor": "computer", "row": row + 1, "col": col + 1})
            if self.player.all_sunk():
                self.phase = "finished"
                self.winner = "computer"
                self.shots_left = 0
                return
        self.turn += 1
        self.shots_left = min(self.player.total_shots(),
                              SIZE * SIZE - len(self.enemy.shots_history))
        if self.shots_left == 0:
            self.phase = "finished"
            self.winner = "computer" if not self.enemy.all_sunk() else "player"

    def view(self):
        return {"phase": self.phase, "turn": self.turn, "shots_left": self.shots_left,
                "winner": self.winner, "next_ship": deepcopy(SHIP_SPECS[len(self.player.ships)])
                if self.phase == "setup" else None,
                "placed": len(self.player.ships), "total_ships": len(SHIP_SPECS),
                "player_grid": deepcopy(self.player.grid),
                "enemy_grid": [[0 if n == 1 else n for n in row] for row in self.enemy.grid],
                "player_shots": self.player.total_shots(), "enemy_shots": self.enemy.total_shots(),
                "player_remaining": sum(len(s["hits"]) < len(s["coords"]) for s in self.player.ships),
                "enemy_remaining": sum(len(s["hits"]) < len(s["coords"]) for s in self.enemy.ships),
                "events": deepcopy(self.last_events)}

    def dump(self):
        return {"version": 1, "player": self.player.dump(), "enemy": self.enemy.dump(),
                "phase": self.phase, "turn": self.turn, "shots_left": self.shots_left,
                "winner": self.winner}

    @classmethod
    def load(cls, data):
        if not isinstance(data, dict) or data.get("version") != 1:
            raise GameError("เวอร์ชันข้อมูลเกมไม่รองรับ")
        game = cls()
        game.player = Board.load(data["player"])
        game.enemy = Board.load(data["enemy"])
        game.phase = data["phase"]
        game.turn = data["turn"]
        game.shots_left = data["shots_left"]
        game.winner = data["winner"]
        if (game.phase not in ("setup", "battle", "finished") or type(game.turn) is not int
                or game.turn < 1 or type(game.shots_left) is not int or not 0 <= game.shots_left <= 10
                or game.winner not in (None, "player", "computer")):
            raise GameError("สถานะเกมไม่ถูกต้อง")
        if game.phase == "setup" and (len(game.player.ships) == 6 or game.shots_left != 0):
            raise GameError("สถานะวางเรือไม่ถูกต้อง")
        if game.phase != "setup" and len(game.player.ships) != 6:
            raise GameError("กองเรือไม่ครบ")
        if game.phase == "battle" and (game.winner is not None or game.shots_left < 1
                                       or game.player.all_sunk() or game.enemy.all_sunk()):
            raise GameError("ข้อมูลการรบไม่ถูกต้อง")
        if game.phase == "finished" and (game.winner is None or game.shots_left != 0):
            raise GameError("ข้อมูลจบเกมไม่ถูกต้อง")
        if game.phase == "finished" and not (game.player.all_sunk() or game.enemy.all_sunk()):
            raise GameError("ไม่มีผู้ชนะตามกระดาน")
        game.last_events = [{"type": "load", "message": "โหลดเกมที่บันทึกไว้แล้ว"}]
        return game


class RecordStore:
    """CRUD/search/filter/sort player scores; file transport delegated to browser."""

    def __init__(self):
        self.records = []

    def load(self, records):
        if not isinstance(records, list):
            raise GameError("ข้อมูลประวัติไม่ถูกต้อง")
        self.records = []
        for item in records[:500]:
            self._validate(item)
            if any(x["id"] == item["id"] for x in self.records):
                raise GameError("รหัสประวัติซ้ำ")
            self.records.append(dict(item))

    @staticmethod
    def _validate(item):
        if (not isinstance(item, dict) or type(item.get("id")) is not str or not item["id"]
                or type(item.get("name")) is not str or not 1 <= len(item["name"].strip()) <= 24
                or type(item.get("turns")) is not int or not 1 <= item["turns"] <= 100
                or item.get("result") not in ("win", "lose")
                or not isinstance(item.get("date"), str) or len(item["date"]) > 40):
            raise GameError("ข้อมูลคะแนนไม่ถูกต้อง")

    def add(self, item):
        self._validate(item)
        if any(x["id"] == item["id"] for x in self.records):
            raise GameError("รหัสประวัติซ้ำ")
        self.records.append(dict(item))

    def rename(self, uid, name):
        if type(name) is not str or not 1 <= len(name.strip()) <= 24:
            raise GameError("ชื่อควรมีความยาว 1–24 ตัวอักษร")
        for item in self.records:
            if item["id"] == uid:
                item["name"] = name.strip()
                return
        raise GameError("ไม่พบประวัติ")

    def delete(self, uid):
        before = len(self.records)
        self.records = [item for item in self.records if item["id"] != uid]
        if len(self.records) == before:
            raise GameError("ไม่พบประวัติ")

    def query(self, search="", result="all", order="newest"):
        if result not in ("all", "win", "lose") or order not in ("newest", "oldest", "turns"):
            raise GameError("ตัวกรองไม่ถูกต้อง")
        found = [dict(item) for item in self.records
                 if str(search).casefold() in item["name"].casefold()
                 and (result == "all" or item["result"] == result)]
        key = (lambda x: x["turns"]) if order == "turns" else (lambda x: x["date"])
        return sorted(found, key=key, reverse=order == "newest")


GAME = BattleshipGame()
RECORDS = RecordStore()


def api(request_json):
    """Single JSON-in/JSON-out bridge: never propagate validation errors to UI."""
    global GAME
    try:
        request = json.loads(request_json)
        action = request.get("action")
        if action == "new":
            GAME = BattleshipGame()
        elif action == "place":
            GAME.place(request["row"], request["col"])
        elif action == "auto":
            GAME.auto_place()
        elif action == "shoot":
            GAME.shoot(request["row"], request["col"])
        elif action == "load":
            GAME = BattleshipGame.load(request["save"])
        elif action == "records_load":
            RECORDS.load(request["records"])
        elif action == "records_add":
            RECORDS.add(request["record"])
        elif action == "records_rename":
            RECORDS.rename(request["id"], request["name"])
        elif action == "records_delete":
            RECORDS.delete(request["id"])
        elif action not in ("state", "records_query"):
            raise GameError("ไม่รู้จักคำสั่ง")
        response = {"ok": True, "game": GAME.view(), "save": GAME.dump(),
                    "records": RECORDS.records,
                    "filtered": RECORDS.query(request.get("search", ""),
                                              request.get("result", "all"),
                                              request.get("order", "newest"))}
    except (GameError, ValueError, TypeError, KeyError, IndexError, AttributeError) as error:
        response = {"ok": False, "error": str(error)}
    return json.dumps(response, ensure_ascii=False)
