""""
Conway's Game Of Life

20221125

Version: 1.0
"""

import json

import numpy as np


class GameOfLife:
    """Conway's Game Of Life"""

    def __init__(
        self,
        board_width: int,
        board_height: int,
        in_box: bool = True,
        initiate_randomly: bool = False,
    ) -> None:
        """Conway's Game Of Life

        Args:
            board_width (int): Game board width.
            board_height (int): Game board height.
            in_box (bool, optional): Bounded by board boundaries. Defaults to True.
            initiate_randomly (bool, optional): Initiate populations randomly. Defaults to False.
        """
        self._board_width = board_width
        self._board_height = board_height
        self._in_box = in_box
        self._initiate_randomly = initiate_randomly
        self._board = self._create_board()
        self._mask_life = np.zeros(
            (self._board_height, self._board_width),
            dtype=np.int64,
        )
        self._mask_dead = np.zeros(
            (self._board_height, self._board_width),
            dtype=np.int64,
        )

    def __str__(self) -> str:
        return str(self._board)

    @classmethod
    def from_json(cls, filepath: str):
        """Create Conway's Game Of Life based on a json file

        Args:
            filepath (str): Json file path.

        Returns:
            GameOfLife: Conway's Game Of Life
        """
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        new_game = cls(
            data["board_width"],
            data["board_height"],
            data["in_box"],
            initiate_randomly=False,
        )
        new_game._board = np.frombuffer(
            bytes(data["board"], "utf-8"), dtype=np.int64
        ).reshape((data["board_height"], data["board_width"]))
        new_game._mask_life = np.frombuffer(
            bytes(data["mask_life"], "utf-8"), dtype=np.int64
        ).reshape((data["board_height"], data["board_width"]))
        new_game._mask_dead = np.frombuffer(
            bytes(data["mask_dead"], "utf-8"), dtype=np.int64
        ).reshape((data["board_height"], data["board_width"]))
        return new_game

    @classmethod
    def from_np(cls, array: np.ndarray, in_box=True):
        """Create Conway's Game Of Life based on a np.ndarray

        Args:
            array (np.ndarray): Board
            in_box (bool, optional): Bounded by board boundaries. Defaults to True.

        Returns:
            GameOfLife: Conway's Game Of Life
        """
        board_height, board_width = array.shape
        new_game = cls(
            board_width, board_height, in_box=in_box, initiate_randomly=False
        )
        new_game._board = array
        return new_game

    @property
    def board(self) -> np.ndarray:
        """Game board

        Returns:
            np.ndarray: Game board
        """
        return self._board

    @board.setter
    def board(self, value: np.ndarray):
        self._board = value

    @property
    def mask_life(self) -> np.ndarray:
        """Life mask

        Returns:
            np.ndarray: Life mask
        """
        return self._mask_life

    @mask_life.setter
    def mask_life(self, value: np.ndarray):
        self._mask_life = value
        self._apply_masks()

    @property
    def mask_dead(self) -> np.ndarray:
        """Dead mask

        Returns:
            np.ndarray: Dead mask
        """
        return self._mask_dead

    @mask_dead.setter
    def mask_dead(self, value: np.ndarray):
        self._mask_dead = value
        self._apply_masks()

    def _create_board(self) -> np.ndarray:
        if self._initiate_randomly:
            return np.random.randint(
                0,
                2,
                size=(self._board_height, self._board_width),
                dtype=np.int64,
            )
        return np.zeros(
            (self._board_height, self._board_width),
            dtype=np.int64,
        )

    def _apply_masks(self):
        temp_board = self._board
        temp_board = (temp_board == 1) | (self._mask_life == 1)
        temp_board = (temp_board == 1) & (self._mask_dead == 0)
        self._board = temp_board.astype(np.int64)

    def update_board(self) -> None:
        """Update the board to the next generation."""
        temp_board = self._board
        if self._in_box:
            temp_board = np.pad(temp_board, ((1, 1), (1, 1)), constant_values=0)

        neighbor = np.zeros(temp_board.shape, dtype=np.int64)
        neighbor += np.roll(temp_board, 1, axis=0)
        neighbor += np.roll(temp_board, -1, axis=0)
        neighbor += np.roll(temp_board, 1, axis=1)
        neighbor += np.roll(temp_board, -1, axis=1)
        neighbor += np.roll(temp_board, (1, 1), axis=(0, 1))
        neighbor += np.roll(temp_board, (-1, -1), axis=(0, 1))
        neighbor += np.roll(temp_board, (-1, 1), axis=(0, 1))
        neighbor += np.roll(temp_board, (1, -1), axis=(0, 1))

        temp_board = ((neighbor == 3) & (temp_board == 0)) | (
            ((neighbor == 2) | (neighbor == 3)) & (temp_board == 1)
        )
        temp_board = temp_board.astype(np.int64)

        if self._in_box:
            temp_board = temp_board[1:-1, 1:-1]

        self._board = temp_board
        self._apply_masks()

    def export_game(self, filepath: str) -> None:
        """Export the board to a json file

        Args:
            filepath (str): Json file path.
        """
        data = {
            "board_width": self._board_width,
            "board_height": self._board_height,
            "in_box": self._in_box,
            "board": self._board.tobytes().decode("utf-8"),
            "mask_life": self._mask_life.tobytes().decode("utf-8"),
            "mask_dead": self._mask_dead.tobytes().decode("utf-8"),
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
