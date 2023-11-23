""""
Conway's Game Of Life GUI

20221125

Version: 0.5 (beta)

TODO:
    - Debug: After opening the file, it is not possible to edit it. (?)
    - NewGameWindow interface update
    - Add the ability to edit masks
"""

import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import numpy as np
import ttkbootstrap as ttk

from game_of_life import GameOfLife

ANIMATION_FRAME_RATE = 15
CELL_SIZE = 10


class NewGameWindow(tk.Toplevel):
    """New game window (tk.Frame)"""

    def __init__(self, master=None, *args, **kwargs):
        """New game window (tk.Frame)"""
        super().__init__(master, *args, **kwargs)

        board_width_label = ttk.Label(self, text="Board width:")
        board_width_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        board_width_entry = ttk.Entry(
            self, textvariable=self.master._var_board_width  # type: ignore
        )
        board_width_entry.grid(column=1, row=0, sticky=tk.W, padx=5, pady=5)

        board_height_label = ttk.Label(self, text="Board height:")
        board_height_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        board_height_entry = ttk.Entry(
            self, textvariable=self.master._var_board_height  # type: ignore
        )
        board_height_entry.grid(column=1, row=1, sticky=tk.W, padx=5, pady=5)

        initiate_randomly_label = ttk.Label(self, text="Initiate randomly:")
        initiate_randomly_label.grid(
            column=0, row=2, sticky=tk.W, padx=5, pady=5
        )

        initiate_randomly_entry = ttk.Checkbutton(
            self,
            variable=self.master._var_initiate_randomly,  # type: ignore
            bootstyle="round-toggle",  # type: ignore
        )
        initiate_randomly_entry.grid(
            column=1, row=2, sticky=tk.W, padx=5, pady=5
        )

        box_mode_label = ttk.Label(self, text="Box mode:")
        box_mode_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)

        box_mode_entry = ttk.Checkbutton(
            self,
            variable=self.master._var_box_mode,  # type: ignore
            bootstyle="round-toggle",  # type: ignore
        )
        box_mode_entry.grid(column=1, row=3, sticky=tk.W, padx=5, pady=5)

        create_game_btn = ttk.Button(
            self,
            text="Create game",
            command=lambda: self.master._init_new_game(),  # type: ignore
        )
        create_game_btn.grid(
            column=0, row=4, sticky=tk.W, padx=5, pady=5, columnspan=1
        )


class BoardViewer(tk.Frame):
    """Game board viewer (tk.Frame)"""

    def __init__(self, master=None, *args, **kwargs):
        """Game board viewer (tk.Frame)"""
        super().__init__(master, *args, **kwargs)
        ttk.Label(self, text="Ctrl+N - Create a new game.\nCtrl+O - Open the game.").pack(anchor=tk.CENTER, fill="y", expand=True)
        self.canvas = None


class App(tk.Frame):
    """Main app (tk.Frame)"""

    def __init__(self, master=None, *args, **kwargs):
        """Main app (tk.Frame)"""
        super().__init__(master, *args, **kwargs)
        self.pack(side="top", fill="both", expand=True)

        self.game = None

        self.configure(background="white")
        self._configure_gui()
        self._create_variables()
        self._create_widgets()
        self._create_shortcuts()

    def _configure_gui(self):
        self.master.title("Conway's Game Of Life")  # type: ignore
        self.master.geometry("500x500")  # type: ignore
        self.master.resizable(False, False)  # type: ignore

    def _create_variables(self):
        self._var_board_width = tk.IntVar(value=50)
        self._var_board_height = tk.IntVar(value=50)
        self._var_initiate_randomly = tk.BooleanVar(value=True)
        self._var_box_mode = tk.BooleanVar(value=False)
        self._var_run_game = tk.BooleanVar(value=False)

    def _create_shortcuts(self):
        self.master.bind("<space>", self._run_game)
        self.master.bind("<Control-n>", self._new_geme)
        self.master.bind("<Control-o>", self._open_game)
        self.master.bind("<Control-s>", self._seve_game)
        self.master.bind("<Control-q>", lambda event: self.master.destroy())
        self.master.bind("<Button-1>", self._edit_cell)

    def _create_widgets(self):
        self.boardviewer = BoardViewer(self)
        self.boardviewer.pack(side="right", fill="both", expand=True)

    def _new_geme(self, event):
        self._var_run_game.set(False)
        if hasattr(self, "newgamewindow"):
            self.newgamewindow.destroy()
        self.newgamewindow = NewGameWindow(self)

    def _open_game(self, event):
        if hasattr(self, "newgamewindow"):
            self.newgamewindow.destroy()
        filetypes = (("JSON file", "*.json"), ("cells file", "*.cells"), ("All file", "*.*"))
        filename = filedialog.askopenfilename(
            title="Open game",
            filetypes=filetypes,
        )
        if filename:
            extension = Path(filename).suffix
            if extension != '.json' and extension != '.cells':
                return
            if extension == '.json':
                self.game = GameOfLife.from_json(filename)
            self.game = GameOfLife.from_cells_file(filename)
            self._var_board_width.set(self.game._board_width)
            self._var_board_height.set(self.game._board_height)
            self._var_initiate_randomly.set(self.game._initiate_randomly)
            self._var_box_mode.set(self.game._in_box)
            self._create_canvas()

    def _seve_game(self, event):
        if not hasattr(self, "game"):
            return
        filetypes = (("JSON files", "*.json"), ("All files", "*.*"))
        filename = filedialog.asksaveasfilename(
            title="Save game",
            filetypes=filetypes,
        )
        if filename is None:
            return
        self.game.export_game(filename)

    def _run_game(self, event):
        self._var_run_game.set(not self._var_run_game.get())
        if self._var_run_game.get():
            self.boardviewer.canvas.after(  # type: ignore
                1000 // ANIMATION_FRAME_RATE, self._animate
            )

    def _edit_cell(self, event):
        if self.game is None:
            return
        x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
        print(self.game.board[y][x])
        self.game.board[y][x] = 0 if self.game.board[y][x] else 1
        self._update_game_board()

    def _init_new_game(self):
        """New game initialization"""
        if hasattr(self, "newgamewindow"):
            self.newgamewindow.destroy()
        board_width = self._var_board_width.get()
        board_height = self._var_board_height.get()
        initiate_randomly = self._var_initiate_randomly.get()
        box_mode = self._var_box_mode.get()

        self.game = GameOfLife(
            board_width,
            board_height,
            initiate_randomly=initiate_randomly,
            in_box=box_mode,
        )
        self._create_canvas()

    def _create_canvas(self):
        """Create new canvas (game board)"""
        board_width = self._var_board_width.get()
        board_height = self._var_board_height.get()

        # Resize window
        self.master.geometry(  # type: ignore
            f"{board_width*CELL_SIZE+1}x{board_height * CELL_SIZE + 1}"
        )

        # Cleanup BoardViewer
        for widget in self.boardviewer.winfo_children():
            widget.destroy()

        self.boardviewer.canvas = tk.Canvas(  # type: ignore
            self.boardviewer,
            width=board_width * CELL_SIZE,
            height=board_height * CELL_SIZE,
            bg="white",
        )

        self.boardviewer.canvas.pack(anchor=tk.CENTER, expand=True)
        self._update_game_board()

    def _update_game_board(self):
        """Update game board"""
        # Cleanup board
        self.boardviewer.canvas.delete("all")  # type: ignore
        row, col = np.indices(
            (self._var_board_height.get(), self._var_board_width.get())
        )
        for y, x, value in zip(
            row.flatten(), col.flatten(), self.game.board.flatten()
        ):
            fill = "black" if value else "white"
            self.boardviewer.canvas.create_rectangle(  # type: ignore
                (x * CELL_SIZE, y * CELL_SIZE),
                ((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE),
                fill=fill,
                outline="#e5e5e5",
            )

    def _animate(self):
        if self._var_run_game.get():
            self.game.update_board()
            self._update_game_board()

            self.boardviewer.canvas.after(  # type: ignore
                1000 // ANIMATION_FRAME_RATE, self._animate
            )


if __name__ == "__main__":
    main_app = App()
    main_app.mainloop()
