import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

conn = sqlite3.connect('kullanicilar.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Kullanici (
                    id INTEGER PRIMARY KEY,
                    kullanici_adi TEXT UNIQUE,
                    sifre TEXT)''')
conn.commit()

current_user = None
comparison_results = []

def kullanici_giris():
    global current_user
    kullanici_adi = kullanici_adi_entry.get()
    sifre = sifre_entry.get()
    
    cursor.execute("SELECT * FROM Kullanici WHERE kullanici_adi=? AND sifre=?", (kullanici_adi, sifre))
    sonuc = cursor.fetchone()
    
    if sonuc:
        current_user = kullanici_adi
        messagebox.showinfo("Başarılı", "Giriş başarılı!")
        ana_menu()
    else:
        messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış!")

def kullanici_kayit():
    kullanici_adi = kullanici_adi_entry.get()
    sifre = sifre_entry.get()
    
    try:
        cursor.execute("INSERT INTO Kullanici (kullanici_adi, sifre) VALUES (?, ?)", (kullanici_adi, sifre))
        conn.commit()
        messagebox.showinfo("Başarılı", "Kayıt başarılı!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Hata", "Bu kullanıcı adı zaten var!")

def sifre_guncelle():
    kullanici_adi = current_user
    mevcut_sifre = mevcut_sifre_entry.get()
    yeni_sifre = yeni_sifre_entry.get()
    
    cursor.execute("SELECT * FROM Kullanici WHERE kullanici_adi=? AND sifre=?", (kullanici_adi, mevcut_sifre))
    sonuc = cursor.fetchone()
    
    if sonuc:
        cursor.execute("UPDATE Kullanici SET sifre=? WHERE kullanici_adi=?", (yeni_sifre, kullanici_adi))
        conn.commit()
        messagebox.showinfo("Başarılı", "Şifre güncellendi!")
        ana_menu()
    else:
        messagebox.showerror("Hata", "Mevcut şifre yanlış!")

def metin_karsilastir(algoritma):
    dosya1 = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    dosya2 = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    
    if not dosya1 or not dosya2:
        return
    
    with open(dosya1, 'r', encoding='utf-8') as file:
        metin1 = file.read()
    with open(dosya2, 'r', encoding='utf-8') as file:
        metin2 = file.read()
    
    if algoritma == "cosine":
        sonuc = cosine_benzerlik(metin1, metin2)
        algoritma_adi = "Cosine Similarity"
    elif algoritma == "jaccard":
        sonuc = jaccard_benzerlik(metin1, metin2)
        algoritma_adi = "Jaccard Benzerlik Katsayısı"
    elif algoritma == "levenshtein":
        sonuc = levenshtein_benzerlik(metin1, metin2)
        algoritma_adi = "Levenshtein Mesafesi"
    
    sonuc_metni = f"{algoritma_adi} ile {dosya1} ve {dosya2} karşılaştırma sonucu: %{sonuc:.2f}\n"
    comparison_results.append(sonuc_metni)
    guncelle_sonuclar()

def cosine_benzerlik(metin1, metin2):
    tfidf_vectorizer = TfidfVectorizer().fit_transform([metin1, metin2])
    benzerlik = cosine_similarity(tfidf_vectorizer[0:1], tfidf_vectorizer[1:2])
    return benzerlik[0][0] * 100

def jaccard_benzerlik(metin1, metin2):
    set1 = set(metin1.split())
    set2 = set(metin2.split())
    kesişim = set1.intersection(set2)
    birleşim = set1.union(set2)
    return len(kesişim) / len(birleşim) * 100

def levenshtein_benzerlik(metin1, metin2):
    def levenshtein(metin1, metin2):
        if len(metin1) < len(metin2):
            return levenshtein(metin2, metin1)
        
        if len(metin2) == 0:
            return len(metin1)
        
        previous_row = range(len(metin2) + 1)
        for i, c1 in enumerate(metin1):
            current_row = [i + 1]
            for j, c2 in enumerate(metin2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    levenshtein_distance = levenshtein(metin1, metin2)
    max_len = max(len(metin1), len(metin2))
    return (1 - levenshtein_distance / max_len) * 100

def ana_menu():
    for widget in root.winfo_children():
        widget.destroy()
    
    menu = tk.Menu(root)
    root.config(menu=menu)
    
    karsilastir_menu = tk.Menu(menu)
    menu.add_cascade(label="Karşılaştır", menu=karsilastir_menu)
    karsilastir_menu.add_command(label="Metni Cosine Similarity ile karşılaştır", command=lambda: metin_karsilastir("cosine"))
    karsilastir_menu.add_command(label="Metni Jaccard Benzerlik Katsayısı ile karşılaştır", command=lambda: metin_karsilastir("jaccard"))
    karsilastir_menu.add_command(label="Metni Levenshtein Mesafesi ile karşılaştır", command=lambda: metin_karsilastir("levenshtein"))
    
    islemler_menu = tk.Menu(menu)
    menu.add_cascade(label="İşlemler", menu=islemler_menu)
    sifre_menu = tk.Menu(islemler_menu)
    islemler_menu.add_cascade(label="Şifre", menu=sifre_menu)
    sifre_menu.add_command(label="Değiştir", command=sifre_degistir_ekrani)
    
    menu.add_command(label="Çıkış", command=root.quit)
    
    global results_text
    results_text = tk.Text(root, height=15, width=80)
    results_text.pack()
    guncelle_sonuclar()

def guncelle_sonuclar():
    results_text.config(state=tk.NORMAL)
    results_text.delete(1.0, tk.END)
    for result in comparison_results:
        results_text.insert(tk.END, result)
    results_text.config(state=tk.DISABLED)

def sifre_degistir_ekrani():
    for widget in root.winfo_children():
        widget.destroy()
    
    tk.Label(root, text="Mevcut Şifre:").pack()
    global mevcut_sifre_entry
    mevcut_sifre_entry = tk.Entry(root, show="*")
    mevcut_sifre_entry.pack()

    tk.Label(root, text="Yeni Şifre:").pack()
    global yeni_sifre_entry
    yeni_sifre_entry = tk.Entry(root, show="*")
    yeni_sifre_entry.pack()
    
    tk.Button(root, text="Güncelle", command=sifre_guncelle).pack()
    tk.Button(root, text="Geri", command=ana_menu).pack()

# Giriş ekranı
root = tk.Tk()
root.title("Kullanıcı Girişi")

tk.Label(root, text="Kullanıcı Adı:").pack()
kullanici_adi_entry = tk.Entry(root)
kullanici_adi_entry.pack()

tk.Label(root, text="Şifre:").pack()
sifre_entry = tk.Entry(root, show="*")
sifre_entry.pack()

tk.Button(root, text="Giriş Yap", command=kullanici_giris).pack()
tk.Button(root, text="Kaydol", command=kullanici_kayit).pack()

root.mainloop()
