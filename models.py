"""Modul models: berisi class Wisata sebagai representasi satu baris data."""


class Wisata:
    """Objek satu destinasi wisata."""

    # Urutan kolom (dipakai sebagai header CSV dan kolom tabel UI)
    FIELDS = ["id", "nama", "kategori", "lokasi", "harga_tiket", "rating", "jam_buka"]

    def __init__(self, id, nama, kategori, lokasi, harga_tiket, rating, jam_buka="08:00-17:00"):
        """Membuat objek wisata.

        Args:
            id: kode unik, contoh 'W001'.
            nama: nama destinasi.
            kategori: Alam / Budaya / Bahari / Kuliner / Buatan.
            lokasi: kota/provinsi.
            harga_tiket: harga tiket (Rupiah, int).
            rating: nilai 0-5 (float).
            jam_buka: teks jam operasional.
        """
        self.id = id
        self.nama = nama
        self.kategori = kategori
        self.lokasi = lokasi
        self.harga_tiket = harga_tiket
        self.rating = rating
        self.jam_buka = jam_buka

    def to_dict(self):
        """Mengubah objek menjadi dictionary (untuk ditulis ke CSV)."""
        return {f: getattr(self, f) for f in self.FIELDS}

    def to_row(self):
        """Mengubah objek menjadi tuple nilai (untuk baris Treeview)."""
        return tuple(getattr(self, f) for f in self.FIELDS)

    @classmethod
    def from_dict(cls, data):
        """Membuat objek Wisata dari dictionary yang sudah tervalidasi."""
        return cls(**{f: data[f] for f in cls.FIELDS})

    def __repr__(self):
        return f"Wisata({self.id}, {self.nama}, {self.kategori})"
