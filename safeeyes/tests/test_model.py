# Safe Eyes is a utility to remind you to take break frequently
# to protect your eyes from eye strain.

# Copyright (C) 2017  Gobinath

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random
from safeeyes import model

class TestBreak:
    def test_break_short(self):
        b = model.Break(
            model.BreakType.SHORT_BREAK,
            "test break",
            15,
            15,
            None,
            None
        )

        assert b.is_short_break()
        assert not b.is_long_break()

    def test_break_long(self):
        b = model.Break(
            model.BreakType.LONG_BREAK,
            "long break",
            75,
            60,
            None,
            None
        )

        assert not b.is_short_break()
        assert b.is_long_break()


class TestBreakQueue:
    def test_create_empty(self):
        config = {
            "short_breaks": [],
            "long_breaks": [],
            "short_break_interval": 15,
            "long_break_interval": 75,
            "long_break_duration": 60,
            "short_break_duration": 15,
            "random_order": False,
        }

        context = {}

        bq = model.BreakQueue(
            config,
            context
        )

        assert bq.is_empty()
        assert bq.is_empty(model.BreakType.LONG_BREAK)
        assert bq.is_empty(model.BreakType.SHORT_BREAK)
        assert bq.next() is None
        assert bq.get_break() is None


    def get_bq_only_short(self, monkeypatch, random_seed=None):
        if random_seed is not None:
            random.seed(random_seed)

        monkeypatch.setattr(model, "_", lambda message: "translated!: " + message, raising=False)

        config = {
            "short_breaks": [
                {"name": "break 1"},
                {"name": "break 2"},
                {"name": "break 3"},
            ],
            "long_breaks": [],
            "short_break_interval": 15,
            "long_break_interval": 75,
            "long_break_duration": 60,
            "short_break_duration": 15,
            "random_order": random_seed is not None,
        }

        context = {
            "session": {},
        }

        return model.BreakQueue(
            config,
            context
        )


    def get_bq_only_long(self, monkeypatch, random_seed=None):
        if random_seed is not None:
            random.seed(random_seed)

        monkeypatch.setattr(model, "_", lambda message: "translated!: " + message, raising=False)

        config = {
            "short_breaks": [],
            "long_breaks": [
                {"name": "long break 1"},
                {"name": "long break 2"},
                {"name": "long break 3"},
            ],
            "short_break_interval": 15,
            "long_break_interval": 75,
            "long_break_duration": 60,
            "short_break_duration": 15,
            "random_order": random_seed is not None,
        }

        context = {
            "session": {},
        }

        return model.BreakQueue(
            config,
            context
        )


    def get_bq_full(self, monkeypatch, random_seed=None):
        if random_seed is not None:
            random.seed(random_seed)

        monkeypatch.setattr(model, "_", lambda message: "translated!: " + message, raising=False)

        config = {
            "short_breaks": [
                {"name": "break 1"},
                {"name": "break 2"},
                {"name": "break 3"},
                {"name": "break 4"},
            ],
            "long_breaks": [
                {"name": "long break 1"},
                {"name": "long break 2"},
                {"name": "long break 3"},
            ],
            "short_break_interval": 15,
            "long_break_interval": 75,
            "long_break_duration": 60,
            "short_break_duration": 15,
            "random_order": random_seed is not None,
        }

        context = {
            "session": {},
        }

        return model.BreakQueue(
            config,
            context
        )


    def test_create_only_short(self, monkeypatch):
        bq = self.get_bq_only_short(monkeypatch)

        assert not bq.is_empty()
        assert not bq.is_empty(model.BreakType.SHORT_BREAK)
        assert bq.is_empty(model.BreakType.LONG_BREAK)


    def test_only_short_repeat_get_break_no_change(self, monkeypatch):
        bq = self.get_bq_only_short(monkeypatch)

        next = bq.get_break()
        assert next.name == "translated!: break 1"

        next = bq.get_break()
        assert next.name == "translated!: break 1"

        assert not bq.is_long_break()


    def test_only_short_next_break(self, monkeypatch):
        bq = self.get_bq_only_short(monkeypatch)

        next = bq.get_break()
        assert next.name == "translated!: break 1"

        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: break 1"
        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: break 1"
        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 3"


    def test_only_short_next_break_random(self, monkeypatch):
        random_seed = 5
        bq = self.get_bq_only_short(monkeypatch, random_seed)

        next = bq.get_break()
        assert next.name == "translated!: break 3"

        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 1"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: break 1"


    def test_create_only_long(self, monkeypatch):
        bq = self.get_bq_only_long(monkeypatch)

        assert not bq.is_empty()
        assert not bq.is_empty(model.BreakType.LONG_BREAK)
        assert bq.is_empty(model.BreakType.SHORT_BREAK)


    def test_only_long_repeat_get_break_no_change(self, monkeypatch):
        bq = self.get_bq_only_long(monkeypatch)

        next = bq.get_break()
        assert next.name == "translated!: long break 1"

        next = bq.get_break()
        assert next.name == "translated!: long break 1"

        assert bq.is_long_break()


    def test_only_long_next_break(self, monkeypatch):
        bq = self.get_bq_only_long(monkeypatch)

        next = bq.get_break()
        assert next.name == "translated!: long break 1"

        assert bq.next().name == "translated!: long break 2"
        assert bq.next().name == "translated!: long break 3"
        assert bq.next().name == "translated!: long break 1"
        assert bq.next().name == "translated!: long break 2"
        assert bq.next().name == "translated!: long break 3"
        assert bq.next().name == "translated!: long break 1"
        assert bq.next().name == "translated!: long break 2"
        assert bq.next().name == "translated!: long break 3"


    def test_only_long_next_break_random(self, monkeypatch):
        random_seed = 5
        bq = self.get_bq_only_long(monkeypatch, random_seed)

        next = bq.get_break()
        assert next.name == "translated!: long break 3"

        assert bq.next().name == "translated!: long break 2"
        assert bq.next().name == "translated!: long break 1"
        assert bq.next().name == "translated!: long break 3"
        assert bq.next().name == "translated!: long break 1"


    def test_create_full(self, monkeypatch):
        bq = self.get_bq_full(monkeypatch)

        assert not bq.is_empty()
        assert not bq.is_empty(model.BreakType.LONG_BREAK)
        assert not bq.is_empty(model.BreakType.SHORT_BREAK)


    def test_full_repeat_get_break_no_change(self, monkeypatch):
        bq = self.get_bq_full(monkeypatch)

        next = bq.get_break()
        assert next.name == "translated!: break 1"

        next = bq.get_break()
        assert next.name == "translated!: break 1"

        assert not bq.is_long_break()


    def test_full_next_break(self, monkeypatch):
        bq = self.get_bq_full(monkeypatch)

        next = bq.get_break()
        assert next.name == "translated!: break 1"
        assert not bq.is_long_break()

        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: break 4"
        assert bq.next().name == "translated!: long break 1"
        assert bq.is_long_break()
        assert bq.next().name == "translated!: break 1"
        assert not bq.is_long_break()
        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: break 4"
        assert bq.next().name == "translated!: long break 2"
        assert bq.next().name == "translated!: break 1"
        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: break 4"
        assert bq.next().name == "translated!: long break 3"
        assert bq.next().name == "translated!: break 1"
        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: break 4"
        assert bq.next().name == "translated!: long break 1"
        assert bq.next().name == "translated!: break 1"
        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: break 4"
        assert bq.next().name == "translated!: long break 2"
        assert bq.next().name == "translated!: break 1"
        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: break 4"
        assert bq.next().name == "translated!: long break 3"
        assert bq.next().name == "translated!: break 1"
        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: break 4"
        assert bq.next().name == "translated!: long break 1"


    def test_full_next_break_random(self, monkeypatch):
        random_seed = 5
        bq = self.get_bq_full(monkeypatch, random_seed)

        next = bq.get_break()
        assert next.name == "translated!: break 1"

        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 4"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: long break 3"
        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 1"
        assert bq.next().name == "translated!: break 4"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: long break 2"
        assert bq.next().name == "translated!: break 2"
        assert bq.next().name == "translated!: break 4"
        assert bq.next().name == "translated!: break 1"
        assert bq.next().name == "translated!: break 3"
        assert bq.next().name == "translated!: long break 1"
