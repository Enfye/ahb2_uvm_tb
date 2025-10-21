# AHB2 UVM Testbench - Kod Örnekleri ve Detaylı Anlatım

## Bölüm 1: Temel Bileşenleri Adım Adım Anlamak

### 1.1 Transaction Sınıfı (ahb_mxtn.svh)

```systemverilog
// ============================================
// STEP 1: Transaction tanımında random fields
// ============================================

class ahb_mxtn extends uvm_sequence_item;
    `uvm_component_utils(ahb_mxtn)
    
    // === KONTROL SİNYALLERİ (Master tarafından set edilir) ===
    rand transfer_t trans_type[];    // Transfer tipi: IDLE(00), BUSY(01), NONSEQ(10), SEQ(11)
    rand burst_t burst_mode;         // Burst modu: SINGLE, INCR, WRAP4, WRAP8, WRAP16
    rand rw_t read_write;            // Okuma(0) veya Yazma(1)
    rand size_t trans_size;          // Transfer boyutu: BYTE, HALFWORD, WORD, ...
    
    // === ADRES ve VERİ ===
    rand bit [31:0] address[];       // İlk beat'te master tarafından gönderilen adres
    rand bit [31:0] write_data[];    // Yazma verisi (write transaction'ında)
    
    // === RESPONSE (Slave tarafından set edilir) ===
    resp_t response;                 // OKAY(00), ERROR(01), SPLIT(11), RETRY(10)
    bit [31:0] read_data;            // Read transaction'ndan okunan veri
    
    // === TIMING ===
    bit ready;                       // HREADY sinyali
    rand bit busy[];                 // Busy insertion sinyalleri
    
    // === CONSTRAINTS ===
    
    // Burst mode'a göre adres array boyutu belirlenir
    constraint addr_size_c {
        if (burst_mode == SINGLE)
            address.size == 1;        // 1 beat
        if (burst_mode == INCR)
            address.size inside {[1:16]};  // 1-16 beat (variable)
        if (burst_mode inside {WRAP4, WRAP4A})
            address.size == 4;        // Exactly 4 beats
        if (burst_mode inside {WRAP8, WRAP8A})
            address.size == 8;        // Exactly 8 beats
    }
    
    // İşlevler
    extern function new(string name = "ahb_mxtn");
    extern function void post_randomize();
endclass

// ============================================
// ÖRNEK: Transaction Randomization
// ============================================

// Bu nasıl yapılır:
ahb_mxtn xtn = ahb_mxtn::type_id::create("xtn");

// Seçenek 1: Tamamen random
xtn.randomize();

// Seçenek 2: Bazı constraints ile
xtn.randomize() with {
    read_write == WRITE;          // Yazma işlemi zorunlu
    burst_mode == INCR;           // INCR burst zorunlu
    trans_size == WORD;           // 32-bit transfer
};

// Seçenek 3: Belirli değerler
xtn.randomize() with {
    address[0] == 32'h0;
    write_data[0] == 32'hDEADBEEF;
};
```

### 1.2 Agent Bileşenleri (Macro-level vs Micro-level)

```systemverilog
// ============================================
// MASTER AGENT YAPISI
// ============================================

/*
    ahb_magent (CONTAINER)
    ├─ ahb_mdriver (Aktif - Signals'ı interface'e yazdırır)
    ├─ ahb_mmonitor (Pasif - Interface'i gözlemler)
    ├─ ahb_mseqr (Koordinatör - Driver'a transaction verir)
    └─ uvm_analysis_port (Gözlemleri diğer bileşenlere yayınlar)
*/

class ahb_magent extends uvm_agent;
    `uvm_component_utils(ahb_magent)
    
    // === BILEŞENLER ===
    ahb_mdriver mdriver_h;          // Transactions → Hardware signals
    ahb_mmonitor mmonitor_h;        // Hardware signals → Gözlem transactions
    ahb_mseqr mseqr_h;              // Sequencer - Driver coordinator
    
    // === CONFIG ===
    ahb_magent_config magt_cfg;     // Agent konfigürasyonu
    
    // === ANALYSIS PORT ===
    uvm_analysis_port#(ahb_mxtn) agent_ap;
    
    // === BUILD PHASE ===
    function void build_phase(uvm_phase phase);
        // 1. Config database'den konfigürasyon al
        if (!uvm_config_db#(ahb_magent_config)::get(
            this, "", "ahb_magent_config", magt_cfg)) 
        begin
            `uvm_fatal("NO_CONFIG", "Cannot find agent config!")
        end
        
        // 2. Monitor her zaman create edilir (pasif gözlem)
        mmonitor_h = ahb_mmonitor::type_id::create("mmonitor_h", this);
        
        // 3. Active/Passive mode check
        if (magt_cfg.is_active == UVM_ACTIVE) begin
            // 4a. Aktif mod: Driver ve Sequencer gerekli
            mdriver_h = ahb_mdriver::type_id::create("mdriver_h", this);
            mseqr_h = ahb_mseqr::type_id::create("mseqr_h", this);
        end
        // 4b. Pasif mod: Sadece gözlem, kontrol yok
    endfunction
    
    // === CONNECT PHASE ===
    function void connect_phase(uvm_phase phase);
        // Monitor'un gözlemlerini agent port'una bağla
        mmonitor_h.monitor_ap.connect(agent_ap);
        
        if (magt_cfg.is_active == UVM_ACTIVE) begin
            // Driver'ı Sequencer'a bağla (kritik!)
            // Driver sequencer'dan transaction ister
            // Sequencer test'ten transaction alır
            mdriver_h.seq_item_port.connect(mseqr_h.seq_item_export);
        end
    endfunction
endclass

// ============================================
// DRIVER NASIL ÇALIŞIR?
// ============================================

class ahb_mdriver extends uvm_driver#(ahb_mxtn);
    
    virtual ahb_intf vif;           // Interface reference
    
    // === RUN PHASE (Aktif çalıştırma) ===
    task run_phase(uvm_phase phase);
        forever begin
            // 1. Sequencer'dan next transaction iste
            seq_item_port.get_next_item(req);
            
            // 2. HREADY ve BUSY ekle
            void'(req.add_busy());
            
            // 3. Hardware signals'a dönüştür
            drive_transaction(req);
            
            // 4. Sequencer'a transaction'ı bittiğini söyle
            seq_item_port.item_done(req);
        end
    endtask
    
    // === DRIVE GÖREV ===
    task drive_transaction(ahb_mxtn req);
        int beat_index = 0;
        
        foreach (req.address[i]) begin
            // Her beat için:
            
            // 1. Kontrol sinyallerini set et
            vif.mdrv_cb.HADDR <= req.address[i];
            vif.mdrv_cb.HWRITE <= req.read_write;
            vif.mdrv_cb.HTRANS <= req.trans_type[beat_index];
            vif.mdrv_cb.HBURST <= req.burst_mode;
            vif.mdrv_cb.HSIZE <= req.trans_size;
            
            // 2. Yazma verisi varsa yaz
            if (req.read_write == WRITE)
                vif.mdrv_cb.HWDATA <= req.write_data[i];
            
            // 3. Clock pulse bekle (clocking block'ı trigger et)
            @(vif.mdrv_cb);
            
            // 4. HREADY kontrol et - Slave hazır olana kadar bekle
            while (!vif.mdrv_cb.HREADY)
                @(vif.mdrv_cb);
            
            beat_index++;
        end
        
        // Transcation bitince IDLE gönder
        vif.mdrv_cb.HTRANS <= IDLE;
    endtask
endclass

// ============================================
// MONITOR NASIL ÇALIŞIR?
// ============================================

class ahb_mmonitor extends uvm_monitor;
    
    virtual ahb_intf vif;
    uvm_analysis_port#(ahb_mxtn) monitor_ap;
    
    // === RUN PHASE (Gözleme) ===
    task run_phase(uvm_phase phase);
        forever begin
            // 1. Yeni transaction container'ı oluştur
            ahb_mxtn xtn = ahb_mxtn::type_id::create("xtn");
            
            // 2. Transfer tipi gözle
            xtn.trans_type[0] = vif.mmon_cb.HTRANS;
            
            // 3. Eğer IDLE ise, basit transaction yaz
            if (xtn.trans_type[0] == IDLE) begin
                monitor_ap.write(xtn);
                @(vif.mmon_cb);
                continue;
            end
            
            // 4. Normal transfer: Tüm sinyalleri al
            xtn.burst_mode = vif.mmon_cb.HBURST;
            xtn.trans_size = vif.mmon_cb.HSIZE;
            xtn.read_write = vif.mmon_cb.HWRITE;
            xtn.address[0] = vif.mmon_cb.HADDR;
            
            // 5. Response ve Data al
            @(vif.mmon_cb);
            xtn.response = vif.mmon_cb.HRESP;
            
            if (xtn.read_write == READ)
                xtn.read_data = vif.mmon_cb.HRDATA;
            else
                xtn.write_data[0] = vif.mmon_cb.HWDATA;
            
            // 6. Gözlemlenen transaction'ı analysis port üzerinden yayınla
            monitor_ap.write(xtn);
        end
    endtask
endclass
```

## Bölüm 2: Virtual Sequences (Koordinasyon)

### 2.1 Virtual Sequence Nedir?

```systemverilog
/*
Virtual Sequence = Master + Slave sekanslarını koordine eder

        Virtual Sequence
        ├─ Master Sequencer'a write_seq başlat
        └─ Slave Sequencer'a response_seq başlat
        (Bu ikisi paralel çalışır)
*/

class ahb_base_vseq extends uvm_sequence#(uvm_sequence_item);
    `uvm_object_utils(ahb_base_vseq)
    
    // Virtual sequencer referansları
    ahb_vseqr vseqr_h;              // Virtual sequencer
    ahb_mseqr mseqr_h;              // Master sequencer
    ahb_sseqr sseqr_h;              // Slave sequencer
    reset_seqr reset_seqr_h;        // Reset sequencer
    
    // Body görev (test yapısı)
    task body();
        // Virtual sequencer'dan cast işlemi
        if (!$cast(vseqr_h, m_sequencer)) begin
            `uvm_fatal("CAST_ERR", "vseqr cast failed!");
        end
        
        // Tüm sequencer referanslarını al
        reset_seqr_h = vseqr_h.reset_seqr_h;
        mseqr_h = vseqr_h.mseqr_h;
        sseqr_h = vseqr_h.sseqr_h;
    endtask
endclass

// ============================================
// ÖRNEK 1: Simple WRITE Transaction
// ============================================

class ahb_write_vseq extends ahb_base_vseq;
    `uvm_object_utils(ahb_write_vseq)
    
    task body();
        super.body();
        
        ahb_write_mseq write_mseq;
        ahb_write_sseq write_sseq;
        
        write_mseq = ahb_write_mseq::type_id::create("write_mseq");
        write_sseq = ahb_write_sseq::type_id::create("write_sseq");
        
        // Paralel olarak çalıştır
        fork
            write_mseq.start(mseqr_h);  // Master: Write komutu gönder
            write_sseq.start(sseqr_h);  // Slave: Accept ve ready
        join
    endtask
endclass

// ============================================
// ÖRNEK 2: INCR Burst (Real Test)
// ============================================

class ahb_incrx_vseq extends ahb_base_vseq;
    `uvm_object_utils(ahb_incrx_vseq)
    
    task body();
        super.body();
        
        ahb_incrx_mseq incrx_mseq;
        ahb_ready_sseq ready_sseq;
        
        incrx_mseq = ahb_incrx_mseq::type_id::create("incrx_mseq");
        ready_sseq = ahb_ready_sseq::type_id::create("ready_sseq");
        
        // Parallel execution:
        // Master: INCR burst (multi-beat transfer)
        // Slave: Synchronized ready responses
        fork
            incrx_mseq.start(mseqr_h);
            ready_sseq.start(sseqr_h);
        join
    endtask
endclass
```

### 2.2 Master Sequence Detayı

```systemverilog
// ============================================
// MASTER SEQUENCE YAZMA
// ============================================

class ahb_incrx_mseq extends uvm_sequence#(ahb_mxtn);
    `uvm_object_utils(ahb_incrx_mseq)
    
    task body();
        // INCR burst transaction oluştur
        req = ahb_mxtn::type_id::create("req");
        
        start_item(req);
        
        // Randomize ile constraints yapı
        if (!req.randomize() with {
            // Zorunlu constraints
            burst_mode == INCR;         // INCR mode
            address.size inside {[2:4]}; // 2-4 beats
            trans_size == WORD;         // 32-bit transfers
            
            // Address alignment (word boundary)
            foreach (address[i])
                address[i][1:0] == 2'b0;
            
            // Address increment
            address[1] == address[0] + 4;
            address[2] == address[0] + 8;
            
            // Multi-beat transfer
            trans_type[0] == NONSEQ;    // First beat: non-sequential
            trans_type[1] == SEQ;       // Subsequent: sequential
            trans_type[2] == SEQ;
            
            // Write operation with data
            read_write == WRITE;
            write_data.size == address.size;
        }) begin
            `uvm_error("RND_ERR", "Randomization failed!");
        end
        
        finish_item(req);
        
        `uvm_info("INCR_SEQ", $sformatf(
            "Sent INCR burst: addr=%h, beats=%0d, data=%h",
            req.address[0], req.address.size, req.write_data[0]
        ), UVM_MEDIUM)
    endtask
endclass

// ============================================
// İMPLEMENTASYON: Timeline
// ============================================

/*
Bu sequence çalıştığında timeline şöyle olur:

Saat   Seq.start    Driver        Interface       Slave
───────────────────────────────────────────────────────────
T0     req oluş.    -             -               -
       
T1     start_item   get_next_item -               -
       randomize
       finish_item  
       
T2                  drive @CB     HTRANS=NONSEQ   -
       HADDR=addr[0]
       HBURST=INCR
       
T3                  wait HREADY   @CB            HREADY=0
                                              (Slave busy)
       
T4                  wait HREADY   @CB            HREADY=1
       drive next              HTRANS=SEQ
       beat       HADDR=addr[1]
       
T5                  wait HREADY   @CB            HREADY=1
                                  HTRANS=SEQ
                                  HADDR=addr[2]
       
T6                  drive IDLE    HTRANS=IDLE
                    item_done
       
T7     seq end      -             -               -
*/
```

## Bölüm 3: Test Yazma

### 3.1 Basit Test Yapısı

```systemverilog
// ============================================
// BASE TEST - Tüm testler bundan inherit eder
// ============================================

class ahb_base_test extends uvm_test;
    `uvm_component_utils(ahb_base_test)
    
    ahb_env env_h;                  // Test'in environment'ı
    virtual ahb_intf vif;           // Interface reference
    env_config env_cfg;             // Configuration
    
    // ========== BUILD PHASE ==========
    function void build_phase(uvm_phase phase);
        // 1. Config object oluştur
        env_cfg = env_config::type_id::create("env_cfg");
        
        // 2. VIF'i config_db'den al
        if (!uvm_config_db#(virtual ahb_intf)::get(
            this, "", "ahb_intf", vif)) 
        begin
            `uvm_fatal("NO_VIF", "VIF not found in config_db!");
        end
        
        // 3. Config'i doldur
        env_cfg.vif = vif;
        env_cfg.m_is_active = UVM_ACTIVE;
        env_cfg.s_is_active = UVM_ACTIVE;
        
        // 4. Config'i config_db'ye yaz (Environment alabilsin diye)
        uvm_config_db#(env_config)::set(this, "*", "env_config", env_cfg);
        
        // 5. Parent build_phase'i çağır
        super.build_phase(phase);
        
        // 6. Environment create et
        env_h = ahb_env::type_id::create("env_h", this);
    endfunction
    
    // ========== RUN PHASE ==========
    task run_phase(uvm_phase phase);
        // Overridden by derived test classes
    endtask
endclass

// ============================================
// SPECİFİK TEST - INCR Burst Test
// ============================================

class ahb_incrx_test extends ahb_base_test;
    `uvm_component_utils(ahb_incrx_test)
    
    // Virtual sequences
    ahb_reset_vseq reset_vseq_h;
    ahb_incrx_vseq incrx_vseq_h;
    ahb_idle_vseq idle_vseq_h;
    
    // Build: Base'den inherit et (hiçbir şey yapmaz)
    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
    endfunction
    
    // Run: Test senaryosu
    task run_phase(uvm_phase phase);
        phase.raise_objection(this);  // Simülasyonu tuttu
        
        // 1. Reset yap
        reset_vseq_h = ahb_reset_vseq::type_id::create("reset_vseq_h");
        reset_vseq_h.start(env_h.vseqr_h);
        
        // 2. INCR transactions gönder (10 kez)
        repeat(10) begin
            incrx_vseq_h = ahb_incrx_vseq::type_id::create("incrx_vseq_h");
            incrx_vseq_h.start(env_h.vseqr_h);
        end
        
        // 3. Idle ile bitir
        idle_vseq_h = ahb_idle_vseq::type_id::create("idle_vseq_h");
        idle_vseq_h.start(env_h.vseqr_h);
        
        // 4. Biraz daha bekle
        #100;
        
        phase.drop_objection(this);  // Simülasyon bitmesine izin ver
    endtask
endclass
```

## Bölüm 4: Debugging ve Observation

### 4.1 Waveform Analysis

```systemverilog
// ============================================
// 1. do dosyasıyla Waveform'u açmak
// ============================================

// ahb_wave.do
add_wave -position end -format Logic \
    -radix unsigned /top/intf/HCLK
add_wave -position end -format Logic \
    -radix unsigned /top/intf/HRESETn
add_wave -position end -format Literal \
    -radix unsigned /top/intf/HTRANS
add_wave -position end -format Logic /top/intf/HREADY
add_wave -position end -format Literal \
    /top/intf/HADDR
add_wave -position end -format Literal \
    /top/intf/HWDATA
add_wave -position end -format Literal \
    /top/intf/HRDATA

run all
quit

// ============================================
// 2. UVM Messaging
// ============================================

// Driver'da debug mesajı
`uvm_info(get_type_name(), "Starting transaction drive", UVM_MEDIUM)

// Monitor'da kritik mesaj
`uvm_warning("MON_WARN", "Unexpected response from slave")

// Test'te hata
`uvm_error("TEST_ERR", "Assertion failed")

// Fatal error (test immediately fails)
`uvm_fatal("SETUP_ERR", "Cannot connect port")

// ============================================
// 3. Transaction Print
// ============================================

// Driver'da
req.print($sformatf("@%t Transaction from Master", $time));

// Monitor'da
xtn.print();

// Test'de
$display("Sending %p", req);

// ============================================
// 4. Yapılandırma Bilgisini Print Etme
// ============================================

// Environment'da
function void end_of_elaboration_phase(uvm_phase phase);
    this.print();  // Tüm hierarchy
    env_cfg.print();  // Config
endfunction
```

### 4.2 Simulasyon Çalıştırma

```bash
# ============================================
# 1. Compile
# ============================================
xvlog -sv +incdir+. -f compile.f

# ============================================
# 2. Elaborate
# ============================================
xelab -debug all top

# ============================================
# 3. Simulate
# ============================================
# Verbosity ile - Tüm UVM messages'ları gör
xsim top -gui +UVM_VERBOSITY=UVM_FULL

# Specific test ile
xsim top -gui -testname ahb_incrx_test

# ============================================
# 4. Coverage ile
# ============================================
xsim top -gui +UVM_VERBOSITY=UVM_LOW
# (Waveform dosyası .wdb formatında kaydedilir)
```

## Özet: Veri Akışı

```
TEST
  │
  ├─1. test::build_phase()
  │   └─ env create + config setup
  │
  ├─2. env::build_phase()
  │   ├─ master_agent::create()
  │   │  ├─ mdriver
  │   │  ├─ mmonitor
  │   │  └─ mseqr
  │   └─ slave_agent::create()
  │
  ├─3. env::connect_phase()
  │   └─ mdriver ↔ mseqr bağla
  │
  └─4. test::run_phase()
      └─ virtual_sequence.start(vseqr)
         ├─ master_seq.start(mseqr)
         │  ├─ req.randomize()
         │  ├─ mdriver.drive(req)
         │  │  ├─ Interface signals set
         │  │  ├─ @clocking block
         │  │  └─ HREADY wait
         │  │
         │  └─ req done
         │
         └─ slave_seq.start(sseqr)
            ├─ Synchronized response
            └─ Signals: HREADY, HRESP, HRDATA

MONITOR (Her zaman çalışır)
  └─ Interface gözleme
     ├─ Signals capture
     ├─ XTN reconstruct
     └─ analysis_port.write()
        └─ COVERAGE / SCOREBOARD
```

Başarılar! 🎯
