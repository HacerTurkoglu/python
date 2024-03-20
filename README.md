frekanslar = {}
def selamla():
    print("HEllO WORLDD:D")
    isim=input("isminiz nedir")
    no=input("öğrenci numaranız nedir?")
    note=input("önceki ödev notunuz nedir?")
    print("merhaba ben {} numaralı öğrenci {} önceki ödev notum {}".format(no,isim,note))
    
    
def kucuk_yap(metin):
    metin.lower()
    harf_mi(metin)
    
def harf_mi(metin):
    for harf in metin:
        if harf.isalpha() or harf.isdecimal(): # karakter string ve sayı ise 
            frekanslar[harf] = frekanslar.get(harf,0) +1
    frekans_bul(metin) 
           
def frekans_bul(metin):
    toplam_harf_sayisi=len(metin)
    print("sembol: frekansı yüzdelik değeri")
    for harf, frekans in sorted(frekanslar.items()):
        yuzde_oran = (frekans / toplam_harf_sayisi) * 100
        print("{}:{:>9}          %{:.2f}".format(harf,frekans,yuzde_oran))
        
selamla()
metin = input("Bir metin girin: ")
kucuk_yap(metin) 
