"""Modul validasi: memeriksa input sebelum masuk ke data."""

KATEGORI_VALID = ("Alam", "Budaya", "Bahari", "Kuliner", "Buatan")


def validasi_wisata(**data):
    """Memvalidasi dan membersihkan data wisata.

    Menggunakan **kwargs agar bisa menerima dict dari form UI maupun baris CSV.

    Raises:
        ValueError: bila field wajib kosong, harga negatif, rating di luar 0-5,
                    atau kategori tidak dikenal.

    Returns:
        dict data yang sudah dibersihkan dengan tipe yang benar.
    """
    # Field wajib diisi -> raise ValueError
    for field in ("id", "nama", "kategori", "lokasi"):
        if not str(data.get(field, "")).strip():
            raise ValueError(f"Field '{field}' wajib diisi")

    kategori = str(data["kategori"]).strip().title()
    if kategori not in KATEGORI_VALID:
        raise ValueError(f"Kategori harus salah satu dari: {', '.join(KATEGORI_VALID)}")

    # Konversi tipe angka; kegagalan diubah menjadi pesan yang ramah
    try:
        harga = int(float(str(data.get("harga_tiket", "")).strip()))
    except ValueError:
        raise ValueError("Harga tiket harus berupa angka")
    try:
        rating = float(str(data.get("rating", "")).strip())
    except ValueError:
        raise ValueError("Rating harus berupa angka")

    # Batas nilai input
    if harga < 0:
        raise ValueError("Harga tiket tidak boleh negatif")
    if not 0 <= rating <= 5:
        raise ValueError("Rating harus antara 0 sampai 5")

    # assert sebagai pengaman internal (invarian setelah validasi)
    assert harga >= 0 and 0 <= rating <= 5, "Invarian data dilanggar"

    return {
        "id": str(data["id"]).strip().upper(),
        "nama": str(data["nama"]).strip(),
        "kategori": kategori,
        "lokasi": str(data["lokasi"]).strip(),
        "harga_tiket": harga,
        "rating": rating,
        "jam_buka": str(data.get("jam_buka") or "08:00-17:00").strip(),
    }
