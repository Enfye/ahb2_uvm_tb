# AHB2 UVM Testbench - Step-by-Step Çalışma Kılavuzu

Bu kılavuz, mevcut projeyi adım adım çalıştırırken ne olduğunu anlayabilmeniz için tasarlanmıştır.

## Adım 1: Projede İlk Yürüyüş

### 1.1 Dosya Yapısını Anlama

```bash
# Proje kökünde
cd /home/beratgokaytopcu/Documents/UVM\ Examples/projects/ahb2_uvm_tb

# Dizinleri listele
ls -la

# Her dizin neyin sorumlusu?
- rtl/              → Hardware interface tanımları
- ahb_master_agent/ → Master agent bileşenleri
- ahb_slave_agent/  → Slave agent bileşenleri
- reset_agent/      → Reset yönetimi
- ahb_env/          → Environment, test, toplam koordinasyon
- ahb_test/         → Spesifik test sınıfları
- sim/              → Simulasyon dosyaları ve scripts
```

### 1.2 Kilit Dosyaları Oku (Sırasıyla)

```
1. sim/compile.f
   ↓ Bu dosya hangi .sv/.svh dosyalarının include edileceğini tanımlar
   ↓ Include sırası ÇOK ÖNEMLİ!
   ↓ Oku ve anlama: hangi dosya hangi dosyaya dependency'si var?

2. rtl/ahb_intf.sv
   ↓ Bu interface tüm haberleşmenin omurgası
   ↓ Clocking block'ları inceле: mdrv_cb, mmon_cb, sdrv_cb, smon_cb

3. ahb_test/tb_defs.svh
   ↓ Tüm enum tanımları burada
   ↓ transfer_t: IDLE, BUSY, NONSEQ, SEQ
   ↓ burst_t: SINGLE, INCR, WRAP4, ...
   ↓ rw_t: READ, WRITE
   ↓ resp_t: OKAY, ERROR, ...

4. ahb_master_agent/ahb_mxtn.svh
   ↓ Transaction tanımı - Master master ne gönderiyor?
   ↓ address[], write_data[], burst_mode, ... constraints

5. ahb_master_agent/ahb_mdriver.svh
   ↓ Transaction'ları interface'e nasıl koyuyor?
   ↓ drive() task'ında timeline var

6. ahb_master_agent/ahb_mmonitor.svh
   ↓ Interface'i gözleme - Transaction'ı nasıl reconstruct ediyor?
   ↓ monitor_ap.write() ile gözlemler yayınlanıyor

7. ahb_master_agent/ahb_magent.svh
   ↓ Master agent bileşenleri kontrol panel
   ↓ mdriver_h, mmonitor_h, mseqr_h'ı connect ediyor

8. ahb_slave_agent/ (master ile aynı yapı)

9. reset_agent/ (basit, sadece reset)

10. ahb_env/ahb_env.svh
    ↓ Tüm agent'ları bir araya getiriyor
    ↓ Virtual sequencer'ı create ediyor

11. ahb_env/ahb_vseqs.svh
    ↓ Master + Slave'i koordine eden sequence'lar
    ↓ RESET, INCR, WRAP, ERROR senaryoları

12. ahb_env/top.sv
    ↓ Module top
    ↓ HCLK generate ediyor
    ↓ Interface'i connect ediyor
    ↓ run_test() çağırıyor

13. ahb_test/ahb_base_test.svh
    ↓ Base test sınıfı
    ↓ build_phase(): config setup
    ↓ env create

14. ahb_test/ahb_incrx_test.svh
    ↓ INCR test - concrete implementation
    ↓ Virtual sequences başlatıyor
    ↓ Simülasyonu kontrol ediyor
```

---

## Adım 2: Simulasyon Özeti

### 2.1 Simulasyon Ne Yapıyor?

```
┌─────────────────────────────────────────────────────────┐
│ Simulasyon Başlaması                                    │
└─────────────────────────────────────────────────────────┘

T0: top module yükleniyor
    ├─ HCLK = 0, forever #10 HCLK = ~HCLK
    ├─ ahb_intf instantiate
    └─ run_test() çağrılıyor

T1: Test create ve build
    ├─ ahb_base_test build_phase
    │  ├─ env_cfg = env_config::create()
    │  ├─ VIF = config_db'den al
    │  ├─ env_cfg.vif = vif
    │  └─ env = ahb_env::create()
    │     └─ ahb_env build_phase
    │        ├─ magt_cfg set
    │        ├─ sagt_cfg set
    │        └─ agent'lar create
    │           └─ mdriver, mmonitor, mseqr create

T2: Connect
    ├─ env connect_phase
    │  ├─ mdriver ↔ mseqr
    │  ├─ mmonitor.ap ↔ coverage
    │  └─ vseqr.mseqr_h = master_seqr

T3: Run
    ├─ ahb_incrx_test run_phase başlıyor
    │  ├─ reset_vseq.start(vseqr)
    │  │  └─ HRESETn toggling
    │  │
    │  ├─ repeat(10) incrx_vseq.start(vseqr)
    │  │  ├─ mseq.start(mseqr)
    │  │  │  └─ mdriver.drive() transactions
    │  │  │
    │  │  └─ sseq.start(sseqr)
    │  │     └─ slave responses
    │  │
    │  ├─ Monitor (paralel) gözlemler
    │  │  └─ transactions capture ve yayınla
    │  │
    │  └─ Coverage update
    │
    └─ Simülasyon bitiş
```

### 2.2 INCR Test Timeline (Gerçek Sayılar)

```
HCLK Period = 20ns (frekans = 50MHz)

Reset Phase:
  0-100ns:   HRESETn = 0
  100ns:     HRESETn = 1 (release)

INCR Transaction (2-beat):
  110ns(T0): HTRANS=NONSEQ, HADDR=0x1000, HWRITE=WRITE
  130ns(T1): HTRANS=SEQ,    HADDR=0x1004, HREADY=1
  150ns(T2): HTRANS=IDLE,   (transaction complete)

Repeat 10 times...

Toplam simülasyon süresi: ~2000ns
```

---

## Adım 3: Bileşenleri Birer Birer Anlamak

### 3.1 Interface (ahb_intf.sv)

```systemverilog
// Oku ve anlama
1. Hangi sinyaller master → slave?
   - HADDR, HWDATA, HWRITE, HTRANS, HBURST, HSIZE
   
2. Hangi sinyaller slave → master?
   - HRDATA, HREADY, HRESP
   
3. mdrv_cb (Master Driver Clocking Block)
   - output: Master ne control ediyor?
   - input: Master ne gözlemliyor?
   
4. mmon_cb (Master Monitor Clocking Block)
   - Aynı sinyalleri ama gözleme amaçlı
   
5. sdrv_cb (Slave Driver Clocking Block)
   - HREADY'i inout (hem giriş hem çıkış kontrolü)
   - HRDATA ve HRESP çıkış (slave control ediyor)
   
6. smon_cb (Slave Monitor Clocking Block)
   - Tüm sinyalleri gözlemliyor
```

### 3.2 Transaction (ahb_mxtn.svh)

```systemverilog
// Oku ve anlama
1. Random fields
   rand transfer_t trans_type[];  // Master ne gönderme sırası yapıyor?
   rand burst_t burst_mode;       // Burst tipi
   rand bit [31:0] address[];     // Kaç beat? Her beat'te adres?
   
2. Constraints (Çok önemli!)
   // Neden constraints var? → Geçerli transaction'lar
   - address.size burst_mode'a göre belirlenir
   - address alignment word boundary'sinde
   - Adresler 1KB sınırının içinde
   
3. Response fields
   resp_t response;    // Slave ne cevap veriyor?
   bit [31:0] read_data;  // Okuma verisini kim koyuyor?

// Constraint örneği okunması:
constraint addr {
    if(burst_mode == 0)              // SINGLE mode
        address.size == 1;           // 1 beat sadece
    if(burst_mode == 1)              // INCR mode
        address.size < (1024/(2^trans_size));  // değişken beat
    if(burst_mode == 2 || burst_mode == 3)  // WRAP4, WRAP4A
        address.size == 4;           // tam 4 beat
}

// Anlamı:
// - Burst modu transfer size'a göre max address sayısını belirliyor
// - Wrap mode'lar sabit beat sayısı (4, 8, 16)
// - INCR mode'da variable beat sayısı (1-16)
```

### 3.3 Driver (ahb_mdriver.svh)

```systemverilog
// Oku ve anla yapısı

task run_phase();
    // Fork 1: Reset Detection
    forever begin
        wait(!vif.HRESETn);         // Reset başlangıcında
        disable driver;              // Aktif transaction'ı iptal et
        vif.HTRANS <= 0;             // Tüm sinyalleri 0 yap
        wait(vif.HRESETn);           // Reset bitişini bekle
    end
    
    // Fork 2: Error Response Detection
    forever begin
        @(vif.mdrv_cb);
        if ((vif.HRESP != 2'b00) && (vif.HREADY == 0)) begin
            disable driver;          // Hata varsa transaction iptal
            vif.mdrv_cb.HTRANS <= 0; // IDLE gönder
        end
    end
    
    // Fork 3: Normal Drive
    forever begin
        seq_item_port.get_next_item(req);  // Sequencer'dan transaction al
        drive();                            // Transaction'ı drive et
        seq_item_port.item_done(req);       // Bittiğini söyle
    end
endtask

// Anlamı:
// 1. 3 fork paralel koşuyor:
//    - Reset hakkında
//    - Error response hakkında  
//    - Normal transaction drive
// 2. Transaction'lar drive() task'ında sinyallere dönüştürülüyor
// 3. Clock edge'de (@vif.mdrv_cb) sinyaller update ediliyor
```

### 3.4 Monitor (ahb_mmonitor.svh)

```systemverilog
// Oku ve anlama

task run_phase();
    forever begin
        // 1. Yeni transaction container oluştur
        xtn = ahb_mxtn::type_id::create("xtn");
        
        // 2. Transfer tipi gözle
        xtn.trans_type[0] = vif.mmon_cb.HTRANS;
        
        // 3. IDLE transaction varsa yaz ve devam
        if (xtn.trans_type[0] == IDLE) begin
            monitor_ap.write(xtn);
            @(vif.mmon_cb);
            continue;
        end
        
        // 4. Normal transfer: tüm kontrol sinyallerini al
        xtn.burst_mode = vif.mmon_cb.HBURST;
        xtn.trans_size = vif.mmon_cb.HSIZE;
        xtn.read_write = vif.mmon_cb.HWRITE;
        xtn.address[0] = vif.mmon_cb.HADDR;
        
        @(vif.mmon_cb);
        
        // 5. Response sinyallerini al
        xtn.response = vif.mmon_cb.HRESP;
        
        // 6. Read/Write verisini al
        if (xtn.read_write == READ)
            xtn.read_data = vif.mmon_cb.HRDATA;
        else
            xtn.write_data[0] = vif.mmon_cb.HWDATA;
        
        // 7. Gözlemlenen transaction'ı yayınla
        monitor_ap.write(xtn);
    end
endtask

// Anlamı:
// 1. Interface'deki gerçek sinyalleri gözlemliyor
// 2. Bunları transaction'a dönüştürüyor
// 3. analysis_port.write() ile yayınlıyor
// 4. Coverage, Scoreboard, vb. bu port'u subscribe ediyor
```

### 3.5 Sequencer (ahb_mseqr.svh)

```systemverilog
// Basit - standart UVM sequencer
class ahb_mseqr extends uvm_sequencer#(ahb_mxtn);
    `uvm_component_utils(ahb_mseqr)
    
    // Hiç şey yapmasına gerek yok
    // UVM framework'ü otomatik olarak:
    // 1. seq_item_export'u expose ediyor
    // 2. Sequence'dan item'ı alıyor
    // 3. Driver'a gönderiyor
endclass

// Anlamı:
// Sequencer = Kanalman
// - Test: "5 write transactions gönder" diyor
// - Sequencer: Transaction'ları receive ediyor
// - Driver: Sequencer'dan transaction alıyor
```

### 3.6 Agent (ahb_magent.svh)

```systemverilog
// Agent = Kontrol Paneli

build_phase:
    // 1. Hangi mode? Active yoksa Passive?
    // 2. Active: Driver + Sequencer gerekli
    // 3. Passive: Sadece Monitor (gözlem)

connect_phase:
    // 1. mdriver ↔ mseqr bağla
    // 2. mmonitor.ap ↔ agent_ap bağla

// Anlamı:
// Agent bir bireyin tüm bileşenlerini yönetiyor
// - Denetim: driver, sequencer (active) veya sadece monitor (passive)
// - Gözlem: monitor her zaman çalışır
// - Haberleşme: analysis port ile haricilere bilgi verir
```

### 3.7 Virtual Sequencer (ahb_vseqr.svh)

```systemverilog
class ahb_vseqr extends uvm_sequencer#(uvm_sequence_item);
    `uvm_component_utils(ahb_vseqr)
    
    // Referanslar (handle'lar) - Component oluşturmaz!
    reset_seqr reset_seqr_h;
    ahb_mseqr mseqr_h;
    ahb_sseqr sseqr_h;
endclass

// Anlamı:
// Virtual Sequencer = Orkestra Şefi
// - Birden fazla sequencer'ı yönetir
// - Bunlar arasında koordinasyon sağlar
// - Virtual sequences bunu kullanır
```

### 3.8 Virtual Sequences (ahb_vseqs.svh)

```systemverilog
// Virtual Sequence = Master + Slave'i koordine eden senaryo

class ahb_incrx_vseq extends ahb_base_vseq;
    task body();
        // 1. Virtual sequencer'dan master ve slave sequencer'ları al
        super.body();  // Bu vseqr_h, mseqr_h, sseqr_h set ediyor
        
        // 2. Master sequence create et
        ahb_incrx_mseq mseq = ahb_incrx_mseq::type_id::create();
        
        // 3. Slave sequence create et
        ahb_ready_sseq sseq = ahb_ready_sseq::type_id::create();
        
        // 4. Paralel olarak başlat
        fork
            mseq.start(mseqr_h);  // Master: Transaction gönder
            sseq.start(sseqr_h);  // Slave: Response ver
        join
    endtask
endclass

// Anlamı:
// 1. Virtual sequence test senaryosunu tanımlar
// 2. Master ne yapacak? (INCR transfer, 2-4 beat)
// 3. Slave ne yapacak? (Ready sinyali, data response)
// 4. Her ikisi paralel çalışır - senkron haberleşme olur
```

### 3.9 Environment (ahb_env.svh)

```systemverilog
build_phase:
    ├─ Config database'den config al
    ├─ Config'i agent'lara set et
    ├─ Tüm agent'ları create et
    ├─ Virtual sequencer create et
    └─ Coverage collector create et

connect_phase:
    ├─ Agents'ı connect et
    ├─ analysis_port'ları bağla
    └─ virtual_seqr.mseqr_h = agent.mseqr_h

// Anlamı:
// Environment = Test Setup'ı
// - Tüm DUT bileşenlerini organize eder
// - Bileşenler arasında haberleşmeyi sağlar
// - Coverage collection'ı organize eder
```

### 3.10 Test (ahb_incrx_test.svh)

```systemverilog
build_phase:
    ├─ env_config create et
    ├─ VIF al (top'tan config_db üzerinden)
    ├─ env_config'i set et
    └─ ahb_env create et

run_phase:
    ├─ phase.raise_objection(this)   // Simülasyon durmayacak
    │
    ├─ reset_vseq.start(env.vseqr)   // Reset yap
    │
    ├─ repeat(10)
    │  incrx_vseq.start(env.vseqr)    // 10 kez INCR transaction
    │
    ├─ idle_vseq.start(env.vseqr)     // Son olarak IDLE
    │
    ├─ #100                            // 100ns daha bekle
    │
    └─ phase.drop_objection(this)     // Simülasyon bitebilir

// Anlamı:
// Test = Senaryo yöneticisi
// - Test senaryosunun ne yapacağını tanımlar
// - Virtual sequences'ı başlatır
// - Simülasyon süresini kontrol eder
```

---

## Adım 4: Transaction Flow Çalışması

### 4.1 INCR Transaction (Detaylı Step-by-Step)

```
TEST SIDE:
─────────
T0: incrx_vseq.start(vseqr_h)
    │
    └─ fork incrx_mseq.start(mseqr_h)
           └─ req = ahb_mxtn::create()
              start_item(req)
              req.randomize() with { burst_mode == INCR, ... }
              finish_item(req)


SEQUENCER SIDE:
───────────────
T1: seq_item_port has req
    │
    └─ mseqr_h broadcasts req


DRIVER SIDE:
────────────
T2: seq_item_port.get_next_item(req)
    │
    └─ drive() 
       ├─ vif.mdrv_cb.HADDR <= req.address[0]
       ├─ vif.mdrv_cb.HTRANS <= req.trans_type[0]  (NONSEQ)
       ├─ vif.mdrv_cb.HBURST <= req.burst_mode      (INCR)
       ├─ vif.mdrv_cb.HSIZE <= req.trans_size
       ├─ vif.mdrv_cb.HWRITE <= req.read_write
       └─ @(vif.mdrv_cb)  ← Clock pulse!


INTERFACE SIDE:
───────────────
T3: posedge HCLK triggers mdrv_cb
    │
    HADDR = address[0]
    HTRANS = NONSEQ
    HBURST = INCR
    HSIZE = WORD
    HWRITE = READ/WRITE


SLAVE SIDE:
───────────
T4: fork ahb_ready_sseq.start(sseqr_h)
           └─ req = ahb_sxtn::create()
              start_item(req)
              req.randomize() with { ready_delay == 0 ... }
              finish_item(req)
                   │
                   └─ sdriver sets HREADY=1


INTERFACE SIDE:
───────────────
T5: HREADY = 1 (Slave ready)
    HRESP = OKAY
    HRDATA = (read data if read)


MONITOR SIDE (paralel çalışır):
────────────────────────────────
T6: forever loop
    ├─ @(vif.mmon_cb)
    ├─ xtn.trans_type = vif.HTRANS
    ├─ IF NOT IDLE:
    │  ├─ xtn.burst_mode = vif.HBURST
    │  ├─ xtn.address[0] = vif.HADDR
    │  ├─ ... tüm sinyalleri capture
    │  └─ monitor_ap.write(xtn)  ← Gözlem yayıncılığı
    │
    └─ Gözlemler Coverage'a ulaşır


DRIVER TARAF (devam):
─────────────────────
T7: wait HREADY
    loop for each address:
    ├─ @(vif.mdrv_cb)
    ├─ vif.mdrv_cb.HADDR <= next_address
    ├─ vif.mdrv_cb.HTRANS <= SEQ
    └─ @(vif.mdrv_cb)
    
    Final beat:
    ├─ vif.mdrv_cb.HTRANS <= IDLE
    └─ @(vif.mdrv_cb)


DRIVER TARAF (bitirme):
───────────────────────
T8: seq_item_port.item_done(req)


SEQUENCER TARAF:
────────────────
T9: Test loop return, next iteration


TEST TARAF:
───────────
T10: repeat(10) devam eder
     10 kez INCR transaction
```

---

## Adım 5: Hands-On Çalışma

### 5.1 İlk Kompilasyon ve Çalıştırma

```bash
# 1. Simulasyon dizinine git
cd /home/beratgokaytopcu/Documents/UVM\ Examples/projects/ahb2_uvm_tb/sim

# 2. Clean
make clean

# 3. Compile (tüm .sv/.svh dosyaları)
make compile
# Hata varsa ekrana çıkar - oku ve düzelt!

# 4. Run default test
make
# veya
make run

# 5. Waveform aç (GUI'de)
make wave
```

### 5.2 Test Output'unu Okuma

```
Simulasyon logs'ta şunları ara:

✓ "AHB Reset" - Reset başlamış
✓ "Transaction From Master" - Master transaction
✓ "Data Received from Master Monitor" - Monitor transaction capture
✓ "IDLE Transaction" - IDLE state
✓ Coverage report - Test kapsamı

Hata cases:
✗ "FATAL" - Kritik hata
✗ "ERROR" - Test failed
✗ "Cannot find" - Config database problemi
```

### 5.3 Waveform'da Neleri Aramalısın?

```
1. HCLK - Her zaman toggling olmalı (20ns period)

2. HRESETn - Başta 0, sonra 1 olmalı

3. HTRANS - Sequence:
   00 (IDLE) → 10 (NONSEQ) → 11 (SEQ) → ... → 00 (IDLE)

4. HADDR - İlk beat'te set edilir, sonra burst modu'na göre değişir:
   - INCR: +4 her beat'te
   - WRAP: Wrap boundary'de reset

5. HREADY - Master transactino sırasında:
   - 1: Slave ready
   - 0: Slave busy (wait cycle)

6. HRESP - Transfer sonunda:
   - 00: OK
   - 01: ERROR
   - 11: SPLIT
   - 10: RETRY

7. HWDATA (write) / HRDATA (read)
   - Verinin aktarıldığı siklus
```

### 5.4 Spesifik Test Çalıştırma

```bash
# Base test (simple)
make -f Makefile testname=ahb_base_test

# INCR test
make -f Makefile testname=ahb_incrx_test

# WRAP test
make -f Makefile testname=ahb_wrapx_test

# Error test
make -f Makefile testname=ahb_err_test

# Reset test
make -f Makefile testname=ahb_reset_test

# Busy test
make -f Makefile testname=ahb_incrbusy_test
```

---

## Adım 6: Sorun Giderme

### 6.1 Yaygın Hatalar

```
HATA 1: "Cannot get VIF from configuration database"
FIX:   top.sv'deki set() ve test'teki get() aynı path kullanmalı
       Genellikle "ahb_intf" ismiyle set/get

HATA 2: "Virtual Sequencer cast failed"
FIX:   Virtual sequence'da $cast(vseqr_h, m_sequencer)
       m_sequencer'ın ahb_vseqr tipinde olduğundan emin ol

HATA 3: "Cannot find AGENT-CONFIG"
FIX:   ahb_env::build_phase'da master_agent config set edilmeli
       uvm_config_db#(ahb_magent_config)::set()

HATA 4: "Randomization failed"
FIX:   Transaction constraints oku ve debug et
       req.randomize() hata verse constraint problemi var

HATA 5: No transfer görülmüyor
FIX:   Reset sinyali kontrol et (HRESETn = 1 olmalı)
       Virtual sequence'ın body() her zaman çağrılmalı
```

### 6.2 Debug Modunda Çalıştırma

```bash
# Full verbosity ile
xsim top -gui +UVM_VERBOSITY=UVM_FULL

# Logları dosyaya yaz
xsim top -R +UVM_VERBOSITY=UVM_MEDIUM > sim.log 2>&1

# Spesifik component loglarını etkinleştir
+uvm_set_type_override=ahb_incrx_mseq,ahb_incrx_mseq,1

# Break point ekle (GUI'de)
# breakpoint <file:line>
# continue
# print <signal>
```

---

## Adım 7: Kendi Test'ini Yazma

### 7.1 Simple WRITE Test (Boilerplate)

Yeni dosya: `ahb_test/ahb_simple_write_test.svh`

```systemverilog
class ahb_simple_write_test extends ahb_base_test;
    `uvm_component_utils(ahb_simple_write_test)
    
    ahb_reset_vseq reset_vseq;
    ahb_simple_write_vseq write_vseq;
    ahb_idle_vseq idle_vseq;
    
    function new(string name = "ahb_simple_write_test", uvm_component parent);
        super.new(name, parent);
    endfunction
    
    task run_phase(uvm_phase phase);
        phase.raise_objection(this);
        
        // 1. Reset
        reset_vseq = ahb_reset_vseq::type_id::create("reset_vseq");
        reset_vseq.start(env_h.vseqr_h);
        
        // 2. Simple write
        write_vseq = ahb_simple_write_vseq::type_id::create("write_vseq");
        write_vseq.start(env_h.vseqr_h);
        
        // 3. Done
        idle_vseq = ahb_idle_vseq::type_id::create("idle_vseq");
        idle_vseq.start(env_h.vseqr_h);
        
        #100;
        phase.drop_objection(this);
    endtask
endclass
```

### 7.2 Sequence'ı Yazma

Yeni dosya: `ahb_env/ahb_simple_write_vseq.svh`

```systemverilog
class ahb_simple_write_vseq extends ahb_base_vseq;
    `uvm_object_utils(ahb_simple_write_vseq)
    
    task body();
        super.body();
        
        // Master sequence
        ahb_simple_write_mseq write_mseq;
        write_mseq = ahb_simple_write_mseq::type_id::create();
        
        // Slave sequence
        ahb_simple_write_sseq write_sseq;
        write_sseq = ahb_simple_write_sseq::type_id::create();
        
        // Paralel olarak çalıştır
        fork
            write_mseq.start(mseqr_h);
            write_sseq.start(sseqr_h);
        join
    endtask
endclass
```

---

## Özet: Akış Taslağı

```
Test yazarken düşün:
1. Ne test etmek istiyorum?
   - INCR burst? WRAP burst? Error response?

2. Master ne göndermeli?
   - Create: ahb_xxx_mseq extends ahb_mbase_seq
   - body() task'ında: req.randomize() with {...}

3. Slave ne yapmalı?
   - Create: ahb_xxx_sseq extends ahb_sbase_seq
   - body() task'ında: Response generate et

4. Birleştir (Virtual Sequence)
   - Create: ahb_xxx_vseq extends ahb_base_vseq
   - fork/join ile master + slave

5. Test sınıfında
   - Create: ahb_xxx_test extends ahb_base_test
   - run_phase'da: vseq.start(env.vseqr)

6. Compile ve run
   - compile.f'ye ekle
   - ahb_test_pkg.sv'ye include ekle
   - Çalıştır ve waveform'da gözlemle
```

İyi şanslar! 🚀
