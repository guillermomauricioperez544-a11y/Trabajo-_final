"""Punto de entrada: ejecuta  python src/main.py"""
import tkinter as tk
from interfaz import App


def main():
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
