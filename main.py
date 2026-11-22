"""Titik masuk aplikasi Sistem Informasi Wisata.

Jalankan:  python main.py
"""
import os

from wisata.storage import WisataStorage
from wisata.services import WisataService


def main():
    """Memuat data dari CSV lalu menjalankan UI."""
    import tkinter as tk
    from wisata.ui import AplikasiWisata

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "wisata.csv")
    storage = WisataStorage(path)
    service = WisataService(storage.muat())
    root = tk.Tk()
    AplikasiWisata(root, service, storage)
    root.mainloop()


if __name__ == "__main__":
    main()
