# 📚 AHB2 UVM Testbench - Türkçe Öğrenme Rehberi (Index)

Hoşgeldiniz! Bu rehber, mevcut **AHB2 UVM Testbench** projesini tamamen anlamanız için tasarlanmıştır.

## 📖 Rehber Dosyaları

Lütfen aşağıdaki sırayla okuyunuz:

### 1️⃣ **[UVM_LEARNING_GUIDE_TR.md](./UVM_LEARNING_GUIDE_TR.md)** - BAŞLAYIN BURADAN! 📍
**İçerik:**
- ✅ Mimari Genel Bakış (üst seviye diagram)
- ✅ Tam Dosya Yapısı Açıklaması (dosya dosya)
- ✅ Bileşen Detayları (Transaction, Driver, Monitor, Agent, vb)
- ✅ Çalıştırma Akışı (Build → Connect → Run phases)
- ✅ Örnek Senaryolar (WRITE, READ, WRAP, BUSY, ERROR, RESET)

**Ne Zaman Oku:** Projeyi ilk kez öğrenirken, genel mimariye aşina olmak için

**Tahmini Süre:** 30-45 dakika

---

### 2️⃣ **[DETAILED_CODE_EXAMPLES_TR.md](./DETAILED_CODE_EXAMPLES_TR.md)** - Kod Seviyesinde Derinlik
**İçerik:**
- ✅ Transaction Sınıfı (random fields, constraints)
- ✅ Agent Bileşenleri (Driver, Monitor, Sequencer detaylı kod)
- ✅ Virtual Sequences (Master + Slave koordinasyon)
- ✅ Test Yazma (Base Test, Spesifik Test implementasyonu)
- ✅ Debugging ve Observation (Waveform analizi, UVM messages)

**Ne Zaman Oku:** UVM_LEARNING_GUIDE'ı okudan sonra, kod seviyesinde derinlik için

**Tahmini Süre:** 40-60 dakika

---

### 3️⃣ **[QUICK_REFERENCE_TR.md](./QUICK_REFERENCE_TR.md)** - Hızlı Arama Kartı
**İçerik:**
- ✅ Dosya Yapısı Tablosu (hangi dosya ne yapar)
- ✅ Sinyaller Reference (Master/Slave sinyalleri)
- ✅ Senaryo Hızlı Başlat (command line)
- ✅ Component Hiyerarşi Diagram
- ✅ Compilation Order (ÇOK ÖNEMLİ!)
- ✅ UVM Phases Timeline
- ✅ Debugging Tips
- ✅ Kısaltmalar ve Commands

**Ne Zaman Oku:** Simulasyon çalıştırırken, hızlı referans olarak

**Tahmini Süre:** 5-10 dakika (ihtiyaç olunca)

---

### 4️⃣ **[STEP_BY_STEP_GUIDE_TR.md](./STEP_BY_STEP_GUIDE_TR.md)** - Pratik Uygulamalı Rehber
**İçerik:**
- ✅ Adım 1: Projede İlk Yürüyüş (dosyaları sırasıyla oku)
- ✅ Adım 2: Simulasyon Özeti
- ✅ Adım 3: Bileşenleri Birer Birer Anlamak (interface, transaction, driver, monitor, vb)
- ✅ Adım 4: Transaction Flow Çalışması (detaylı timeline)
- ✅ Adım 5: Hands-On Çalışma (compilation ve run)
- ✅ Adım 6: Sorun Giderme (yaygın hatalar ve fixler)
- ✅ Adım 7: Kendi Test'ini Yazma (boilerplate code)

**Ne Zaman Oku:** Teorik bilgiden sonra pratik yapırken

**Tahmini Süre:** 60-90 dakika (interactive)

---

## 🎯 Önerilen Okuma Sırası

### Başlangıçlar için (Total: ~2 saat)

```
1. UVM_LEARNING_GUIDE_TR.md (Bölüm: Mimari Genel Bakış)
   ↓
2. QUICK_REFERENCE_TR.md (Bölüm: Sinyaller Reference)
   ↓
3. UVM_LEARNING_GUIDE_TR.md (Kalan Bölüm: Dosya Yapısı)
   ↓
4. STEP_BY_STEP_GUIDE_TR.md (Adım 1-3)
   ↓
5. QUICK_REFERENCE_TR.md (Compilation Order)
   ↓
6. STEP_BY_STEP_GUIDE_TR.md (Adım 5: Hands-On)
```

### Belirli Konuyu Öğrenmek İçin

**"Driver nasıl çalışıyor?" öğrenmek istiyorum:**
1. QUICK_REFERENCE_TR.md → Sinyaller Reference
2. UVM_LEARNING_GUIDE_TR.md → Driver bölümü
3. DETAILED_CODE_EXAMPLES_TR.md → Driver kod örnekleri
4. STEP_BY_STEP_GUIDE_TR.md → Adım 3.3 Driver

**"Virtual Sequence nasıl koordinasyon yapıyor?" öğrenmek istiyorum:**
1. UVM_LEARNING_GUIDE_TR.md → Virtual Sequencer bölümü
2. DETAILED_CODE_EXAMPLES_TR.md → Virtual Sequences bölümü
3. STEP_BY_STEP_GUIDE_TR.md → Adım 4 Flow çalışması

**"Transaction Constraints nasıl çalışıyor?" öğrenmek istiyorum:**
1. DETAILED_CODE_EXAMPLES_TR.md → Transaction bölümü
2. UVM_LEARNING_GUIDE_TR.md → Master Transaction bölümü
3. Run et ve waveform'da gözlemle

---

## 💡 Hızlı Tips

### Simülasyon Çalıştırmadan Önce OKU!

```bash
# ✅ Compilation order kontrol et
cat sim/compile.f

# ✅ include sırası kontrol et
cat ahb_test/ahb_test_pkg.sv

# ✅ Interface sinyallerini anla
cat rtl/ahb_intf.sv

# ✅ Temel enum'ları anla
cat ahb_test/tb_defs.svh
```

### İlk Simulasyon

```bash
cd /home/beratgokaytopcu/Documents/UVM\ Examples/projects/ahb2_uvm_tb/sim

# Compile
make clean
make compile

# Run
make run

# Waveform aç (GUI)
make wave
```

### Debugging Checklist

- [ ] HRESETn reset yapıyor mu? (Waveform'da kontrol et)
- [ ] HTRANS sequence doğru mu? (IDLE → NONSEQ → SEQ → ... → IDLE)
- [ ] HREADY expected yerlerde 0 ve 1 mi?
- [ ] Monitor transaction yakalayabiliyor mu? (UVM logs'ta kontrol)
- [ ] Virtual sequencer cast etme başarılı mı?
- [ ] Config database'den tüm config'ler alındı mı?

---

## 📊 Bileşen Harita

```
┌─ rtl/
│  └─ ahb_intf.sv ................... Hardware Interface
│
├─ ahb_master_agent/
│  ├─ ahb_mxtn.svh ................. Master Transaction
│  ├─ ahb_mdriver.svh .............. Master Driver (Aktif)
│  ├─ ahb_mmonitor.svh ............. Master Monitor (Pasif)
│  ├─ ahb_mseqr.svh ................ Master Sequencer
│  ├─ ahb_mseqs.svh ................ Master Sequences
│  ├─ ahb_magent_config.svh ........ Master Config
│  └─ ahb_magent.svh ............... Master Agent (Container)
│
├─ ahb_slave_agent/
│  ├─ ahb_sxtn.svh ................. Slave Transaction
│  ├─ ahb_sdriver.svh .............. Slave Driver (Aktif)
│  ├─ ahb_smonitor.svh ............. Slave Monitor (Pasif)
│  ├─ ahb_sseqr.svh ................ Slave Sequencer
│  ├─ ahb_sseqs.svh ................ Slave Sequences
│  ├─ ahb_sagent_config.svh ........ Slave Config
│  └─ ahb_sagent.svh ............... Slave Agent (Container)
│
├─ reset_agent/
│  ├─ reset_agent.svh .............. Reset Agent
│  ├─ reset_driver.svh ............. Reset Driver
│  ├─ reset_seqr.svh ............... Reset Sequencer
│  └─ reset_seqs.svh ............... Reset Sequences
│
├─ ahb_env/
│  ├─ env_config.svh ............... Environment Config
│  ├─ ahb_vseqr.svh ................ Virtual Sequencer
│  ├─ ahb_vseqs.svh ................ Virtual Sequences
│  ├─ ahb_coverage.svh ............. Coverage Collector
│  ├─ ahb_env.svh .................. Environment (Container)
│  └─ top.sv ....................... Top Module
│
├─ ahb_test/
│  ├─ tb_defs.svh .................. Type Definitions
│  ├─ ahb_test_pkg.sv .............. Test Package
│  ├─ ahb_base_test.svh ............ Base Test
│  ├─ ahb_incrx_test.svh ........... INCR Test
│  ├─ ahb_wrapx_test.svh ........... WRAP Test
│  ├─ ahb_err_test.svh ............. Error Test
│  ├─ ahb_reset_test.svh ........... Reset Test
│  └─ ahb_incrbusy_test.svh ........ Busy Test
│
└─ sim/
   ├─ Makefile ..................... Build automation
   ├─ compile.f .................... File list for compiler
   ├─ run.py ....................... Python run script
   ├─ ahb_wave.do .................. Waveform save config
   └─ [xsim files] ................. Generated files

DOCUMENTATION (YENİ):
├─ UVM_LEARNING_GUIDE_TR.md ........ Ana rehber
├─ DETAILED_CODE_EXAMPLES_TR.md .... Kod örnekleri
├─ QUICK_REFERENCE_TR.md ........... Hızlı referans
└─ STEP_BY_STEP_GUIDE_TR.md ........ Adım adım pratikal
```

---

## 📝 Sık Sorulan Sorular

### Q: Nereden başlamalıyım?
**A:** `UVM_LEARNING_GUIDE_TR.md` sayfasının "Mimari Genel Bakış" bölümünden başlayın.

### Q: Bir bileşeni hızlı anlamak istiyorum
**A:** `QUICK_REFERENCE_TR.md` → `DETAILED_CODE_EXAMPLES_TR.md` → İlgili dosyayı oku

### Q: Simülasyon nasıl çalışıyor?
**A:** `UVM_LEARNING_GUIDE_TR.md` → "Çalıştırma Akışı" bölümü

### Q: Kendi test'imi nasıl yazarım?
**A:** `STEP_BY_STEP_GUIDE_TR.md` → "Adım 7: Kendi Test'ini Yazma"

### Q: Hata alıyorum, ne yapmalı?
**A:** `STEP_BY_STEP_GUIDE_TR.md` → "Adım 6: Sorun Giderme"

### Q: Compilation order ne?
**A:** `QUICK_REFERENCE_TR.md` → "Compilation Order (Çooook Önemli!)"

---

## 🔧 Sistem Gereksinimleri

- **Simulator:** Vivado/Xilinx xsim (mevcut proje için)
- **Language:** SystemVerilog (UVM)
- **UVM Version:** 1.2 (genellikle simulator ile gelir)
- **OS:** Linux (proje yapısı Linux'e uygun)

---

## 🎓 Öğrenme Çıktıları

Bu rehberi okudum sonra şunları yapabileceksiniz:

✅ AHB2 protokolünü anlama
✅ UVM mimari yapısını anlama (Component, Sequencer, Driver, Monitor)
✅ Master-Slave iletişimini anlama
✅ Virtual sequences ile koordinasyon yapma
✅ Kendi test senaryolarını yazma
✅ Waveform'da gözlemler yapma
✅ Hata ayıklama ve sorun çözme

---

## 📞 İletişim / Sorular

Rehberde anlamadığınız yerler:
1. Dosya yeniden okuyun (daha dikkatli)
2. STEP_BY_STEP_GUIDE'ın ilgili adımını çalıştırın
3. Waveform'da gözlemleyin
4. Diğer rehberleri cross-reference yapın

---

## 📄 Rehber Yazarı

Bu rehber **AHB2 UVM Testbench** projesinin mevcut kodu analiz edilerek hazırlanmıştır.

---

## 🚀 Sonraki Adımlar

1. Bu rehberi tamamen oku
2. Simulasyon çalıştır ve waveform'da gözlemle
3. Bileşenleri değiştir ve ne değişiyor gözlemle
4. Kendi test'ini yaz ve çalıştır
5. Coverage report'unu analiz et

Başarılar! 🎯
