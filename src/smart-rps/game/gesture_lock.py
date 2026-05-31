
from __future__ import annotations

from typing import Optional


GESTURE_TO_MOVE: dict[str, str] = {"Rock": "R", "Paper": "P", "Scissors": "S"}

#frames a single valid gesture must be held continuously before it locks
LOCK_FRAMES = 24


class GestureLock:
    def __init__(self, lock_frames: int = LOCK_FRAMES) -> None:
        self.lock_frames = lock_frames
        self._held_move: Optional[str] = None
        self._count: int = 0

    def reset(self) -> None:

        self._held_move = None
        self._count = 0

    @property
    def progress(self) -> float:
        if self.lock_frames <= 0:
            return 1.0
        return min(1.0, self._count / self.lock_frames)

    @property
    def held_move(self) -> Optional[str]:
        #move currently being held , or None
        return self._held_move

    def update(self, gesture_name: str) -> Optional[str]:
        
        #returns the locked move 
    
        move = GESTURE_TO_MOVE.get(gesture_name)
        if move is None:
            # not a valid R/P/S this frame -> drop the streak entirely
            self._held_move = None
            self._count = 0
            return None
        if move != self._held_move:
            # a different valid gesture -> start a fresh streak at 1
            self._held_move = move
            self._count = 1
            return None
        # same valid gesture held -> advance; lock at the threshold
        self._count += 1
        if self._count >= self.lock_frames:
            return move
        return None
