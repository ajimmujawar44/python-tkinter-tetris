"""Dark-themed desktop calculator built with Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont


COLORS = {
    "bg": "#121417",
    "panel": "#1b1f24",
    "display": "#0e1114",
    "text": "#f3f5f7",
    "muted": "#8b939c",
    "number": "#2a3038",
    "number_hover": "#353c46",
    "op": "#2d5aa0",
    "op_hover": "#3669b8",
    "accent": "#e07a3d",
    "accent_hover": "#ef8b4e",
    "util": "#3a414b",
    "util_hover": "#4a5260",
}


class Calculator(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Calculator")
        self.configure(bg=COLORS["bg"])
        self.resizable(False, False)

        self.expression = ""
        self.just_evaluated = False

        self.display_font = tkfont.Font(family="Segoe UI", size=28, weight="bold")
        self.preview_font = tkfont.Font(family="Segoe UI", size=11)
        self.button_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")

        self._build_ui()
        self._bind_keys()
        self.update_idletasks()
        self._center_window()

    def _center_window(self) -> None:
        width, height = 340, 520
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self) -> None:
        shell = tk.Frame(self, bg=COLORS["bg"], padx=16, pady=16)
        shell.pack(fill="both", expand=True)

        display = tk.Frame(shell, bg=COLORS["display"], padx=16, pady=18)
        display.pack(fill="x", pady=(0, 14))

        self.preview_var = tk.StringVar(value="")
        tk.Label(
            display,
            textvariable=self.preview_var,
            anchor="e",
            bg=COLORS["display"],
            fg=COLORS["muted"],
            font=self.preview_font,
        ).pack(fill="x")

        self.value_var = tk.StringVar(value="0")
        tk.Label(
            display,
            textvariable=self.value_var,
            anchor="e",
            bg=COLORS["display"],
            fg=COLORS["text"],
            font=self.display_font,
        ).pack(fill="x")

        grid = tk.Frame(shell, bg=COLORS["bg"])
        grid.pack(fill="both", expand=True)

        buttons = [
            ("C", self.clear, "util"),
            ("⌫", self.backspace, "util"),
            ("%", self.percent, "util"),
            ("÷", lambda: self.input_operator("/"), "op"),
            ("7", lambda: self.input_digit("7"), "number"),
            ("8", lambda: self.input_digit("8"), "number"),
            ("9", lambda: self.input_digit("9"), "number"),
            ("×", lambda: self.input_operator("*"), "op"),
            ("4", lambda: self.input_digit("4"), "number"),
            ("5", lambda: self.input_digit("5"), "number"),
            ("6", lambda: self.input_digit("6"), "number"),
            ("−", lambda: self.input_operator("-"), "op"),
            ("1", lambda: self.input_digit("1"), "number"),
            ("2", lambda: self.input_digit("2"), "number"),
            ("3", lambda: self.input_digit("3"), "number"),
            ("+", lambda: self.input_operator("+"), "op"),
            ("±", self.toggle_sign, "number"),
            ("0", lambda: self.input_digit("0"), "number"),
            (".", self.input_dot, "number"),
            ("=", self.evaluate, "accent"),
        ]

        for index, (label, command, kind) in enumerate(buttons):
            row, col = divmod(index, 4)
            self._make_button(grid, label, command, kind).grid(
                row=row, column=col, sticky="nsew", padx=5, pady=5
            )

        for i in range(4):
            grid.columnconfigure(i, weight=1)
        for i in range(5):
            grid.rowconfigure(i, weight=1)

    def _make_button(self, parent: tk.Frame, text: str, command, kind: str) -> tk.Button:
        bg = COLORS[kind]
        hover = COLORS[f"{kind}_hover"]
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.button_font,
            bg=bg,
            fg=COLORS["text"],
            activebackground=hover,
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        button.bind("<Enter>", lambda _e, b=button, c=hover: b.configure(bg=c))
        button.bind("<Leave>", lambda _e, b=button, c=bg: b.configure(bg=c))
        return button

    def _bind_keys(self) -> None:
        for digit in "0123456789":
            self.bind(digit, lambda e, d=digit: self.input_digit(d))
        for key, op in [("+", "+"), ("-", "-"), ("*", "*"), ("/", "/")]:
            self.bind(key, lambda e, o=op: self.input_operator(o))
        self.bind(".", lambda _e: self.input_dot())
        self.bind("<Return>", lambda _e: self.evaluate())
        self.bind("<KP_Enter>", lambda _e: self.evaluate())
        self.bind("=", lambda _e: self.evaluate())
        self.bind("<BackSpace>", lambda _e: self.backspace())
        self.bind("<Escape>", lambda _e: self.clear())
        self.bind("%", lambda _e: self.percent())

    def _refresh(self) -> None:
        self.preview_var.set(self._pretty(self.expression) if self.expression else "")
        shown = self.expression.split(" ")[-1] if self.expression else "0"
        self.value_var.set(shown)

    def _pretty(self, text: str) -> str:
        return text.replace("*", "×").replace("/", "÷").replace("-", "−")

    def input_digit(self, digit: str) -> None:
        if self.just_evaluated:
            self.expression = ""
            self.just_evaluated = False
        parts = self.expression.split(" ")
        current = parts[-1] if parts else ""
        if current == "0":
            parts[-1] = digit
            self.expression = " ".join(parts).strip()
        else:
            self.expression += digit
        self._refresh()

    def input_dot(self) -> None:
        if self.just_evaluated:
            self.expression = "0"
            self.just_evaluated = False
        parts = self.expression.split(" ")
        current = parts[-1] if self.expression else ""
        if current in ("", "+", "-", "*", "/"):
            self.expression += "0."
        elif "." not in current:
            self.expression += "."
        self._refresh()

    def input_operator(self, operator: str) -> None:
        self.just_evaluated = False
        if not self.expression:
            self.expression = "0"
        if self.expression.endswith(" "):
            self.expression = self.expression[:-3] + f" {operator} "
        else:
            self.expression += f" {operator} "
        self._refresh()

    def toggle_sign(self) -> None:
        if not self.expression or self.expression.endswith(" "):
            return
        parts = self.expression.split(" ")
        token = parts[-1]
        if token.startswith("-"):
            parts[-1] = token[1:]
        else:
            parts[-1] = f"-{token}"
        self.expression = " ".join(parts)
        self._refresh()

    def percent(self) -> None:
        if not self.expression or self.expression.endswith(" "):
            return
        parts = self.expression.split(" ")
        try:
            parts[-1] = str(float(parts[-1]) / 100)
            self.expression = " ".join(parts)
            self._refresh()
        except ValueError:
            self.value_var.set("Error")

    def backspace(self) -> None:
        self.just_evaluated = False
        if self.expression.endswith(" "):
            self.expression = self.expression[:-3]
        else:
            self.expression = self.expression[:-1]
        self._refresh()

    def clear(self) -> None:
        self.expression = ""
        self.just_evaluated = False
        self._refresh()

    def evaluate(self) -> None:
        if not self.expression:
            return
        expr = self.expression.rstrip(" +-*/")
        try:
            result = eval(expr, {"__builtins__": {}}, {})
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.preview_var.set(self._pretty(expr) + " =")
            self.expression = str(result)
            self.value_var.set(self.expression)
            self.just_evaluated = True
        except Exception:
            self.value_var.set("Error")
            self.expression = ""
            self.just_evaluated = False


if __name__ == "__main__":
    Calculator().mainloop()
