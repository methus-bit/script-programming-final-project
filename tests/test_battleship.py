"""Regression and edge-case tests for web-compatible Python engine."""
import json
import unittest
from battleship import Board, BattleshipGame, GameError, SHIP_SPECS, RecordStore, api


class TestBoard(unittest.TestCase):
    def test_separate_rows(self):
        board = Board()
        board.grid[0][0] = 1
        self.assertEqual(board.grid[1][0], 0)

    def test_placement_boundary_overlap_and_negative(self):
        board = Board()
        with self.assertRaises(GameError):
            board.can_place(-1, 0, SHIP_SPECS[0])
        with self.assertRaises(GameError):
            board.can_place(True, 0, SHIP_SPECS[0])
        self.assertFalse(board.can_place(0, 8, SHIP_SPECS[2]))
        board.place_ship(0, 0, SHIP_SPECS[0])
        self.assertFalse(board.can_place(0, 0, SHIP_SPECS[1]))

    def test_sink_decreases_shots(self):
        board = Board()
        board.place_ship(0, 0, SHIP_SPECS[0])
        board.place_ship(1, 0, SHIP_SPECS[2])
        self.assertEqual(board.total_shots(), 4)
        self.assertEqual(board.receive_shot(0, 0)['type'], 'sunk')
        self.assertEqual(board.total_shots(), 2)
        with self.assertRaises(GameError):
            board.receive_shot(0, 0)
        self.assertEqual(board.receive_shot(5, 5)['type'], 'miss')

    def test_board_roundtrip_and_tamper(self):
        board = Board()
        board.place_ship(0, 0, SHIP_SPECS[0])
        board.receive_shot(0, 0)
        board.receive_shot(9, 9)
        saved = board.dump()
        self.assertEqual(Board.load(saved).dump(), saved)
        saved['grid'][0][0] = 1
        with self.assertRaises(GameError):
            Board.load(saved)


class TestGame(unittest.TestCase):
    def test_autoplace_and_no_shot_duplicates(self):
        game = BattleshipGame(seed=3)
        game.auto_place()
        self.assertEqual(game.phase, 'battle')
        self.assertEqual(game.shots_left, 10)
        for _ in range(10):
            valid = next((r, c) for r in range(10) for c in range(10)
                         if (r, c) not in game.enemy.shots_history)
            game.shoot(*valid)
            if game.phase == 'finished':
                break
        self.assertEqual(len(game.enemy.shots_history), len(set(game.enemy.shots_history)))
        self.assertEqual(len(game.player.shots_history), len(set(game.player.shots_history)))
        self.assertEqual(game.turn, 2)

    def test_no_enemy_reveal(self):
        game = BattleshipGame(seed=1)
        self.assertTrue(any(1 in row for row in game.enemy.grid))
        self.assertFalse(any(1 in row for row in game.view()['enemy_grid']))

    def test_save_load(self):
        game = BattleshipGame(seed=4)
        game.auto_place()
        game.shoot(0, 0)
        restored = BattleshipGame.load(json.loads(json.dumps(game.dump())))
        self.assertEqual(restored.view()['shots_left'], 9)
        self.assertEqual(restored.dump(), game.dump())

    def test_api_invalid(self):
        self.assertFalse(json.loads(api(json.dumps({'action':'shoot','row':-5,'col':0})))['ok'])
        self.assertFalse(json.loads(api(json.dumps({'action':'what'})))['ok'])


class TestRecords(unittest.TestCase):
    def test_crud_filter_sort(self):
        store = RecordStore()
        entries = [dict(id='1', name='Alice', turns=6, result='win', date='2026-10-10'),
                   dict(id='2', name='Bob', turns=3, result='lose', date='2026-10-11'),
                   dict(id='3', name='alice2', turns=2, result='win', date='2026-10-12')]
        for entry in entries:
            store.add(entry)
        self.assertEqual([r['id'] for r in store.query('alice', 'win', 'turns')], ['3', '1'])
        store.rename('2', 'Robert')
        self.assertEqual(store.query('robert')[0]['name'], 'Robert')
        store.delete('2')
        self.assertEqual(len(store.records), 2)
        with self.assertRaises(GameError):
            store.delete('not-found')
        with self.assertRaises(GameError):
            store.load('bad data')


if __name__ == '__main__':
    unittest.main()
