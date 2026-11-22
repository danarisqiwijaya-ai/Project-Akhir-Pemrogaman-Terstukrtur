"""Modul storage: penyimpanan permanen data tabular ke file CSV."""
import csv
import os
from datetime import datetime

from .models import Wisata
from .validasi import validasi_wisata


class WisataStorage:
    """Mengelola baca/tulis file CSV dan file log.

    Seluruh operasi file memakai context manager `with open()`.
    """

    def __init__(self, path, log_path=None):
        self.path = path
        self.log_path = log_path or os.path.join(os.path.dirname(path) or ".", "log.txt")
        self.peringatan = []  # daftar pesan baris rusak saat muat

    def buat_file_kosong(self):
        """Membuat file CSV baru berisi header saja (mode 'x': gagal bila sudah ada)."""
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        try:
            with open(self.path, "x", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=Wisata.FIELDS).writeheader()
        except FileExistsError:
            pass  # sudah ada, tidak perlu dibuat

    def muat(self):
        """Memuat data dari CSV (mode 'r').

        - File hilang  -> dibuat baru (FileNotFoundError ditangani).
        - Header rusak / baris tidak valid -> ValueError ditangani, baris dilewati.
        UI tidak akan crash meskipun file corrupt.
        """
        data, self.peringatan = [], []
        try:
            with open(self.path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames != Wisata.FIELDS:
                    raise ValueError("Header CSV tidak sesuai format")
                for no, row in enumerate(reader, start=2):
                    try:
                        data.append(Wisata.from_dict(validasi_wisata(**row)))
                    except (ValueError, TypeError, KeyError) as e:
                        self.peringatan.append(f"Baris {no} dilewati: {e}")
        except FileNotFoundError:
            self.buat_file_kosong()
            self.peringatan.append("File data tidak ditemukan, dibuat file baru.")
        except ValueError as e:
            self.peringatan.append(f"File corrupt: {e}")
            data = []
        for p in self.peringatan:
            self.catat_log(p)
        return data

    def simpan(self, data):
        """Menyimpan seluruh data ke CSV (mode 'w' menimpa isi lama)."""
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=Wisata.FIELDS)
            writer.writeheader()
            for w in data:
                writer.writerow(w.to_dict())

    def catat_log(self, pesan):
        """Menambah satu baris log di akhir file (mode 'a')."""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {pesan}\n")
        except OSError:
            pass  # gagal log tidak boleh menghentikan aplikasi
