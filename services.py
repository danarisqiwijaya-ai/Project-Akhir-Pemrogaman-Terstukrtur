"""Modul services: logika pengolahan data (CRUD, searching, sorting, filter)."""
from .models import Wisata
from .validasi import validasi_wisata


# ---------------------------------------------------------------------------
# Algoritma pengurutan
# ---------------------------------------------------------------------------
def bubble_sort(data, key=lambda x: x, reverse=False):
    """Bubble Sort O(n^2) - versi AWAL sebelum refactoring (dipertahankan untuk perbandingan)."""
    hasil = list(data)  # salin agar data asli tidak berubah
    n = len(hasil)
    for i in range(n):
        for j in range(0, n - i - 1):
            a, b = key(hasil[j]), key(hasil[j + 1])
            if (a < b) if reverse else (a > b):
                hasil[j], hasil[j + 1] = hasil[j + 1], hasil[j]
    return hasil


def merge_sort(data, key=lambda x: x, reverse=False):
    """Merge Sort O(n log n) - hasil REFACTORING dari bubble sort. Stabil."""
    if len(data) <= 1:
        return list(data)
    tengah = len(data) // 2
    kiri = merge_sort(data[:tengah], key, reverse)
    kanan = merge_sort(data[tengah:], key, reverse)

    hasil, i, j = [], 0, 0
    while i < len(kiri) and j < len(kanan):
        a, b = key(kiri[i]), key(kanan[j])
        # ambil dari kiri jika urutannya sudah benar (<= menjaga kestabilan)
        ambil_kiri = (a >= b) if reverse else (a <= b)
        if ambil_kiri:
            hasil.append(kiri[i]); i += 1
        else:
            hasil.append(kanan[j]); j += 1
    hasil.extend(kiri[i:])
    hasil.extend(kanan[j:])
    return hasil


ALGORITMA = {"Merge Sort": merge_sort, "Bubble Sort": bubble_sort}


class WisataService:
    """Mengelola daftar objek Wisata beserta operasi pencarian & pengurutan."""

    def __init__(self, data=None):
        self.data = list(data) if data else []

    # ---------------- CRUD ----------------
    def id_berikutnya(self):
        """Membuat ID otomatis, contoh W019 (angka terbesar + 1)."""
        angka = [int(w.id[1:]) for w in self.data if w.id[1:].isdigit()]
        return f"W{(max(angka) + 1) if angka else 1:03d}"

    def tambah(self, **kwargs):
        """Menambah data baru. Menerima field sebagai keyword argument (**kwargs)."""
        bersih = validasi_wisata(**kwargs)
        if any(w.id == bersih["id"] for w in self.data):
            raise ValueError(f"ID {bersih['id']} sudah dipakai")
        wisata = Wisata.from_dict(bersih)
        self.data.append(wisata)
        return wisata

    def ubah(self, id_wisata, **kwargs):
        """Mengubah data berdasarkan ID."""
        lama = self.cari_id(id_wisata)
        if lama is None:
            raise ValueError(f"ID {id_wisata} tidak ditemukan")
        bersih = validasi_wisata(**{**lama.to_dict(), **kwargs, "id": lama.id})
        for k, v in bersih.items():
            setattr(lama, k, v)
        return lama

    def hapus(self, id_wisata):
        """Menghapus data berdasarkan ID."""
        target = self.cari_id(id_wisata)
        if target is None:
            raise ValueError(f"ID {id_wisata} tidak ditemukan")
        self.data.remove(target)

    # ---------------- Searching ----------------
    def cari(self, keyword, field="semua", sumber=None):
        """Linear search kata kunci (tidak peka huruf besar/kecil).

        Args:
            keyword: kata yang dicari (substring).
            field: 'nama', 'id', 'kategori', 'lokasi' atau 'semua'.
            sumber: daftar yang dicari (default seluruh data).
        """
        sumber = self.data if sumber is None else sumber
        kata = str(keyword).strip().lower()
        if not kata:
            return list(sumber)
        kolom = ["id", "nama", "kategori", "lokasi"] if field == "semua" else [field]
        return [w for w in sumber
                if any(kata in str(getattr(w, k)).lower() for k in kolom)]

    def cari_id(self, id_wisata):
        """Binary search ID persis. Data diurutkan dulu berdasarkan ID."""
        terurut = merge_sort(self.data, key=lambda w: w.id)
        target = str(id_wisata).strip().upper()
        kiri, kanan = 0, len(terurut) - 1
        while kiri <= kanan:
            tengah = (kiri + kanan) // 2
            if terurut[tengah].id == target:
                return terurut[tengah]
            if terurut[tengah].id < target:
                kiri = tengah + 1
            else:
                kanan = tengah - 1
        return None

    # ---------------- Sorting ----------------
    @staticmethod
    def urutkan(data, kolom, reverse=False, algoritma="Merge Sort"):
        """Mengurutkan daftar berdasarkan kolom dengan algoritma pilihan.

        Key memakai lambda; teks dibandingkan tanpa peka huruf besar/kecil.
        """
        fungsi = ALGORITMA[algoritma]
        return fungsi(
            data,
            key=lambda w: (getattr(w, kolom).lower()
                           if isinstance(getattr(w, kolom), str) else getattr(w, kolom)),
            reverse=reverse,
        )

    # ---------------- Filter & agregat ----------------
    def filter_data(self, sumber=None, **filters):
        """Menyaring data dengan filter variatif (**kwargs).

        Filter yang didukung: kategori, harga_max, rating_min, lokasi.
        """
        hasil = list(self.data if sumber is None else sumber)
        if filters.get("kategori"):
            hasil = [w for w in hasil if w.kategori.lower() == filters["kategori"].lower()]
        if filters.get("lokasi"):
            hasil = [w for w in hasil if filters["lokasi"].lower() in w.lokasi.lower()]
        if filters.get("harga_max") is not None:
            hasil = [w for w in hasil if w.harga_tiket <= filters["harga_max"]]
        if filters.get("rating_min") is not None:
            hasil = [w for w in hasil if w.rating >= filters["rating_min"]]
        return hasil

    @staticmethod
    def hitung_total(*args):
        """Menjumlahkan sejumlah nilai (*args), contoh: hitung_total(10000, 25000)."""
        return sum(args)

    def total_harga(self, daftar=None):
        """Total harga tiket dari daftar wisata (memakai *args)."""
        daftar = self.data if daftar is None else daftar
        return self.hitung_total(*[w.harga_tiket for w in daftar])

    def rata_rating(self, daftar=None):
        """Rata-rata rating dari daftar wisata."""
        daftar = self.data if daftar is None else daftar
        return round(sum(w.rating for w in daftar) / len(daftar), 2) if daftar else 0.0

    def jumlah_per_kategori(self, daftar=None):
        """Dictionary kategori -> jumlah (untuk visualisasi grafik)."""
        daftar = self.data if daftar is None else daftar
        hasil = {}
        for w in daftar:
            hasil[w.kategori] = hasil.get(w.kategori, 0) + 1
        return hasil
