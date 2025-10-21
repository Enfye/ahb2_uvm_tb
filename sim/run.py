#!/usr/bin/env python3
import argparse
import os
from os import system, path

# ----------------------------------------
# Command-line options
# ----------------------------------------
parser = argparse.ArgumentParser(
    description="XSIM runner (Perl run.pl equivalent)"
)

parser.add_argument("--clean", action="store_true", help="Clean build/sim artifacts and exit")
parser.add_argument("--compile", action="store_true", help="Compile/elaborate only (no simulation)")
parser.add_argument("--batch", action="store_true", help="Force batch (non-GUI) run")
parser.add_argument("--gui", action="store_true", help="Open GUI for a single test")

parser.add_argument("--test", type=str, default="ahb_crt_test", help="Test name to run (like +UVM_TESTNAME)")
parser.add_argument("--regress", action="store_true", help="Run all tests from testcases.txt (one per line)")

parser.add_argument("--verbosity", type=str, default="UVM_LOW", help="UVM verbosity level")
parser.add_argument("--seed", type=str, default="16422201", help="SV random seed")
parser.add_argument("--coverage", action="store_true", help="(XSIM) Enable debug/coverage-friendly build")

args = parser.parse_args()

# ----------------------------------------
# Variable Definitions
# ----------------------------------------
def init_variables():
    global XVLOG_OPT, XELAB_OPT, TOP, INC_FILE

    TOP = "top"              # top module name
    INC_FILE = "ahb_inc.f"   # filelist (same as Perl script)

    XVLOG_OPT = f"-sv -f {INC_FILE} -L uvm"

    # Notes:
    #  -relax and -timescale to match your original
    #  -debug typical helps keep waves/coverage-friendly info (similar in spirit to vsim -assertdebug/-sva)
    XELAB_OPT = "-relax -s {top} -timescale 1ns/1ps -L uvm".format(top=TOP)
    if args.coverage:
        # In XSIM, adding debug helps retain hierarchy & signals for coverage/waves
        XELAB_OPT += " -debug typical"


# ----------------------------------------
# Helpers
# ----------------------------------------
def sh(cmd: str):
    print(f"\n$ {cmd}")
    return system(cmd)

def log_and_wdb_names(testname: str):
    log = f"{testname}_sim.log"
    wdb = f"{testname}.wdb"
    return log, wdb


# ----------------------------------------
# Compile / Elaborate
# ----------------------------------------
def compile_files():
    cmd = f"xvlog {XVLOG_OPT}"
    return sh(cmd)

def elaborate():
    # work.<top> is the default library.work.top in xelab; with xvlog default lib is 'work'
    cmd = f"xelab {XELAB_OPT} work.{TOP}"
    return sh(cmd)


# ----------------------------------------
# Simulate (single test)
# ----------------------------------------
def simulate_one(testname: str, use_gui: bool):
    log, wdb = log_and_wdb_names(testname)

    # Base xsim command composed to mimic Perl vsim options:
    # -testplusarg UVM_TESTNAME
    # -testplusarg UVM_VERBOSITY
    # Use -sv_seed to mirror ModelSim's -sv_seed
    # -log <file> for per-test logging
    cmd = (
        f"xsim {TOP} "
        f"-sv_seed {args.seed} "
        f"-testplusarg UVM_OBJECTION_TRACE "
        f"-testplusarg UVM_TESTNAME={testname} "
        f"-testplusarg UVM_VERBOSITY={args.verbosity} "
        f"-wdb {wdb} "
        f"-log {log}"
    )

    # Batch vs GUI
    if use_gui:
        # GUI mode: let user drive run, or auto-run then open waves; choose the simpler: launch GUI with a short TCL
        # If you want auto-run to completion in GUI, you can provide a tclbatch that does 'run -all'.
        cmd += " -gui"
    else:
        cmd += " -runall"

    return sh(cmd)


# ----------------------------------------
# Regress: read testcases.txt and run all
# ----------------------------------------
def run_regress():
    tcf = "testcases.txt"
    if not path.exists(tcf):
        print("ERROR: testcases.txt missing!")
        return 1

    status = 0
    with open(tcf, "r") as fr:
        for line in fr:
            test = line.strip()
            if not test or test.startswith("#"):
                continue
            print(f"\n=== Running test: {test} ===")
            rc = simulate_one(test, use_gui=False)
            status |= (rc != 0)

    # If desired, this is where you'd post-process coverage reports for XSIM.
    # (ModelSim used `vcover report -html`. For Vivado/XSIM, coverage reporting differs
    #  and typically involves Vivado GUI or xsim stats/wave databases.)
    return 0 if status == 0 else 1


# ----------------------------------------
# Clean
# ----------------------------------------
def clean():
    # Vivado/XSIM usual suspects
    patterns = [
        "xsim.dir", ".Xil", "xsim.log", "xsim.pb", "*.pb", "*.wdb",
        "webtalk*", "*.jou", "*.str", "*.log", "xelab.*", "xvlog.*",
        "*.backup.jou", "*.backup.log",
    ]
    for p in patterns:
        sh(f"rm -rf {p}")
    return 0


# ----------------------------------------
# Main
# ----------------------------------------
def main():
    init_variables()

    if args.clean:
        return clean()

    # Build
    rc = compile_files()
    if rc != 0:
        return rc
    rc = elaborate()
    if rc != 0:
        return rc

    # If --compile only, stop here
    if args.compile:
        return 0

    # Regress or single test
    if args.regress:
        return run_regress()
    else:
        # --gui takes precedence; otherwise batch (default), or forced by --batch
        use_gui = bool(args.gui and not args.batch)
        return simulate_one(args.test, use_gui=use_gui)


if __name__ == "__main__":
    raise SystemExit(main())
