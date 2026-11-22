"""Modul ui: antarmuka grafis (GUI) Tkinter."""
import time
import tkinter as tk
from tkinter import ttk, messagebox

from .models import Wisata
from .services import ALGORITMA
from .validasi import KATEGORI_VALID

# Judul kolom yang tampil di tabel
JUDUL = {"id": "ID", "nama": "Nama Wisata", "kategori": "Kategori", "lokasi": "Lokasi",
         "harga_tiket": "Harga Tiket (Rp)", "rating": "Rating", "jam_buka": "Jam Buka"}


class FormWisata(tk.Toplevel):
    """Jendela dialog tambah / ubah data wisata."""

    def __init__(self, master, judul, id_awal, wisata=None, on_simpan=None):
        super().__init__(master)
        self.title(judul)
        self.resizable(False, False)
        self.on_simpan = on_simpan
        self.var = {f: tk.StringVar() for f in Wisata.FIELDS}
        awal = wisata.to_dict() if wisata else {"id": id_awal, "kategori": "Alam", "jam_buka": "08:00-17:00"}
        for k, v in awal.items():
            self.var[k].set(v)

        for baris, f in enumerate(Wisata.FIELDS):
            ttk.Label(self, text=JUDUL[f]).grid(row=baris, column=0, padx=10, pady=4, sticky="w")
            if f == "kategori":
                w = ttk.Combobox(self, textvariable=self.var[f], values=KATEGORI_VALID, state="readonly")
            else:
                w = ttk.Entry(self, textvariable=self.var[f], width=32,
                              state="readonly" if f == "id" else "normal")
            w.grid(row=baris, column=1, padx=10, pady=4)
        ttk.Button(self, text="Simpan", command=self._simpan).grid(row=len(Wisata.FIELDS), column=0, columnspan=2, pady=10)
        self.grab_set()  # modal

    def _simpan(self):
        """Mengirim data ke callback; error validasi ditampilkan sebagai pesan."""
        try:
            self.on_simpan({f: v.get() for f, v in self.var.items()})
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Input tidak valid", str(e), parent=self)


class AplikasiWisata:
    """Jendela utama: menu, pencarian, pengurutan, tabel, grafik, status bar."""

    def __init__(self, root, service, storage):
        self.root, self.service, self.storage = root, service, storage
        self.tampil = list(service.data)       # data yang sedang tampil di tabel
        self.urut_naik = True
        root.title("Sistem Informasi Wisata")
        root.geometry("1000x640")
        self._buat_menu()
        self._buat_toolbar()
        self._buat_tabel()
        self._buat_grafik()
        self.status = tk.StringVar()
        ttk.Label(root, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x", side="bottom")
        self.refresh()
        if storage.peringatan:
            self.status.set(storage.peringatan[0])

    # ---------- Pembentukan komponen ----------
    def _buat_menu(self):
        """Menu bar: File, Data, Bantuan."""
        bar = tk.Menu(self.root)
        m_file = tk.Menu(bar, tearoff=0)
        m_file.add_command(label="Simpan", command=self.simpan)
        m_file.add_separator()
        m_file.add_command(label="Keluar", command=self.root.destroy)
        m_data = tk.Menu(bar, tearoff=0)
        m_data.add_command(label="Tambah", command=self.tambah)
        m_data.add_command(label="Ubah", command=self.ubah)
        m_data.add_command(label="Hapus", command=self.hapus)
        m_bantu = tk.Menu(bar, tearoff=0)
        m_bantu.add_command(label="Tentang", command=lambda: messagebox.showinfo(
            "Tentang", "Sistem Informasi Wisata\nTugas UAS Pemrograman Python"))
        bar.add_cascade(label="File", menu=m_file)
        bar.add_cascade(label="Data", menu=m_data)
        bar.add_cascade(label="Bantuan", menu=m_bantu)
        self.root.config(menu=bar)

    def _buat_toolbar(self):
        """Baris kontrol: pencarian, filter, pengurutan, tombol aksi."""
        f = ttk.Frame(self.root, padding=6)
        f.pack(fill="x")
        # Pencarian
        ttk.Label(f, text="Cari:").grid(row=0, column=0)
        self.kata = tk.StringVar()
        e = ttk.Entry(f, textvariable=self.kata, width=22)
        e.grid(row=0, column=1, padx=3)
        e.bind("<Return>", lambda _e: self.cari())
        self.field = tk.StringVar(value="semua")
        ttk.Combobox(f, textvariable=self.field, width=9, state="readonly",
                     values=["semua", "id", "nama", "kategori", "lokasi"]).grid(row=0, column=2, padx=3)
        ttk.Button(f, text="Cari", command=self.cari).grid(row=0, column=3, padx=3)
        ttk.Button(f, text="Reset", command=self.reset).grid(row=0, column=4, padx=3)
        # Filter
        ttk.Label(f, text="Harga maks:").grid(row=0, column=5, padx=(15, 0))
        self.harga_max = tk.StringVar()
        ttk.Entry(f, textvariable=self.harga_max, width=10).grid(row=0, column=6, padx=3)
        ttk.Label(f, text="Rating min:").grid(row=0, column=7)
        self.rating_min = tk.StringVar()
        ttk.Entry(f, textvariable=self.rating_min, width=5).grid(row=0, column=8, padx=3)
        ttk.Button(f, text="Filter", command=self.filter).grid(row=0, column=9, padx=3)
        # Pengurutan
        ttk.Label(f, text="Urutkan:").grid(row=1, column=0, pady=6)
        self.kolom = tk.StringVar(value="nama")
        ttk.Combobox(f, textvariable=self.kolom, width=22, state="readonly",
                     values=list(Wisata.FIELDS)).grid(row=1, column=1, padx=3)
        self.arah = tk.StringVar(value="Naik (A-Z)")
        ttk.Combobox(f, textvariable=self.arah, width=9, state="readonly",
                     values=["Naik (A-Z)", "Turun (Z-A)"]).grid(row=1, column=2, padx=3)
        self.algo = tk.StringVar(value="Merge Sort")
        ttk.Combobox(f, textvariable=self.algo, width=11, state="readonly",
                     values=list(ALGORITMA)).grid(row=1, column=3, padx=3)
        ttk.Button(f, text="Urutkan", command=self.urutkan).grid(row=1, column=4, padx=3)
        # Aksi data
        ttk.Button(f, text="Tambah", command=self.tambah).grid(row=1, column=6)
        ttk.Button(f, text="Ubah", command=self.ubah).grid(row=1, column=7, columnspan=2)
        ttk.Button(f, text="Hapus", command=self.hapus).grid(row=1, column=9)

    def _buat_tabel(self):
        """Tabel data (Treeview) dengan scrollbar; klik header = urutkan kolom."""
        kerangka = ttk.Frame(self.root)
        kerangka.pack(fill="both", expand=True, padx=6)
        self.tree = ttk.Treeview(kerangka, columns=Wisata.FIELDS, show="headings", height=12)
        lebar = {"id": 60, "nama": 200, "kategori": 80, "lokasi": 160, "harga_tiket": 110, "rating": 60, "jam_buka": 110}
        for f in Wisata.FIELDS:
            # lambda dengan default argument agar tiap header memegang kolomnya sendiri
            self.tree.heading(f, text=JUDUL[f], command=lambda c=f: self.urut_header(c))
            self.tree.column(f, width=lebar[f], anchor="e" if f in ("harga_tiket", "rating") else "w")
        sb = ttk.Scrollbar(kerangka, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _buat_grafik(self):
        """Canvas untuk grafik batang jumlah wisata per kategori (visualisasi data)."""
        self.canvas = tk.Canvas(self.root, height=140, bg="white", highlightthickness=1)
        self.canvas.pack(fill="x", padx=6, pady=6)

    # ---------- Tampilan ----------
    def refresh(self, daftar=None):
        """Menampilkan daftar ke tabel, memperbarui grafik & status."""
        if daftar is not None:
            self.tampil = daftar
        self.tree.delete(*self.tree.get_children())
        for w in self.tampil:
            self.tree.insert("", "end", values=w.to_row())
        self._gambar_grafik()
        self.status.set(
            f"Tampil {len(self.tampil)} dari {len(self.service.data)} data | "
            f"Total tiket: Rp{self.service.total_harga(self.tampil):,} | "
            f"Rata-rata rating: {self.service.rata_rating(self.tampil)}")

    def _gambar_grafik(self):
        """Menggambar grafik batang sederhana dengan Canvas."""
        c = self.canvas
        c.delete("all")
        data = self.service.jumlah_per_kategori(self.tampil)
        c.create_text(8, 8, anchor="nw", text="Jumlah wisata per kategori", font=("Arial", 9, "bold"))
        if not data:
            return
        maks, lebar = max(data.values()), 80
        for i, (kat, jml) in enumerate(sorted(data.items())):
            x = 40 + i * (lebar + 30)
            tinggi = int(70 * jml / maks)
            c.create_rectangle(x, 110 - tinggi, x + lebar, 110, fill="#3b82f6", outline="")
            c.create_text(x + lebar / 2, 105 - tinggi, text=str(jml), anchor="s")
            c.create_text(x + lebar / 2, 122, text=kat)

    def _terpilih(self):
        """Mengembalikan ID baris yang dipilih, atau None dengan peringatan."""
        pilih = self.tree.selection()
        if not pilih:
            messagebox.showwarning("Pilih data", "Pilih satu baris pada tabel terlebih dahulu.")
            return None
        return str(self.tree.item(pilih[0])["values"][0])

    # ---------- Aksi ----------
    def cari(self):
        """Pencarian kata kunci pada seluruh data."""
        self.refresh(self.service.cari(self.kata.get(), self.field.get()))

    def filter(self):
        """Filter harga maksimum dan rating minimum (diteruskan sebagai **kwargs)."""
        try:
            kw = {}
            if self.harga_max.get().strip():
                kw["harga_max"] = int(self.harga_max.get())
            if self.rating_min.get().strip():
                kw["rating_min"] = float(self.rating_min.get())
        except ValueError:
            messagebox.showerror("Input tidak valid", "Harga dan rating harus berupa angka.")
            return
        self.refresh(self.service.filter_data(**kw))

    def urutkan(self, kolom=None):
        """Mengurutkan tabel yang sedang tampil dan menampilkan waktu proses."""
        kolom = kolom or self.kolom.get()
        mulai = time.perf_counter()
        hasil = self.service.urutkan(self.tampil, kolom,
                                     reverse=self.arah.get().startswith("Turun"),
                                     algoritma=self.algo.get())
        durasi = (time.perf_counter() - mulai) * 1000
        self.refresh(hasil)
        self.status.set(self.status.get() + f" | {self.algo.get()} {durasi:.3f} ms")

    def urut_header(self, kolom):
        """Klik header kolom: urutkan dan balik arah setiap klik."""
        self.kolom.set(kolom)
        self.arah.set("Naik (A-Z)" if self.urut_naik else "Turun (Z-A)")
        self.urut_naik = not self.urut_naik
        self.urutkan(kolom)

    def reset(self):
        """Mengembalikan tampilan ke seluruh data."""
        self.kata.set(""); self.harga_max.set(""); self.rating_min.set("")
        self.refresh(list(self.service.data))

    def simpan(self):
        """Menyimpan data ke file CSV."""
        try:
            self.storage.simpan(self.service.data)
            self.status.set("Data berhasil disimpan ke file.")
        except OSError as e:
            messagebox.showerror("Gagal menyimpan", str(e))

    def tambah(self):
        """Membuka form tambah data."""
        def simpan(data):
            self.service.tambah(**data)
            self.storage.catat_log(f"Tambah {data['id']}")
            self.simpan(); self.reset()
        FormWisata(self.root, "Tambah Wisata", self.service.id_berikutnya(), on_simpan=simpan)

    def ubah(self):
        """Membuka form ubah data untuk baris terpilih."""
        id_w = self._terpilih()
        if id_w is None:
            return
        def simpan(data):
            self.service.ubah(id_w, **data)
            self.storage.catat_log(f"Ubah {id_w}")
            self.simpan(); self.reset()
        FormWisata(self.root, "Ubah Wisata", id_w, self.service.cari_id(id_w), simpan)

    def hapus(self):
        """Menghapus baris terpilih setelah konfirmasi."""
        id_w = self._terpilih()
        if id_w and messagebox.askyesno("Konfirmasi", f"Hapus data {id_w}?"):
            self.service.hapus(id_w)
            self.storage.catat_log(f"Hapus {id_w}")
            self.simpan(); self.reset()
