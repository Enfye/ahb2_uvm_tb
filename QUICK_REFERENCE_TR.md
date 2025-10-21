# AHB2 UVM Testbench - Hızlı Referans Kartı

## Dosya Yapısı Özet

| Dosya | Amaç | Önemli Sınıflar |
|-------|------|-----------------|
| **rtl/ahb_intf.sv** | Hardware Interface | `interface ahb_intf`, clocking blocks |
| **tb_defs.svh** | Type Definitions | Enum'lar: `transfer_t`, `burst_t`, `rw_t`, `resp_t` |
| **ahb_mxtn.svh** | Master Transaction | `class ahb_mxtn` |
| **ahb_mdriver.svh** | Master Drive | `class ahb_mdriver extends uvm_driver` |
| **ahb_mmonitor.svh** | Master Gözlem | `class ahb_mmonitor extends uvm_monitor` |
| **ahb_mseqr.svh** | Master Sequencer | `class ahb_mseqr extends uvm_sequencer` |
| **ahb_mseqs.svh** | Master Sequences | `class ahb_mbase_seq`, `ahb_idle_mseq`, `ahb_incrx_mseq` |
| **ahb_magent_config.svh** | Master Config | `class ahb_magent_config` |
| **ahb_magent.svh** | Master Agent | `class ahb_magent extends uvm_agent` |
| **ahb_sxtn.svh** | Slave Transaction | `class ahb_sxtn` |
| **ahb_sdriver.svh** | Slave Drive | `class ahb_sdriver extends uvm_driver` |
| **ahb_smonitor.svh** | Slave Gözlem | `class ahb_smonitor extends uvm_monitor` |
| **ahb_sseqr.svh** | Slave Sequencer | `class ahb_sseqr extends uvm_sequencer` |
| **ahb_sseqs.svh** | Slave Sequences | `class ahb_sbase_seq`, `ahb_ready_sseq` |
| **ahb_sagent_config.svh** | Slave Config | `class ahb_sagent_config` |
| **ahb_sagent.svh** | Slave Agent | `class ahb_sagent extends uvm_agent` |
| **reset_agent.svh** | Reset Agent | `class reset_agent extends uvm_agent` |
| **env_config.svh** | Environment Config | `class env_config extends uvm_object` |
| **ahb_vseqr.svh** | Virtual Sequencer | `class ahb_vseqr extends uvm_sequencer` |
| **ahb_vseqs.svh** | Virtual Sequences | `class ahb_base_vseq`, koordine sekanslar |
| **ahb_coverage.svh** | Coverage Collector | `class ahb_coverage extends uvm_subscriber` |
| **ahb_env.svh** | Environment | `class ahb_env extends uvm_env` |
| **ahb_base_test.svh** | Base Test | `class ahb_base_test extends uvm_test` |
| **ahb_incrx_test.svh** | INCR Test | `class ahb_incrx_test extends ahb_base_test` |
| **ahb_wrapx_test.svh** | WRAP Test | `class ahb_wrapx_test extends ahb_base_test` |
| **ahb_err_test.svh** | Error Test | `class ahb_err_test extends ahb_base_test` |
| **top.sv** | Top Module | `module top` |

---

## Sinyaller Quick Reference

### Master Sinyalleri

```
Çıkış (Master → Slave):
├─ HADDR[31:0]     Address bus
├─ HWDATA[31:0]    Write data bus
├─ HWRITE          Write enable (1=write, 0=read)
├─ HTRANS[1:0]     Transfer type (IDLE=00, BUSY=01, NONSEQ=10, SEQ=11)
├─ HBURST[2:0]     Burst type (SINGLE=0, INCR=1, WRAP4=2, ...)
├─ HSIZE[2:0]      Transfer size (BYTE=0, HALFWORD=1, WORD=2, ...)
└─ (Optional HPROT, HPROT, ...) Protection signals

Giriş (Slave → Master):
├─ HRDATA[31:0]    Read data bus
├─ HREADY          Slave ready (1=ready, 0=wait)
└─ HRESP[1:0]      Response (OKAY=00, ERROR=01, RETRY=10, SPLIT=11)

Global:
├─ HCLK             Clock
└─ HRESETn          Reset (active low)
```

### Clocking Blocks

```systemverilog
// Master Driver CB
clocking mdrv_cb@(posedge HCLK);
    output HTRANS, HBURST, HSIZE, HWRITE, HADDR, HWDATA;
    input HREADY, HRESP, HRDATA;
endclocking

// Master Monitor CB
clocking mmon_cb@(posedge HCLK);
    input HRESETn, HREADY, HTRANS, HBURST, HSIZE;
    input HWRITE, HADDR, HWDATA, HRESP, HRDATA;
endclocking

// Slave Driver CB
clocking sdrv_cb@(posedge HCLK);
    input HTRANS, HBURST, HSIZE, HWRITE, HADDR, HWDATA;
    output HREADY, HRESP, HRDATA;
endclocking

// Slave Monitor CB
clocking smon_cb@(posedge HCLK);
    input HREADY, HTRANS, HBURST, HSIZE;
    input HWRITE, HADDR, HWDATA, HRESP, HRDATA;
endclocking
```

---

## Senaryo Hızlı Başlat

### Senaryo 1: Basit WRITE (SINGLE, 1 Beat)

```
Komut:        xsim top -testname ahb_base_test
Zaman:        ~50 ns
Timeline:
  T0: HTRANS=NONSEQ, HWRITE=1, HADDR=random, HWDATA=random
  T1: HTRANS=IDLE, (HREADY gerekirse)
```

### Senaryo 2: INCR READ (Multi-beat, 2-4 beats)

```
Komut:        xsim top -testname ahb_incrx_test
Zaman:        ~500 ns
Timeline:
  T0: HTRANS=NONSEQ, HWRITE=0, HADDR=0x1000
  T1: HTRANS=SEQ,    HWRITE=0, HADDR=0x1004, HRDATA='[0]'
  T2: HTRANS=SEQ,    HWRITE=0, HADDR=0x1008, HRDATA='[1]'
  T3: HTRANS=IDLE,                           HRDATA='[2]'
```

### Senaryo 3: WRAP Burst

```
Komut:        xsim top -testname ahb_wrapx_test
Zaman:        ~300 ns
Özellik:      Addresses wrap 4/8/16 beat boundary'sinde
```

### Senaryo 4: BUSY Insertion

```
Komut:        xsim top -testname ahb_incrbusy_test
Zaman:        ~1000 ns
Özellik:      HTRANS=BUSY insertions between transfers
```

### Senaryo 5: Error Response

```
Komut:        xsim top -testname ahb_err_test
Zaman:        ~200 ns
Özellik:      Slave HRESP=ERROR (2'b01) ile cevap verir
```

### Senaryo 6: Reset

```
Komut:        xsim top -testname ahb_reset_test
Zaman:        ~300 ns
Özellik:      HRESETn assert/release işlemini test eder
```

---

## UVM Component Hiyerarşi Diagram

```
test_top (top.sv module)
    |
    +---> ahb_interface (ahb_intf.sv)
    |       |
    |       +---> mdrv_cb, mmon_cb (master)
    |       +---> sdrv_cb, smon_cb (slave)
    |       +---> reset logic
    |
    +---> UVM Test (ahb_base_test.svh)
            |
            +---> uvm_env (ahb_env.svh)
                    |
                    +---> reset_agent
                    |       +---> reset_driver
                    |       +---> reset_sequencer
                    |
                    +---> ahb_magent (Master Agent)
                    |       +---> ahb_mdriver
                    |       +---> ahb_mmonitor --[analysis_port]--> coverage
                    |       +---> ahb_mseqr
                    |
                    +---> ahb_sagent (Slave Agent)
                    |       +---> ahb_sdriver
                    |       +---> ahb_smonitor --[analysis_port]
                    |       +---> ahb_sseqr
                    |
                    +---> ahb_vseqr (Virtual Sequencer)
                    |       +---> reset_seqr_h (reference)
                    |       +---> mseqr_h (reference)
                    |       +---> sseqr_h (reference)
                    |
                    +---> ahb_coverage (Subscriber)
                    |
                    +---> analysis_ports
                            +---> ahb_master_ap
                            +---> ahb_slave_ap

            |
            +---> Virtual Sequences (ahb_vseqs.svh)
                    +---> ahb_reset_vseq
                    +---> ahb_incrx_vseq
                    +---> ahb_wrapx_vseq
                    +---> ahb_crt_vseq
                    +---> ahb_incrbusy_vseq
                    +---> ahb_err_vseq
```

---

## Compilation Order (Çooook Önemli!)

```makefile
# compile.f dosyasında include sırası:

# 1. UVM Library
+incdir+$UVM_HOME/src
$UVM_HOME/src/uvm.sv

# 2. Interface
./rtl/ahb_intf.sv

# 3. Test Package Components (In Order!)
./ahb_test/tb_defs.svh

./ahb_master_agent/ahb_mxtn.svh
./ahb_slave_agent/ahb_sxtn.svh

./ahb_master_agent/ahb_magent_config.svh
./ahb_slave_agent/ahb_sagent_config.svh
./reset_agent/reset_agent_config.svh
./ahb_env/env_config.svh

./ahb_master_agent/ahb_mdriver.svh
./ahb_master_agent/ahb_mmonitor.svh
./ahb_master_agent/ahb_mseqr.svh
./ahb_master_agent/ahb_mseqs.svh
./ahb_master_agent/ahb_magent.svh

./ahb_slave_agent/ahb_sdriver.svh
./ahb_slave_agent/ahb_smonitor.svh
./ahb_slave_agent/ahb_sseqr.svh
./ahb_slave_agent/ahb_sseqs.svh
./ahb_sagent.svh

./reset_agent/reset_seqs.svh
./reset_agent/reset_driver.svh
./reset_agent/reset_seqr.svh
./reset_agent/reset_agent.svh

./ahb_env/ahb_vseqr.svh
./ahb_env/ahb_vseqs.svh
./ahb_env/ahb_coverage.svh
./ahb_env/ahb_env.svh

./ahb_test/ahb_base_test.svh
./ahb_test/ahb_incrx_test.svh
./ahb_test/ahb_wrapx_test.svh
./ahb_test/ahb_err_test.svh
./ahb_test/ahb_reset_test.svh

# 4. Top Module
./ahb_env/top.sv
```

---

## Makefile Komutları

```bash
# Compile
make compile

# Run specific test
make run_incrx
make run_wrapx
make run_err
make run_reset

# Clean
make clean

# View waveform
make wave

# Coverage report
make cov
```

---

## UVM Phases Timeline

```
┌────────────────────────────────────────────┐
│ create_objects_phase()                     │
│ (Resources allocated)                      │
└───────┬────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ build_phase()                              │
│ ├─ Components created                      │
│ └─ Configuration set                       │
└───────┬────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ connect_phase()                            │
│ ├─ Ports connected                         │
│ └─ References resolved                     │
└───────┬────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ end_of_elaboration_phase()                 │
│ └─ Hierarchy printouts, final checks       │
└───────┬────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ start_of_simulation_phase()                │
│ └─ Simulation environment initialized      │
└───────┬────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ run_phase()  ***** ACTIVE EXECUTION *****  │
│ ├─ Sequences start here                    │
│ ├─ Transactions generated                  │
│ └─ Run for specified time                  │
└───────┬────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ extract_phase()                            │
│ └─ Coverage data extracted                 │
└───────┬────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ check_phase()                              │
│ └─ Scoreboard/assertions checked           │
└───────┬────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ report_phase()                             │
│ └─ Final reports and statistics            │
└───────┬────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ final_phase()                              │
│ └─ Simulation complete                     │
└────────────────────────────────────────────┘
```

---

## Debugging Quick Tips

```systemverilog
// 1. Enable Full Verbosity
$ xsim top +UVM_VERBOSITY=UVM_FULL

// 2. Print Transaction
req.print();
xtn.print();

// 3. Print Hierarchy
env.print();

// 4. UVM Messages
`uvm_info(get_full_name(), "Message", UVM_MEDIUM)
`uvm_warning("TAG", "Warning message")
`uvm_error("TAG", "Error message")
`uvm_fatal("TAG", "Fatal error - simulation stops")

// 5. Transaction Logging
$display("@%0t: HADDR=%h", $time, vif.HADDR);

// 6. Clocking Block Observation
@(vif.mdrv_cb) $display("Clock edge");

// 7. Objection Management
phase.raise_objection(this);
#1000;
phase.drop_objection(this);

// 8. Check Configuration
if (!uvm_config_db#(type)::get(...)) 
    `uvm_fatal("CONFIG_ERR", "Config not found");
```

---

## Kısaltmalar (Abbreviations)

| Kısaltma | Anlamı |
|----------|--------|
| VIF | Virtual Interface |
| XTN | Transaction |
| CB | Clocking Block |
| NONSEQ | Non-Sequential Transfer |
| SEQ | Sequential Transfer |
| INCR | Increment Burst Mode |
| WRAP | Wrap Burst Mode |
| HREADY | Hardware Ready Signal |
| HRESP | Hardware Response Signal |
| HRDATA | Hardware Read Data |
| HWDATA | Hardware Write Data |

---

## Frequently Used Commands

```bash
# Compile with visibility
xvlog -sv +incdir+. -f compile.f -v

# Elaborate with debug
xelab -debug all -v top

# Simulate with GUI
xsim top -gui +UVM_VERBOSITY=UVM_MEDIUM

# Simulate headless
xsim top -R

# Run specific test with verbosity
xsim top -testname ahb_incrx_test +UVM_VERBOSITY=UVM_FULL

# Generate waveform
xsim top -g -R

# View coverage
xvhdl -cdslib cds.lib -worklib xsim work ahb_coverage.svh
```

Başarılar! 💪
