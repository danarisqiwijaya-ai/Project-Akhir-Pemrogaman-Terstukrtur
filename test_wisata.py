"""Unit test (unittest) untuk logika data, searching, sorting, dan file handling.

Berjalan terpisah dari UI.  Jalankan:  python -m unittest -v
"""
import os
import tempfile
import unittest

from wisata.models import Wisata
from wisata.services import WisataService, bubble_sort, merge_sort
from wisata.storage import WisataStorage
from wisata.validasi import validasi_wisata


def buat_data():
    """Data contoh kecil untuk pengujian."""
    return [
        Wisata("W001", "Borobudur", "Budaya", "Magelang", 50000, 4.8),
        Wisata("W002", "Pantai Kuta", "Bahari", "Bali", 0, 4.3),
        Wisata("W003", "Kawah Putih", "Alam", "Bandung", 28000, 4.5),
        Wisata("W004", "Bromo", "Alam", "Probolinggo", 35000, 4.8),
    ]


class TestWisata(unittest.TestCase):
    """Kumpulan test untuk validasi, service, algoritma, dan storage."""

    def setUp(self):
        self.service = WisataService(buat_data())

    def test_validasi_harga_negatif(self):
        """Harga negatif harus memunculkan ValueError."""
        with self.assertRaises(ValueError):
            validasi_wisata(id="W9", nama="X", kategori="Alam", lokasi="Y", harga_tiket=-1, rating=4)

    def test_validasi_field_kosong(self):
        """Nama kosong harus ditolak."""
        with self.assertRaises(ValueError):
            validasi_wisata(id="W9", nama="  ", kategori="Alam", lokasi="Y", harga_tiket=1, rating=4)

    def test_cari_kata_kunci(self):
        """Pencarian 'alam' pada kategori menghasilkan 2 data."""
        hasil = self.service.cari("alam", "kategori")
        self.assertEqual({w.id for w in hasil}, {"W003", "W004"})

    def test_cari_id_biner(self):
        """Binary search menemukan ID yang ada & mengembalikan None bila tidak ada."""
        self.assertEqual(self.service.cari_id("w003").nama, "Kawah Putih")
        self.assertIsNone(self.service.cari_id("W999"))

    def test_merge_sort_harga(self):
        """Merge sort mengurutkan harga naik & turun dengan benar."""
        naik = self.service.urutkan(self.service.data, "harga_tiket", False, "Merge Sort")
        self.assertEqual([w.harga_tiket for w in naik], [0, 28000, 35000, 50000])
        turun = self.service.urutkan(self.service.data, "harga_tiket", True, "Merge Sort")
        self.assertEqual([w.harga_tiket for w in turun], [50000, 35000, 28000, 0])

    def test_bubble_dan_merge_sama(self):
        """Hasil bubble sort (lama) dan merge sort (refactor) harus identik."""
        a = bubble_sort(self.service.data, key=lambda w: w.nama)
        b = merge_sort(self.service.data, key=lambda w: w.nama)
        self.assertEqual([w.id for w in a], [w.id for w in b])

    def test_filter_kwargs_dan_total_args(self):
        """filter_data (**kwargs) dan hitung_total (*args) bekerja benar."""
        murah = self.service.filter_data(harga_max=30000, rating_min=4.4)
        self.assertEqual([w.id for w in murah], ["W003"])
        self.assertEqual(WisataService.hitung_total(1000, 2000, 3000), 6000)

    def test_simpan_dan_muat_file(self):
        """Data yang disimpan ke CSV bisa dimuat ulang tanpa berubah."""
        with tempfile.TemporaryDirectory() as folder:
            st = WisataStorage(os.path.join(folder, "t.csv"))
            st.simpan(self.service.data)
            muat = st.muat()
            self.assertEqual([w.to_dict() for w in muat], [w.to_dict() for w in self.service.data])

    def test_file_hilang_dan_corrupt(self):
        """File hilang dibuat ulang; baris rusak dilewati tanpa crash."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "x.csv")
            st = WisataStorage(path)
            self.assertEqual(st.muat(), [])          # FileNotFoundError ditangani
            self.assertTrue(os.path.exists(path))
            with open(path, "a", encoding="utf-8") as f:   # tambah baris rusak
                f.write("W001,A,Alam,B,abc,4,08:00\n")
            self.assertEqual(st.muat(), [])
            self.assertTrue(st.peringatan)


if __name__ == "__main__":
    unittest.main()
