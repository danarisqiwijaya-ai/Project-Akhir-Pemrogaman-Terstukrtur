# Sistem Informasi Wisata (Tugas UAS Pemrograman Python)

## Cara Menjalankan
```
python main.py              # menjalankan aplikasi (butuh Tkinter, bawaan Python)
python -m unittest -v       # menjalankan unit test
```
Linux: bila Tkinter belum ada -> `sudo apt install python3-tk`.

## Struktur Package
| File | Fungsi |
|---|---|
| main.py | Titik masuk aplikasi |
| wisata/models.py | Class `Wisata` |
| wisata/validasi.py | Validasi input (`raise ValueError`, `assert`) |
| wisata/storage.py | Class `WisataStorage` - baca/tulis CSV (`with open`, mode r/w/a/x) |
| wisata/services.py | Class `WisataService` - CRUD, searching, sorting, filter (*args, **kwargs, lambda) |
| wisata/ui.py | Class `AplikasiWisata` & `FormWisata` - GUI Tkinter |
| tests/test_wisata.py | Unit test (1 class, 9 fungsi uji) |
| data/wisata.csv | Data tabular (18 destinasi) |

## Data (untuk Bab "Data" di laporan)
Tema: **Destinasi wisata Indonesia**. Format: CSV UTF-8 dengan header.

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | teks | Kode unik, contoh W001 |
| nama | teks | Nama destinasi |
| kategori | teks | Alam / Budaya / Bahari / Kuliner / Buatan |
| lokasi | teks | Kota - Provinsi |
| harga_tiket | integer | Rupiah, >= 0 |
| rating | float | 0 - 5 |
| jam_buka | teks | Jam operasional |

## Fitur
- Tabel data + grafik batang jumlah wisata per kategori (Canvas).
- Searching: kata kunci (linear search) per kolom/semua kolom; pencarian ID memakai binary search.
- Sorting: Merge Sort / Bubble Sort, pilih lewat combobox atau klik header kolom.
- Filter harga maksimum dan rating minimum.
- Tambah / Ubah / Hapus data, otomatis tersimpan ke CSV; log aktivitas di `data/log.txt`.
- File hilang dibuat ulang, baris corrupt dilewati (UI tidak crash).

## Tabel Refactoring Kode
| No | Sebelum | Sesudah | Manfaat |
|---|---|---|---|
| 1 | Pengurutan dengan Bubble Sort O(n^2) | Diganti Merge Sort O(n log n) (`merge_sort`), bubble sort tetap disimpan untuk perbandingan; waktu proses tampil di status bar | Lebih cepat untuk data besar, stabil |
| 2 | Validasi input tersebar di UI dan service | Dipusatkan di `validasi.py` (`validasi_wisata`) | Tidak ada duplikasi, mudah diuji |
| 3 | Pencarian ID memakai loop linear | Diganti Binary Search pada data terurut (`cari_id`) | Kompleksitas pencarian O(log n) |
| 4 | Satu file besar berisi UI, data, dan file | Dipecah menjadi modul models/storage/services/validasi/ui | Modular, UI terpisah dari logika sehingga bisa di-unit-test |
| 5 | Banyak parameter filter yang dituliskan satu per satu | Memakai `**kwargs` pada `filter_data` dan `*args` pada `hitung_total` | Fungsi fleksibel, mudah ditambah filter baru |


