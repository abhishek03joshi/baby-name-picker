"""Native Tkinter desktop interface for Name Picker."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .picker import MAX_NAMES, MAX_TRIES, SessionResult, run_session


BG = "#eef2f0"
CARD = "#fffdf8"
INK = "#1f3040"
MUTED = "#687a80"
TEAL = "#4d8b84"
TEAL_DARK = "#356b67"
MIST = "#dce9e5"
GOLD = "#f2d39b"


class NamePickerApp(tk.Tk):
    """A small, native Mac-friendly window for picking a name."""

    def __init__(self) -> None:
        super().__init__()
        self.title("🌙 Baby Name Picker")
        self.geometry("900x720")
        self.minsize(680, 560)
        self.configure(bg=BG)

        self.name_vars = [tk.StringVar() for _ in range(MAX_NAMES)]
        self.tries_var = tk.IntVar(value=1)
        self.best_of_var = tk.StringVar(value="Best-of-1 round")
        self.result_var = tk.StringVar(value="Ready when you are ✨")
        self.all_time_var = tk.StringVar(value="All-time winner: —")
        self.rounds_var = tk.StringVar(value="")
        self.current_result: SessionResult | None = None
        self.all_time_scores: dict[str, int] = {}
        self.scoreboard: ttk.Treeview
        self.rounds_view: ttk.Treeview
        self.history_body: ttk.Frame
        self.history_toggle: ttk.Button
        self.pick_button: ttk.Button
        self.progress: ttk.Progressbar
        self._build_styles()
        self._build_layout()
        self.tries_var.trace_add("write", self._update_best_of_label)

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("App.TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD, bordercolor=MIST, borderwidth=1, relief="solid")
        style.configure("Title.TLabel", background=BG, foreground=INK, font=("Helvetica", 24, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=("Helvetica", 11))
        style.configure("Card.TLabel", background=CARD, foreground=INK, font=("Helvetica", 11))
        style.configure("Muted.Card.TLabel", background=CARD, foreground=MUTED, font=("Helvetica", 10))
        style.configure("Result.TLabel", background=CARD, foreground=TEAL_DARK, font=("Helvetica", 18, "bold"))
        style.configure("AllTime.TLabel", background=GOLD, foreground=INK, font=("Helvetica", 12, "bold"), padding=8)
        style.configure("Accent.TButton", background=TEAL, foreground="white", font=("Helvetica", 12, "bold"), padding=(16, 9), borderwidth=0)
        style.map("Accent.TButton", background=[("active", TEAL_DARK), ("pressed", TEAL_DARK)])
        style.configure("Treeview", background=CARD, fieldbackground=CARD, foreground=INK, rowheight=30, font=("Helvetica", 11), borderwidth=0)
        style.configure("Treeview.Heading", background=MIST, foreground=INK, font=("Helvetica", 10, "bold"), padding=6)
        style.map("Treeview", background=[("selected", GOLD)], foreground=[("selected", INK)])
        style.configure("Modern.Horizontal.TProgressbar", troughcolor=MIST, background=TEAL, bordercolor=MIST, lightcolor=TEAL, darkcolor=TEAL_DARK)

    def _build_layout(self) -> None:
        outer = ttk.Frame(self, style="App.TFrame", padding=28)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="🌙 Baby Name Picker", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            outer,
            text="A little science, a little luck, and one very important name.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 20))

        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(2, weight=1)

        workspace = ttk.Panedwindow(outer, orient="horizontal")
        workspace.grid(row=2, column=0, sticky="nsew")

        result_card = ttk.Frame(workspace, style="Card.TFrame", padding=18)
        names_card = ttk.Frame(workspace, style="Card.TFrame", padding=18)
        workspace.add(result_card, weight=4)
        workspace.add(names_card, weight=2)
        ttk.Label(names_card, text="Names", style="Card.TLabel").pack(anchor="w")
        ttk.Label(names_card, text="Enter 2–10 names", style="Muted.Card.TLabel").pack(anchor="w", pady=(4, 12))

        for index, name_var in enumerate(self.name_vars):
            row = ttk.Frame(names_card, style="Card.TFrame")
            row.pack(fill="x", pady=3)
            ttk.Label(row, text=f"{index + 1}", width=3, style="Muted.Card.TLabel").pack(side="left")
            ttk.Entry(row, textvariable=name_var).pack(side="left", fill="x", expand=True)

        ttk.Label(names_card, textvariable=self.best_of_var, style="Card.TLabel").pack(anchor="w", pady=(18, 4))
        ttk.Label(names_card, text=f"Choose a value from 1 to {MAX_TRIES}", style="Muted.Card.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Combobox(
            names_card,
            textvariable=self.tries_var,
            values=tuple(range(1, MAX_TRIES + 1)),
            state="readonly",
            width=8,
        ).pack(anchor="w")
        self.pick_button = ttk.Button(names_card, text="Pick the names ✨", style="Accent.TButton", command=self.pick_names)
        self.pick_button.pack(fill="x", pady=(18, 0))
        self.progress = ttk.Progressbar(names_card, mode="indeterminate", style="Modern.Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(10, 0))

        ttk.Label(result_card, textvariable=self.result_var, style="Result.TLabel").pack(anchor="w")
        ttk.Label(result_card, text="Freshly randomized result", style="Muted.Card.TLabel").pack(anchor="w", pady=(4, 12))

        history_panel = ttk.Frame(result_card, style="Card.TFrame")
        history_panel.pack(side="bottom", fill="x", pady=(12, 0))
        ttk.Label(history_panel, textvariable=self.all_time_var, style="AllTime.TLabel").pack(fill="x", pady=(0, 8))
        history_header = ttk.Frame(history_panel, style="Card.TFrame")
        history_header.pack(fill="x")
        self.history_toggle = ttk.Button(history_header, text="Hide round history ▲", command=self.toggle_history)
        self.history_toggle.pack(side="left")

        self.history_body = ttk.Frame(history_panel, style="Card.TFrame")
        self.history_body.pack(fill="x", pady=(8, 0))
        self.rounds_view = ttk.Treeview(self.history_body, columns=("round", "finalists", "winner"), show="headings", height=5)
        self.rounds_view.heading("round", text="#")
        self.rounds_view.heading("finalists", text="Finalists")
        self.rounds_view.heading("winner", text="Winner")
        self.rounds_view.column("round", width=35, anchor="center")
        self.rounds_view.column("finalists", width=190, anchor="w")
        self.rounds_view.column("winner", width=90, anchor="w")
        self.rounds_view.pack(fill="x")

        actions = ttk.Frame(self.history_body, style="Card.TFrame")
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Clear selected round", command=self.clear_selected_round).pack(side="left")
        ttk.Button(actions, text="Clear all rounds", command=self.clear_all_rounds).pack(side="right")

        content = ttk.Frame(result_card, style="Card.TFrame")
        content.pack(fill="both", expand=True)
        self.scoreboard = ttk.Treeview(content, columns=("name", "score"), show="headings", height=8)
        self.scoreboard.heading("name", text="Name")
        self.scoreboard.heading("score", text="Wins")
        self.scoreboard.column("name", width=180, anchor="w")
        self.scoreboard.column("score", width=70, anchor="center")
        self.scoreboard.pack(side="left", fill="both", expand=True)

    def pick_names(self) -> None:
        names = [name_var.get().strip() for name_var in self.name_vars if name_var.get().strip()]
        try:
            tries = self.tries_var.get()
            result = run_session(names, tries)
        except (tk.TclError, ValueError) as error:
            messagebox.showerror("Let’s fix that", str(error), parent=self)
            return
        self._add_to_all_time(result.scores)
        self.pick_button.state(["disabled"])
        self.progress.start(80)
        self._animate_result(result)

    def _animate_result(self, result: SessionResult, frame: int = 0) -> None:
        messages = ("Shuffling chits", "Shuffling chits ·", "Shuffling chits · ·", "Shuffling chits ✨")
        if frame < len(messages):
            self.result_var.set(messages[frame])
            self.update_idletasks()
            self.after(120, lambda: self._animate_result(result, frame + 1))
            return
        self._display_result(result, animate_scores=True)

    def toggle_history(self) -> None:
        if self.history_body.winfo_manager():
            self.history_body.pack_forget()
            self.history_toggle.configure(text="Show round history ▼")
        else:
            self.history_body.pack(fill="x", pady=(8, 0))
            self.history_toggle.configure(text="Hide round history ▲")

    def _display_result(self, result: SessionResult, animate_scores: bool = False) -> None:
        self.current_result = result
        for item in self.scoreboard.get_children():
            self.scoreboard.delete(item)
        score_rows = sorted(result.scores.items(), key=lambda item: (-item[1], item[0].casefold()))

        for item in self.rounds_view.get_children():
            self.rounds_view.delete(item)
        for round_result in result.rounds:
            self.rounds_view.insert(
                "",
                "end",
                iid=str(round_result.round_number),
                values=(round_result.round_number, " · ".join(round_result.finalists), round_result.winner),
            )
        if animate_scores:
            self.result_var.set("The scoreboard is landing ✨")
            self._reveal_score_rows(result, score_rows)
            return
        for name, score in score_rows:
            self.scoreboard.insert("", "end", values=(name, score))
        self._finish_display(result)

    def _reveal_score_rows(self, result: SessionResult, score_rows: list[tuple[str, int]], index: int = 0) -> None:
        if index >= len(score_rows):
            self._finish_display(result)
            return
        name, score = score_rows[index]
        item_id = self.scoreboard.insert("", "end", values=(name, score), tags=("new-score",))
        self.scoreboard.tag_configure("new-score", background=GOLD)
        self.after(240, lambda: self.scoreboard.item(item_id, tags=()))
        self.after(110, lambda: self._reveal_score_rows(result, score_rows, index + 1))

    def _finish_display(self, result: SessionResult) -> None:
        self.progress.stop()
        self.pick_button.state(["!disabled"])
        if not result.rounds:
            self.result_var.set("No rounds remaining")
            return
        if result.has_clear_winner:
            self.result_var.set(f"🎉 Winner: {result.leaders[0]}")
        else:
            self.result_var.set(f"🤝 Tie: {', '.join(result.leaders)}")
            # Flush the new scoreboard and round text before opening the modal
            # prompt, so the updated result is visible behind it.
            self.update_idletasks()
            if messagebox.askyesno("It’s a tie", "No clear winner this time. Run another fresh round?", parent=self):
                self.pick_names()

    def clear_selected_round(self) -> None:
        if self.current_result is None:
            return
        selection = self.rounds_view.selection()
        if not selection:
            messagebox.showinfo("Select a round", "Select a round from the history first.", parent=self)
            return
        round_number = int(selection[0])
        if not messagebox.askyesno("Clear this round?", f"Remove round {round_number} from the scoreboard?", parent=self):
            return
        removed_round = next(round_result for round_result in self.current_result.rounds if round_result.round_number == round_number)
        self.all_time_scores[removed_round.winner] -= 1
        remaining = tuple(round_result for round_result in self.current_result.rounds if round_result.round_number != round_number)
        self._update_all_time_label()
        self._display_result(self._rebuild_result(remaining))

    def clear_all_rounds(self) -> None:
        if self.current_result is None or not self.current_result.rounds:
            return
        if not messagebox.askyesno("Clear all rounds?", "Reset all rounds and scores to zero?", parent=self):
            return
        self.current_result = None
        self.all_time_scores.clear()
        self.result_var.set("Ready when you are ✨")
        self._update_all_time_label()
        for item in self.scoreboard.get_children():
            self.scoreboard.delete(item)
        for item in self.rounds_view.get_children():
            self.rounds_view.delete(item)

    def _rebuild_result(self, rounds: tuple) -> SessionResult:
        scores = {name: 0 for name in self.current_result.scores}
        for round_result in rounds:
            scores[round_result.winner] += 1
        return SessionResult(self.current_result.seed, rounds, scores)

    def _add_to_all_time(self, scores: dict[str, int]) -> None:
        for name, score in scores.items():
            self.all_time_scores[name] = self.all_time_scores.get(name, 0) + score
        self._update_all_time_label()

    def _update_all_time_label(self) -> None:
        active_scores = {name: score for name, score in self.all_time_scores.items() if score > 0}
        if not active_scores:
            self.all_time_var.set("All-time winner: —")
            return
        highest = max(active_scores.values())
        leaders = [name for name, score in active_scores.items() if score == highest]
        if len(leaders) == 1:
            self.all_time_var.set(f"All-time winner: {leaders[0]} ({highest} wins)")
        else:
            self.all_time_var.set(f"All-time leaders: {', '.join(leaders)} ({highest} wins each)")

    def _update_best_of_label(self, *_: object) -> None:
        rounds = self.tries_var.get()
        noun = "round" if rounds == 1 else "rounds"
        self.best_of_var.set(f"Best-of-{rounds} {noun}")


def main() -> None:
    app = NamePickerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
