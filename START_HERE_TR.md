# ⚡ BAŞLAYIN BURADAN - 5 Dakikalık Hızlı Başlang

## Merhaba! 👋

Bu proje bir **AHB2 Protocol Testbench** UVM ile yazılmış. Öğrenmek istiyorsanız:

---

## 🎯 Hemen Başla

### 1️⃣ Önce Bu Dosyayı Oku (5 min)
```
📄 INDEX_TR.md
   ↓
   Tüm rehberlerin haritası ve kılavuzu
   Hangi rehberi ne zaman okuyacağınızı bulacaksınız
```

### 2️⃣ Sonra Bu Dosyayı Oku (45 min)
```
📄 UVM_LEARNING_GUIDE_TR.md
   ↓
   Tüm mimarinin genel bakışı
   Dosya yapısı açıklaması
   Bileşenlerin nasıl çalıştığı
```

### 3️⃣ Kod Örnekleri (60 min)
```
📄 DETAILED_CODE_EXAMPLES_TR.md
   ↓
   Gerçek kod örnekleri
   Her bileşenin nasıl çalıştığı (kod seviyesinde)
```

### 4️⃣ Pratik Yapma (60 min)
```
📄 STEP_BY_STEP_GUIDE_TR.md
   ↓
   Adım adım simülasyon çalıştırma
   Sorun giderme
   Kendi test yazma
```

### 5️⃣ Hızlı Referans Kartı (5-10 min ihtiyaç olunca)
```
📄 QUICK_REFERENCE_TR.md
   ↓
   Komutlar, filelist, hızlı tips
   Simulasyon çalıştırırken kullan
```

---

## 📍 Dosya Konumları

```
ahb2_uvm_tb/
├── 📄 INDEX_TR.md                    ← ŞU ANDA BURDASINIZ (Ana harita)
├── 📄 UVM_LEARNING_GUIDE_TR.md       ← 1. OKU (Genel mimari)
├── 📄 DETAILED_CODE_EXAMPLES_TR.md   ← 2. OKU (Kod seviyesi)
├── 📄 STEP_BY_STEP_GUIDE_TR.md       ← 3. OKU (Praktik)
├── 📄 QUICK_REFERENCE_TR.md          ← 4. OKU (Hızlı referans)
│
├── rtl/
│   └── ahb_intf.sv                   (Hardware Interface)
│
├── ahb_master_agent/                 (Master bileşenleri)
├── ahb_slave_agent/                  (Slave bileşenleri)
├── reset_agent/                      (Reset yönetimi)
├── ahb_env/                          (Environment ve test koordinasyon)
├── ahb_test/                         (Spesifik test sınıfları)
└── sim/                              (Simulasyon araçları)
```

---

## 🚀 Hemen Simulasyon Çalıştır!

```bash
# Terminal'de:
cd sim
make clean
make compile
make run

# Waveform'u görmek için:
make wave
```

---

## 💡 Ne Öğreneceksiniz?

- ✅ **AHB2 Protocol** - Bus protokolü, sinyaller
- ✅ **UVM Architecture** - Component modeli, sequencer, driver, monitor
- ✅ **Master-Slave Communication** - İki tarafın nasıl haberleştiği
- ✅ **Virtual Sequencing** - Testleri koordine etme
- ✅ **Coverage & Functional Verification** - Test kapsamını ölçme

---

## 📚 Rehber İçeriği Özet

| Rehber | Süre | İçerik |
|--------|------|--------|
| INDEX_TR | 5 min | 📍 Harita ve kılavuz |
| UVM_LEARNING_GUIDE_TR | 45 min | 🏗️ Tam mimari ve dosya yapısı |
| DETAILED_CODE_EXAMPLES_TR | 60 min | 💻 Kod seviyesinde örnekler |
| STEP_BY_STEP_GUIDE_TR | 90 min | 👣 Adım adım pratik kılavuz |
| QUICK_REFERENCE_TR | 10 min | ⚡ Hızlı arama kartı |

---

## ❓ Sık Sorulan Sorular

**S: Hangisinden başlamalıyım?**
A: `UVM_LEARNING_GUIDE_TR.md` → "Mimari Genel Bakış" bölümünden

**S: Simulasyon nasıl çalışıyor?**
A: `STEP_BY_STEP_GUIDE_TR.md` → "Adım 2: Simulasyon Özeti"

**S: Test nasıl yazarım?**
A: `STEP_BY_STEP_GUIDE_TR.md` → "Adım 7: Kendi Test'ini Yazma"

**S: Hata alıyorum!**
A: `STEP_BY_STEP_GUIDE_TR.md` → "Adım 6: Sorun Giderme"

---

## 🎯 Önerilen Akış

```
1. Bu dosyayı oku (5 min)
   ↓
2. INDEX_TR.md'nin önerilen sırasını takip et
   ↓
3. Her rehberi oku ve örnekleri çalıştır
   ↓
4. Simulasyon yapıp waveform'da gözlemle
   ↓
5. Kendi test'ini yaz
   ↓
6. QUICK_REFERENCE_TR'ı bookmark'la
```

---

## 🔥 İlk 5 Adım (Bugün!)

### Adım 1: Dosyaları Gözat (5 min)
```bash
# Project root'ta
find . -name "*.md" | head -5
# 📄 INDEX_TR.md
# 📄 UVM_LEARNING_GUIDE_TR.md
# vb...
```

### Adım 2: Proje Yapısını Anla (10 min)
```bash
# Her dizini aç ve neyin ne olduğunu oku
ls -la ahb_master_agent/
ls -la ahb_slave_agent/
ls -la ahb_env/
```

### Adım 3: Interface'i İnceле (5 min)
```bash
# Bu tüm haberleşmenin omurgası
cat rtl/ahb_intf.sv | head -50
```

### Adım 4: Type Definitions (3 min)
```bash
# Tüm enum'lar burada
cat ahb_test/tb_defs.svh | head -40
```

### Adım 5: UVM_LEARNING_GUIDE İlk Bölümü (15 min)
```bash
# Tüm mimarinin genel görünümü
# UVM_LEARNING_GUIDE_TR.md → "Mimari Genel Bakış"
```

**Toplam: 38 dakika** 

---

## 📊 Proje Mimarisi (1 dakikalık özet)

```
Top Module
    │
    ├─→ HCLK (Saat sinyali)
    ├─→ ahb_intf (Hardware interface)
    └─→ run_test()
            │
            ├─→ Test build_phase
            │       └─→ Environment create
            │           └─→ Agents create
            │
            ├─→ Test connect_phase
            │       └─→ Components bağla
            │
            └─→ Test run_phase
                    └─→ Virtual Sequences
                            ├─→ Master: Transaction gönder
                            ├─→ Slave: Response ver
                            └─→ Monitor: Gözlemle ve kaydet
```

---

## 🎓 Başında Bilinmesi Gerekenler

| Konsept | Açıklama |
|---------|----------|
| **Agent** | Driver + Monitor + Sequencer container'ı |
| **Driver** | Transaction'ları hardware signal'lerine dönüştürür |
| **Monitor** | Hardware signal'lerini gözlemler, transaction'ı reconstruct eder |
| **Sequencer** | Transaction'ları oluşturur ve Driver'a gönderir |
| **Virtual Sequencer** | Birden fazla sequencer'ı koordine eder |
| **Virtual Sequence** | Master + Slave'i koordine eden test senaryosu |
| **Clocking Block** | Hardware sinyallere timing reference sağlar |

---

## ✅ Kontrolü Listesi

Başlamadan önce:
- [ ] Dosyalara erişim var mı? (`ls -la` ile kontrol et)
- [ ] Simulator yüklü mü? (`which xsim` ile kontrol et)
- [ ] Makefile mevcut mu? (`cat sim/Makefile` ile kontrol et)
- [ ] UVM include yolları doğru mu? (`cat sim/compile.f` ile kontrol et)

---

## 🚀 Sonrası Ne?

Rehberleri okuduktan sonra:

1. **Simulasyon çalıştırınız**
   ```bash
   cd sim && make run
   ```

2. **Waveform'u açınız**
   ```bash
   make wave
   ```

3. **Sinyalleri gözlemleyiniz**
   - HCLK: Toggling
   - HRESETn: 0 → 1
   - HTRANS: IDLE → NONSEQ → SEQ → IDLE
   - HADDR: Burst modu'na göre değişir

4. **Logs'ları okuyunuz**
   - "Transaction From Master" mesajlarını ara
   - "Data Received from Master Monitor" mesajlarını ara

5. **Kendi test'inizi yazınız**
   - Yeni sequence oluştur
   - Test sınıfında başlat
   - Simulasyon çalıştır ve sonuç gözlemle

---

## 📞 Rehber Sayfaları

1. **INDEX_TR.md** - 📍 Şu anda burdasınız!
2. **UVM_LEARNING_GUIDE_TR.md** - 🏗️ Ana rehber
3. **DETAILED_CODE_EXAMPLES_TR.md** - 💻 Kod örnekleri
4. **STEP_BY_STEP_GUIDE_TR.md** - 👣 Adım adım
5. **QUICK_REFERENCE_TR.md** - ⚡ Hızlı referans

---

## 🎉 Başlamaya Hazır mısınız?

**ŞİMDİ: INDEX_TR.md'yi oku** (eğer 5 dakikanız varsa)
**SONRA: UVM_LEARNING_GUIDE_TR.md'ye git** (ana rehber)

Başarılar! 🚀

---

*Son güncelleme: Ekim 2025*
*Dil: Türkçe*
*Proje: AHB2 UVM Testbench*
