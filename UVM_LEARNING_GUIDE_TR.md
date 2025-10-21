# AHB2 UVM Testbench - Tamamen Öğrenme Kılavuzu

## İçerik Tablosu
1. [Mimari Genel Bakış](#mimari-genel-bakış)
2. [Dosya Yapısı](#dosya-yapısı)
3. [Bileşen Detayları](#bileşen-detayları)
4. [Çalıştırma Akışı](#çalıştırma-akışı)
5. [Örnek Senaryolar](#örnek-senaryolar)

---

## Mimari Genel Bakış

Bu testbench **AHB (Advanced High-performance Bus)** protokolünü test etmek için Master-Slave mimarisi kullanır.

### Üst Seviye Mimari

```
┌─────────────────────────────────────────────────────────┐
│                    TOP MODULE                            │
│  • Saat Sinyali Üretir (HCLK)                          │
│  • Interface'i Instantiate Eder                          │
│  • UVM Test'i Çalıştırır                               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    AHB INTERFACE                         │
│  • Master Clocking Block (mdrv_cb, mmon_cb)            │
│  • Slave Clocking Block (sdrv_cb, smon_cb)             │
│  • Protokol Sinyalleri                                 │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    TEST HIERARCHY                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  BASE_TEST                                       │  │
│  │  └─ ENV (Environment)                           │  │
│  │     ├─ RESET_AGENT                              │  │
│  │     ├─ MASTER_AGENT (AHB Master UVC)            │  │
│  │     │  ├─ Driver                                │  │
│  │     │  ├─ Monitor                               │  │
│  │     │  └─ Sequencer                             │  │
│  │     ├─ SLAVE_AGENT (AHB Slave UVC)             │  │
│  │     │  ├─ Driver                                │  │
│  │     │  ├─ Monitor                               │  │
│  │     │  └─ Sequencer                             │  │
│  │     ├─ VIRTUAL_SEQUENCER                        │  │
│  │     └─ COVERAGE                                 │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  └─ VIRTUAL_SEQUENCES (Koordine testler)              │
│     ├─ Reset Sequence                                 │
│     ├─ Increment Burst Sequence                       │
│     ├─ Wrap Sequence                                  │
│     └─ Error Response Sequence                        │
└─────────────────────────────────────────────────────────┘
```

---

## Dosya Yapısı

### 1. **rtl/** - Hardware Interface

```
rtl/ahb_intf.sv
├─ AHB Protokol Sinyalleri
├─ Master Clocking Block (mdrv_cb, mmon_cb)
├─ Slave Clocking Block (sdrv_cb, smon_cb)
└─ Reset Sinyali (HRESETn)
```

**Temel Sinyaller:**
- `HCLK`: Saat
- `HRESETn`: Reset (aktif düşük)
- `HADDR[31:0]`: Adres
- `HWRITE`: Okuma/Yazma kontrol
- `HTRANS[1:0]`: Transfer tipi (IDLE=00, BUSY=01, NONSEQ=10, SEQ=11)
- `HBURST[2:0]`: Burst modu (Single=0, INCR=1, WRAP=2-7)
- `HSIZE[2:0]`: Transfer boyutu
- `HWDATA[31:0]`: Master yazma verisi
- `HRDATA[31:0]`: Slave okuma verisi
- `HREADY`: Slave hazır sinyali
- `HRESP[1:0]`: Slave cevap (OK=00, ERROR=01)

---

### 2. **ahb_master_agent/** - Master UVC (Universal Verification Component)

#### **ahb_mxtn.svh** - Master Transaction Sınıfı
```
İçerik:
├─ rand bit reset           → Reset işlemi
├─ rand transfer_t trans_type[]    → Transfer tipleri dizisi
├─ rand bit [31:0] address[]       → Adres dizisi
├─ rand burst_t burst_mode         → Burst modu
├─ rand rw_t read_write           → R/W kontrol
├─ rand bit [31:0] write_data[]   → Yazma verisi dizisi
├─ resp_t response                → Slave cevabı
├─ bit [31:0] read_data           → Okuma verisi
└─ rand bit busy[]                → Busy durumları
```

**Constraints (Kısıtlamalar):**
- Burst modu ve boyuta göre adres sınırları belirlenir
- Word boundary gereksinimleri uygulanır
- 1KB sınırı kontrolü yapılır

#### **ahb_mdriver.svh** - Master Driver
```
Görev:
├─ Sequencer'dan transaction alır
├─ AHB protokol sinyallerine dönüştürür
├─ Interface clocking block (mdrv_cb) üzerinden sürücü
└─ RESET, ERROR RESPONSE gibi özel durumları işler
```

**Ana Görevler:**
- `run_phase()`: Üç ana fork'a sahip
  1. Reset Monitoring
  2. Error Response Detection
  3. Transaction Drive

#### **ahb_mmonitor.svh** - Master Monitor
```
Görev:
├─ AHB sinyallerini gözlemler
├─ Transaction'ları yakalamak için reconstruct eder
├─ Gözlemlenen transaction'ları analysis port üzerinden yayınlar
└─ Reset ve IDLE transaction'ları işler
```

#### **ahb_mseqr.svh** - Master Sequencer
```
Standart UVM Sequencer
├─ Master Driver'a transaction gönderir
└─ Virtual Sequencer tarafından kontrol edilir
```

#### **ahb_magent_config.svh** - Master Agent Konfigürasyonu
```
Konfigürasyon Parametreleri:
├─ virtual ahb_intf vif      → Interface referansı
├─ is_active                 → UVM_ACTIVE / UVM_PASSIVE
└─ Agent davranışını kontrol eder
```

#### **ahb_magent.svh** - Master Agent
```
Agent Bileşenleri:
├─ ahb_mdriver mdriver_h
├─ ahb_mmonitor mmonitor_h
├─ ahb_mseqr mseqr_h
├─ uvm_analysis_port agent_ap
└─ Tüm bileşenleri connect eder
```

#### **ahb_mseqs.svh** - Master Sequence Kütüphanesi
```
Sequence Türleri:
├─ ahb_idle_mseq      → IDLE transaction
├─ ahb_incrx_mseq     → Increment burst
├─ ahb_wrapx_mseq     → Wrap burst
├─ ahb_crt_mseq       → Constantly repeat
└─ ahb_incrbusy_mseq  → Busy duration test
```

---

### 3. **ahb_slave_agent/** - Slave UVC

#### **ahb_sxtn.svh** - Slave Transaction

**Slave Transaction Özellikleri:**
- Master transaction'ın cevabı
- Response çeşitleri (OK, ERROR, SPLIT, RETRY)
- Okuma/yazma verisi
- Timing kontrol

#### **ahb_sdriver.svh** - Slave Driver
```
Görevler:
├─ HREADY sinyalini kontrol eder
├─ HRESP sinyalini kontrol eder
├─ HRDATA sinyalini kontrol eder (okuma için)
└─ Protocol timing'ini sağlar
```

#### **ahb_smonitor.svh** - Slave Monitor
```
Gözlem:
├─ Slave sinyallerini izler
├─ Response'u kaydeder
└─ Data transfer'ı izler
```

#### **ahb_sagent.svh** - Slave Agent
```
Slave Agent mimarisi Master Agent ile aynı
├─ Slave Driver
├─ Slave Monitor
└─ Slave Sequencer
```

---

### 4. **reset_agent/** - Reset Agent

```
Basit Agent:
├─ Reset Seqencer'dan sequence alır
├─ HRESETn sinyalini kontrol eder
└─ Reset Event'ini yaratır
```

**Reset Sekansları:**
- Assert Reset
- De-assert Reset
- Reset Pulse

---

### 5. **ahb_env/** - Environment ve Test Konfigürasyonu

#### **env_config.svh** - Environment Konfigürasyonu
```
Konfigürasyon:
├─ Master Agent config
├─ Slave Agent config
├─ is_active flags
└─ Virtual interface
```

#### **ahb_env.svh** - AHB Environment
```
Build Phase:
├─ Configuration database'den config alır
├─ Sub-agent'lar için config'i set eder
├─ Tüm agent'ları create eder
└─ Coverage collector'ı create eder

Connect Phase:
├─ Agents'ı connect eder
├─ Virtual sequencer'a sequencer'ları link eder
└─ Analysis port'ları connect eder
```

#### **ahb_vseqr.svh** - Virtual Sequencer
```
Koordinasyon:
├─ reset_seqr_h      → Reset sequencer
├─ mseqr_h           → Master sequencer
└─ sseqr_h           → Slave sequencer

Master ve Slave'i koordine eder
```

#### **ahb_vseqs.svh** - Virtual Sequences
```
Synchronize Sekanslar:
├─ ahb_reset_vseq        → Reset yapıp bekleme
├─ ahb_idle_vseq         → Idle
├─ ahb_incrx_vseq        → Master increment gönder, Slave cevap ver
├─ ahb_wrapx_vseq        → Master wrap gönder, Slave cevap ver
├─ ahb_crt_vseq          → Constantly repeat transfer
├─ ahb_incrbusy_vseq     → BUSY signalling ile increment
├─ ahb_ready_vseq        → Ready signalı
└─ ahb_err_vseq          → Error response
```

#### **ahb_coverage.svh** - Coverage Collector
```
Gözlem Noktaları:
├─ Master signals coverage
├─ Slave signals coverage
├─ Cross coverage
└─ Interface coverage
```

#### **top.sv** - Top Module
```
Görevler:
├─ HCLK saat sinyali üretir
├─ ahb_intf'i instantiate eder
├─ VIF'i config_db'ye yazar
└─ UVM test'i çalıştırır
```

---

### 6. **ahb_test/** - Test Sınıfları

#### **ahb_test_pkg.sv** - Test Package
```
Include sırası:
├─ tb_defs.svh        → Enum ve define'ler
├─ Transaction classes
├─ Config classes
├─ Driver/Monitor classes
├─ Agent classes
├─ Environment class
├─ Sequencer ve Sequences
├─ Coverage class
├─ Test class
└─ Tüm import'lar
```

#### **tb_defs.svh** - Tanımlamalar
```systemverilog
// Transfer Types
typedef enum bit [1:0] {
    IDLE   = 2'b00,
    BUSY   = 2'b01,
    NONSEQ = 2'b10,
    SEQ    = 2'b11
} transfer_t;

// Burst Modes
typedef enum bit [2:0] {
    SINGLE = 3'b000,
    INCR   = 3'b001,
    WRAP4  = 3'b010,
    ...
} burst_t;

// R/W
typedef enum bit {
    READ  = 1'b0,
    WRITE = 1'b1
} rw_t;

// Response Types
typedef enum bit [1:0] {
    OKAY  = 2'b00,
    ERROR = 2'b01,
    SPLIT = 2'b11,
    RETRY = 2'b10
} resp_t;

// Size Types
typedef enum bit [2:0] {
    BYTE    = 3'b000,
    HALFWORD = 3'b001,
    WORD    = 3'b010,
    ...
} size_t;
```

#### **ahb_base_test.svh** - Base Test Sınıfı
```
Build Phase:
├─ env_config create ve konfigure
├─ VIF'i config_db'den alır
├─ Master/Slave active flags set eder
└─ env_config'i config_db'ye yazar

Environment create
```

#### **ahb_incrx_test.svh** - Increment Test
```
Test Senaryosu:
├─ Reset apply
└─ Master increment sequence, Slave response
```

#### **ahb_wrapx_test.svh** - Wrap Test
```
Test Senaryosu:
├─ Reset apply
└─ Master wrap sequence, Slave response
```

#### **ahb_crt_test.svh** - Constantly Repeat Test
```
Test Senaryosu:
├─ Reset apply
└─ Master repeatedly sends transactions
```

#### **ahb_incrbusy_test.svh** - Busy Test
```
Test Senaryosu:
├─ Reset apply
└─ Master increment with BUSY phase insertion
```

#### **ahb_err_test.svh** - Error Response Test
```
Test Senaryosu:
├─ Reset apply
└─ Master request gönder, Slave error response ver
```

#### **ahb_reset_test.svh** - Reset Test
```
Test Senaryosu:
├─ Normal transaction
├─ Reset apply → Transfer iptal
└─ Reset release ve yeni transfer
```

---

## Bileşen Detayları

### UVM Bileşen Hiyerarşisi

```
test
├─ env
│  ├─ reset_agent (UVM_ACTIVE)
│  │  ├─ reset_driver
│  │  └─ reset_sequencer
│  │
│  ├─ master_agent (UVM_ACTIVE)
│  │  ├─ ahb_mdriver
│  │  ├─ ahb_mmonitor → monitor_ap
│  │  ├─ ahb_mseqr
│  │  └─ agent_ap
│  │
│  ├─ slave_agent (UVM_ACTIVE)
│  │  ├─ ahb_sdriver
│  │  ├─ ahb_smonitor → monitor_ap
│  │  ├─ ahb_sseqr
│  │  └─ agent_ap
│  │
│  ├─ ahb_vseqr (Virtual Sequencer)
│  │  ├─ reset_seqr_h
│  │  ├─ mseqr_h
│  │  └─ sseqr_h
│  │
│  ├─ ahb_coverage
│  │  └─ analysis_export
│  │
│  ├─ ahb_master_ap
│  └─ ahb_slave_ap
│
└─ Sequences
   ├─ reset_vseq
   ├─ incrx_vseq
   ├─ wrapx_vseq
   └─ err_vseq
```

### UVM Phases (Aşamalar)

```
┌─────────────────────────────────────────┐
│  build_phase                             │
│  ├─ Component'ler create edilir         │
│  └─ Config database set edilir          │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  connect_phase                           │
│  ├─ Component'ler connect edilir        │
│  └─ Port'lar bağlanır                   │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  end_of_elaboration_phase               │
│  ├─ Hierarchy print edilir              │
│  └─ Setup completion check              │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  start_of_simulation_phase              │
│  ├─ Simulation başı işlemleri           │
│  └─ Saat enable                         │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  run_phase                               │
│  ├─ Aktif simülasyon                    │
│  ├─ Sequence'ler çalışır                │
│  └─ Transaction'lar transfer edilir     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  post_shutdown_phase                    │
│  ├─ Son işlemler                        │
│  └─ Temizlik                            │
└─────────────────────────────────────────┘
```

### Sequencer - Driver - Monitor Akışı

```
SEQUENCER                 DRIVER              INTERFACE
   │                        │                     │
   ├─ req create ──────────→│                     │
   │                        ├─ Drive Signals ────→ HADDR
   │                        │                     HWRITE
   │                        │                     HTRANS
   │                        │                     ...
   │                        │
   │                        ├──── @(posedge HCLK)
   │                        │
   │ ←─── item_done ────────│
   │                        │
   └─ req delete

MONITOR
   │
   ├─ Gözlem @ clocking block
   ├─ Transaction reconstruct
   ├─ XTN create ve doldurma
   └─ monitor_ap.write(xtn)
        │
        ↓
   COVERAGE / SCOREBOARD
   ├─ Coverage update
   └─ Transaction logging
```

---

## Çalıştırma Akışı

### 1. **Simulasyon Başlangıcı**

```
Top Module Başlatılır
    ↓
HCLK saat üretilir
    ↓
ahb_intf instantiate edilir
    ↓
VIF config_db'ye yazılır
    ↓
run_test() çağrılır
    ↓
UVM Factory oluşturulur
    ↓
Test create edilir
```

### 2. **Build Phase**

```
test::build_phase()
    ├─ env_config::create() → env_cfg
    ├─ env_cfg.vif = config_db'den alınan vif
    ├─ uvm_config_db::set("env_config", env_cfg)
    └─ ahb_env::create("env", this)
        │
        └─ ahb_env::build_phase()
            ├─ env_cfg alınır config_db'den
            ├─ master_agent config set edilir
            ├─ slave_agent config set edilir
            ├─ reset_agent::create()
            ├─ ahb_magent::create()
            ├─ ahb_sagent::create()
            ├─ ahb_vseqr::create()
            └─ ahb_coverage::create()
                │
                └─ ahb_magent::build_phase()
                    ├─ config alınır
                    ├─ ahb_mmonitor::create()
                    ├─ IF is_active: ahb_mdriver::create()
                    └─ IF is_active: ahb_mseqr::create()
```

### 3. **Connect Phase**

```
ahb_env::connect_phase()
├─ master_agent.agent_ap → ahb_coverage.analysis_export
├─ master_agent.agent_ap → ahb_master_ap
├─ slave_agent.agent_ap → ahb_slave_ap
├─ vseqr.reset_seqr_h = reset_agent.reset_seqr_h
├─ vseqr.mseqr_h = master_agent.mseqr_h (IF ACTIVE)
└─ vseqr.sseqr_h = slave_agent.sseqr_h (IF ACTIVE)
    │
    └─ ahb_magent::connect_phase()
        ├─ ahb_mmonitor.monitor_ap → agent_ap
        └─ IF is_active:
            ahb_mdriver.seq_item_port → ahb_mseqr.seq_item_export
```

### 4. **Run Phase**

```
test spawn'lar virtual sequence
    ↓
vseq::body()
    ├─ reset_vseq başlatılır
    │  ├─ reset_agent sequencer'a erişir
    │  ├─ reset seqüansı çalıştırılır
    │  └─ HRESETn assert/de-assert edilir
    │
    ├─ master_vseq başlatılır (parallel)
    │  ├─ ahb_mseqr'e erişir
    │  ├─ master sequence create edilir
    │  ├─ sequence::start(sequencer)
    │  │  ├─ sequencer.randomize()
    │  │  └─ sequencer'a send edilir
    │  │
    │  └─ driver::run_phase()
    │     ├─ seq_item_port.get_next_item(req) — transaction alınır
    │     ├─ drive() task → interface sinyallere dönüştürülür
    │     ├─ @(clocking_block) — timing kontrol
    │     └─ seq_item_port.item_done(req)
    │
    ├─ slave_vseq başlatılır (parallel)
    │  ├─ ahb_sseqr'e erişir
    │  ├─ slave sequence create edilir
    │  ├─ sequence::start(sequencer)
    │  │
    │  └─ slave_driver::run_phase()
    │     ├─ slave seqüansından req alınır
    │     ├─ HREADY, HRESP, HRDATA sinyallerini kontrol eder
    │     └─ Timing ile response verir
    │
    └─ monitor'lar çalışır (parallel)
       ├─ master_monitor::run_phase()
       │  ├─ Interface sinyalleri gözlemler
       │  ├─ Transaction reconstruct eder
       │  ├─ monitor_ap.write(xtn)
       │  └─ Coverage ve Scoreboard'a ulaşır
       │
       └─ slave_monitor::run_phase()
          ├─ Interface sinyalleri gözlemler
          └─ Response transaction'ı yakalamış olur
```

### 5. **Transaction Flow (Detaylı)**

```
┌─────────────────────────────────────────────────────────┐
│ MASTER SIDE - WRITE TRANSACTION                         │
└─────────────────────────────────────────────────────────┘

T0: ahb_incrx_mseq::body()
    req = ahb_mxtn::type_id::create()
    req.randomize() with {
        burst_mode == INCR;
        read_write == WRITE;
        address[0] == 32'h1000;
        write_data = {32'h11223344, 32'h55667788, ...}
    }
    start_item(req)
        │
        └─ sequencer'dan master_driver'a iletilir

T1: master_driver::drive()
    • First beat:
      HADDR ← 32'h1000
      HWRITE ← WRITE
      HTRANS ← NONSEQ
      HBURST ← INCR
      HSIZE ← WORD
    
    • Wait for HREADY
    
    • Subsequent beats:
      HADDR ← 32'h1004, 32'h1008, ...
      HTRANS ← SEQ
      HWDATA ← yazma verisi

T2: master_monitor::run_phase()
    @posedge HCLK: HTRANS gözlenir
    
    IF NONSEQ:
        burst_mode, size, r/w, address kaydedilir
    
    IF SEQ:
        address update edilir
        data captured edilir
    
    IF IDLE:
        transaction bitir, monitor_ap.write() yap

T3: COVERAGE
    master_monitor'un monitor_ap'ı coverage'a bağlı
    coverage::analysis_imp_write()
        cross_coverage.sample() ile coverage update edilir

┌─────────────────────────────────────────────────────────┐
│ SLAVE SIDE - RESPONSE                                   │
└─────────────────────────────────────────────────────────┘

T1: slave_driver
    HREADY kontrol eder
    • Default: HREADY = 1 (slave ready)
    • Insert wait: HREADY = 0 (slave busy)
    • After N cycles: HREADY = 1 (data ready)

T2: slave_driver (READ case)
    HRDATA ← okuma verisi
    HRESP ← OKAY (2'b00) veya ERROR (2'b01)

T3: slave_monitor
    HRDATA ve HRESP gözlemler
    Slave transaction'ı reconstruct eder
    slave_agent_ap.write() ile yayınlar
```

---

## Örnek Senaryolar

### Senaryo 1: Basit WRITE Transaction (INCR, Single Beat)

```systemverilog
// Virtual Sequence (Koordine)
class ahb_simple_write_vseq extends uvm_sequence;
    task body();
        // 1. Master tarafı: WRITE komutu gönder
        ahb_simple_mseq mseq = ahb_simple_mseq::type_id::create();
        mseq.start(vseqr.mseqr_h);  // Master sequencer'a başlat
        
        // 2. Slave tarafı: Response ver
        ahb_simple_sseq sseq = ahb_simple_sseq::type_id::create();
        sseq.start(vseqr.sseqr_h);  // Slave sequencer'a başlat
    endtask
endclass

// Master Sequence
class ahb_simple_mseq extends uvm_sequence#(ahb_mxtn);
    task body();
        req = ahb_mxtn::type_id::create("req");
        start_item(req);
        
        // WRITE transaction oluştur
        assert(req.randomize() with {
            read_write == WRITE;      // Write operation
            burst_mode == INCR;       // Increment mode
            address[0] == 32'h1000;   // Sabit adres
            write_data[0] == 32'hDEADBEEF;
            trans_type[0] == NONSEQ;  // Non-sequential transfer
        });
        
        finish_item(req);
    endtask
endclass

// Slave Sequence
class ahb_simple_sseq extends uvm_sequence#(ahb_sxtn);
    task body();
        req = ahb_sxtn::type_id::create("req");
        start_item(req);
        
        // WRITE response
        assert(req.randomize() with {
            response == OKAY;    // Success response
            ready_delay == 0;    // No wait
        });
        
        finish_item(req);
    endtask
endclass

// Timeline
Saat    Master                   Slave           Interface
─────────────────────────────────────────────────────────
T0      NONSEQ, W, INCR,         Wait for req    HADDR=1000
        addr=1000,                               HWRITE=1
        size=WORD                                HTRANS=10
                                                 HBURST=001
        
T1      SEQ, IDLE               Ready, OK        HREADY=1
        addr=1004,                               HRESP=00
        Write data ready                         HWDATA=DEADBEEF

T2      -                        -                Transaction
                                                 complete
```

### Senaryo 2: INCR Burst ile READ (4-beat)

```
Timeline:
Clock  HADDR       HTRANS  HBURST  HWDATA    HREADY  HRDATA
─────────────────────────────────────────────────────────
T0     0x1000      NONSEQ  INCR    ----      1       ----
T1     0x1004      SEQ     INCR    ----      1       data0 (from T0)
T2     0x1008      SEQ     INCR    ----      1       data1 (from T1)
T3     0x100C      SEQ     INCR    ----      1       data2 (from T2)
T4     0x1010      IDLE    0       ----      1       data3 (from T3)
```

### Senaryo 3: BUSY Insertions

```
Clock  HTRANS  HADDR   Ready  Event
─────────────────────────────────
T0     NONSEQ  0x1000  0      Slave başta hazır değil
T1     BUSY    0x1000  0      Master bekleme inserti
T2     NONSEQ  0x1004  1      Slave ready, yeni adres
T3     SEQ     0x1008  1      Devam
T4     IDLE    -       1      Son
```

### Senaryo 4: ERROR Response

```
Clock  HTRANS  HADDR   Data    HREADY  HRESP   Event
─────────────────────────────────────────────────
T0     NONSEQ  0x1000  ----    1       OK      Request
T1     SEQ     0x1004  ----    1       OK      Devam
T2     SEQ     0x1008  ----    0       ERROR   Error! Slave tutuklandı
T3     IDLE    -       ----    1       OK      Master IDLE gönder
```

### Senaryo 5: WRAP Burst

```
Başlangıç Adresi: 0x1008, Burst Mode: WRAP4, Size: WORD
Adresler wrap around yapacak.

Clock  HADDR       Event
─────────────────────────
T0     0x1008      Start
T1     0x100C      +4
T2     0x1000      Wrap! (4 beat sınırında)
T3     0x1004      Devam
T4     0x1008      Tekrar wrap
```

---

## Kod Okuma Rehberi

### 1. Test Çalıştırırken Ne Olur?

```
$ make test_incrx

1. Makefile compile.f dosyasından tüm .sv ve .svh dosyaları compile eder
2. Simulasyon başlatılır (Vivado Simulator)
3. top.sv module'u load edilir
4. UVM components build edilir
5. Connections yapılır
6. Virtual sequence başlat
7. Transactions flow'u
8. Simülasyon bitiş
9. Coverage report generate
10. Waveform file (.vcd) kaydedilir
```

### 2. Test Package Compilation Order

```systemverilog
// ahb_test_pkg.sv içinde include sırası ÇOOOOK önemli!

`include "tb_defs.svh"              // Enum tanımları
`include "ahb_mxtn.svh"             // Master XTN
`include "ahb_sxtn.svh"             // Slave XTN
`include "ahb_magent_config.svh"    // Master config
`include "ahb_sagent_config.svh"    // Slave config
`include "env_config.svh"           // Env config

`include "ahb_mdriver.svh"          // Master driver
`include "ahb_mmonitor.svh"         // Master monitor
`include "ahb_mseqr.svh"            // Master sequencer
`include "ahb_mseqs.svh"            // Master sequences
`include "ahb_magent.svh"           // Master agent

`include "ahb_sdriver.svh"          // Slave driver
`include "ahb_smonitor.svh"         // Slave monitor
`include "ahb_sseqr.svh"            // Slave sequencer
`include "ahb_sseqs.svh"            // Slave sequences
`include "ahb_sagent.svh"           // Slave agent

`include "reset_seqs.svh"           // Reset sequences
`include "reset_driver.svh"         // Reset driver
`include "reset_seqr.svh"           // Reset sequencer
`include "reset_agent.svh"          // Reset agent

`include "ahb_vseqr.svh"            // Virtual sequencer
`include "ahb_vseqs.svh"            // Virtual sequences
`include "ahb_coverage.svh"         // Coverage

`include "ahb_env.svh"              // Environment
`include "ahb_base_test.svh"        // Base test
`include "ahb_incrx_test.svh"       // Specific tests
// ... diğer test'ler
```

### 3. Debuglama İçin İpuçları

```systemverilog
// UVM messaging levels
`uvm_info(...)      // Normal bilgi (UVM_MEDIUM)
`uvm_warning(...)   // Uyarı
`uvm_error(...)     // Hata (test başarısız olmaz)
`uvm_fatal(...)     // Kritik hata (test immediate fails)

// Debugging aktif hale getir
+UVM_VERBOSITY=UVM_FULL

// Transaction print
req.print()         // Transaction'ı ekrana yaz

// Hierarchy print
test.print()        // Component hiyerarşisini yaz

// Clocking block debugging
$timeformat(-9, 2, " ns")
$display("@%t: HADDR=%h, HWRITE=%b", $time, vif.HADDR, vif.HWRITE);
```

---

## Özet

Bu AHB2 testbench şunları gösterir:

✅ **Master-Slave Protocol Testing**
- Master transactions gönderir
- Slave responses verir
- Full-duplex communication

✅ **UVM Best Practices**
- Configuration-driven test setup
- Reusable agent architecture
- Virtual sequencing for test coordination
- Analysis port usage for coverage

✅ **Protocol Specifics**
- Burst modes (INCR, WRAP)
- HREADY (slave ready) signaling
- HRESP (error responses)
- Address alignment constraints

✅ **Test Scenarios**
- Normal operations
- Error conditions
- Busy insertions
- Reset scenarios

---

## İleri Öğrenme Kaynakları

1. **UVM User Guide** - UVM specification
2. **AHB Protocol Documentation** - ARM AMBA specs
3. **SystemVerilog LRM** - Language specification
4. Bu projedeki her dosyayı satır satır oku
5. Waveform'u Vivado Wave Viewer'da aç ve gözlemle

Başarılar! 🚀
