# AutoAccel

Automated Design-Space Exploration and Multi-Objective Optimization of Energy-Efficient Arithmetic Accelerators.

AutoAccel compares conventional and Karatsuba unsigned multipliers using parameterized SystemVerilog, simulation, formal equivalence, and Yosys synthesis statistics. The current experiment focuses on integer multiplication. It reports generic logic-cell counts; it does not report physical area, power, or signoff timing.

## Architectures and widths

- `conventional_multiplier` is a shift-and-add partial-product implementation in `rtl/multiplier/conventional_multiplier.sv`.
- `karatsuba_multiplier` uses Karatsuba's three-product split identity in `rtl/multiplier/PARAMETERIZED_MULTIPLIER.sv`.
- Both modules use parameter `N`, unsigned `N`-bit operands `A` and `B`, and a full unsigned `2*N`-bit product `P`.
- The Karatsuba implementation requires an even `N >= 2`. The checked-in synthesis data covers `N=8,16,32,64`; the Karatsuba simulation testbench covers `N=8,16,32`.

## Repository layout

| Path | Purpose |
|---|---|
| `rtl/multiplier/` | Conventional and Karatsuba RTL and a comparison wrapper |
| `tb/` | Self-checking simulation testbenches |
| `formal/` | Equivalence harnesses, configurations, logs, and retained work products |
| `scripts/` | Synthesis, comparison, plotting, selection, and summary scripts |
| `results/baseline.csv` | Generic cell counts and the width-specific Yosys log for each measurement |
| `results/comparison.csv` | Conventional-versus-Karatsuba comparison derived from the baseline |
| `results/architecture_recommendations.csv` | Lower-cell-count choice and reduction relative to the other architecture |
| `results/plots/` | Generated comparison plots |
| `results/*_yosys.log` | Yosys synthesis transcripts |

## Prerequisites

The flow was checked with Python 3.12, OSS CAD Suite Yosys 0.70+190, Icarus Verilog 14.0 development build, SymbiYosys v0.70-9-g79fc9ed, and Bitwuzla 0.9.1. Plot generation requires Matplotlib. Use a PowerShell 7 session and configure the installed OSS CAD Suite for that session:

```powershell
$suite = 'C:\path\to\oss-cad-suite' # Replace with your OSS CAD Suite installation directory
$env:PATH = "$suite\bin;$suite\lib;$env:PATH"
python --version
yosys -V
iverilog -V
```

The PATH change above applies to the current PowerShell process only. Install Python dependencies separately if they are missing; the repository currently has no requirements or environment lock file.

## Simulation

Run the conventional testbench at its default `N=8`:

```powershell
New-Item -ItemType Directory -Force "$env:TEMP\autoaccel-sim" | Out-Null
iverilog -g2012 -s tb_conventional_multiplier -o "$env:TEMP\autoaccel-sim\conventional.vvp" rtl/multiplier/conventional_multiplier.sv tb/tb_conventional_multiplier.sv
Push-Location "$env:TEMP\autoaccel-sim"
vvp .\conventional.vvp
Pop-Location
```

The conventional bench checks 8 directed vectors and 100 pseudorandom vectors (108 total). It prints `STATUS: PASS` or `STATUS: FAIL`; it does not call `$fatal` on a mismatch, so inspect that status line rather than relying only on the simulator exit code. The random seed is not fixed by the bench. To test `N=16`, use this compile command (then run it from the temporary directory as above):

```powershell
iverilog "-Ptb_conventional_multiplier.N=16" -g2012 -s tb_conventional_multiplier -o "$env:TEMP\autoaccel-sim\conventional_N16.vvp" rtl/multiplier/conventional_multiplier.sv tb/tb_conventional_multiplier.sv
```

Run the Karatsuba bench, which instantiates separate `N=8`, `N=16`, and `N=32` configurations:

```powershell
iverilog -g2012 -s karatsuba_multiplier_tb_top -o "$env:TEMP\autoaccel-sim\karatsuba.vvp" rtl/multiplier/PARAMETERIZED_MULTIPLIER.sv tb/tb_PARAMETERIZED_KARATSUBA.sv
Push-Location "$env:TEMP\autoaccel-sim"
vvp .\karatsuba.vvp
Pop-Location
```

Each Karatsuba configuration checks 25 corner pairs, 4 directed vectors, 16 pattern pairs, and 1,000 pseudorandom vectors (1,045 total). The bench calls `$fatal` if a mismatch occurs. These are finite simulation checks against `A * B`; they are not formal proofs. The current wrapper launches all three configurations together.

For a standalone run with an unambiguous per-width result, select one parameterized bench instance. For example, for `N=16`:

```powershell
iverilog "-Pkaratsuba_multiplier_tb.N=16" -g2012 -s karatsuba_multiplier_tb -o "$env:TEMP\autoaccel-sim\karatsuba_N16.vvp" rtl/multiplier/PARAMETERIZED_MULTIPLIER.sv tb/tb_PARAMETERIZED_KARATSUBA.sv
Push-Location "$env:TEMP\autoaccel-sim"
vvp .\karatsuba_N16.vvp
Pop-Location
```

## Synthesis and results

Run the complete data flow from the repository root:

```powershell
python scripts/run_autoaccel.py
```

This workflow synthesizes both architectures at `N=8,16,32,64`, compares the results, regenerates plots, writes architecture recommendations, runs the selector unit tests, and regenerates `results/project_summary.md`. **It overwrites the corresponding CSV files, width-specific synthesis logs, plots, and summary.** Preserve or copy those artifacts before rerunning if you need to retain a prior result set.

The synthesis script uses the installed `yosys` executable and runs `read_verilog -sv`, `hierarchy -top ... -chparam N ...`, `proc; opt; techmap; opt; stat`. The reported quantity is the final generic Yosys cell count after this flow. It is a unitless count, not an area in square micrometers or a physical timing or power measurement. Comparisons use:

```text
Karatsuba reduction (%) = 100 * (conventional_cells - karatsuba_cells) / conventional_cells
```

Positive values indicate fewer generic cells for Karatsuba; negative values indicate more. The recommendation script selects the lower-count architecture and reports the magnitude of its reduction relative to the higher-count architecture. `results/baseline.csv` points to the active width-specific logs, named `*_N<width>_yosys.log`. Older unqualified logs such as `results/karatsuba_yosys.log` are retained historical artifacts and are not the source for the current CSV.

To run individual stages instead of the full workflow:

```powershell
python scripts/run_synthesis.py
python scripts/compare_results.py
python scripts/plot_results.py
python scripts/select_architecture.py
python -m unittest discover -s scripts -p 'test_select_architecture.py' -v
python scripts/generate_summary.py
```

## Formal equivalence

The retained N=8 SymbiYosys configuration compares the actual conventional and Karatsuba modules at `N=8`, with the same unconstrained operands and an assertion over the full 16-bit product. The recorded run used Bitwuzla and completed `PASS` (`rc=0`; 12 seconds) in `formal/logs/N8_sby_console_run2.log`; its status record is `formal/logs/N8_sby_status_run2.txt`.

To repeat with a fresh work directory and retain a console transcript:

```powershell
Push-Location formal
$tag = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$run = "work\SBY_N8_$tag"
$log = "logs\N8_$tag.log"
& sby.exe -d $run multiplier_N8_sby.sby 2>&1 | Tee-Object -FilePath $log
$proofExit = $LASTEXITCODE
"COMMAND: sby.exe -d $run multiplier_N8_sby.sby`r`nEXIT_CODE: $proofExit" | Add-Content $log
Pop-Location
if ($proofExit -ne 0) { throw "N=8 formal run failed with exit code $proofExit" }
```

The expected successful result is `DONE (PASS, rc=0)` in the console output and a `PASS` status in the SBY work directory. `FAIL` or a counterexample is not a proof; timeout, interrupted execution, or `UNKNOWN` remains unresolved.

**Current formal status:** N=8 is proven equivalent. N=16 is unresolved: the full-output proof and selected per-bit attempts timed out; bit 0 passed, which does not establish equality of the full 32-bit output. No confirmed counterexample is present in the recorded timeout runs. No claim of N=16 equivalence is made.

## Current synthesis results

| Operand width | Conventional cells | Karatsuba cells | Karatsuba reduction | Lower count |
|---:|---:|---:|---:|---|
| 8 | 404 | 492 | -21.78% | Conventional |
| 16 | 1,903 | 1,685 | 11.46% | Karatsuba |
| 32 | 8,306 | 5,943 | 28.45% | Karatsuba |
| 64 | 34,837 | 21,581 | 38.05% | Karatsuba |

These values describe the saved Yosys generic-cell reports and depend on the RTL, Yosys version, and synthesis script. They do not establish physical PPA or generalize beyond the measured configurations.

## Limitations and next work

- Finish a scalable full-output N=16 formal proof; retain timeout and failure as distinct outcomes.
- Add a deterministic random seed and machine-readable failure status to the conventional simulation bench.
- The Karatsuba bench currently exercises only the Karatsuba implementation, not both architectures under one simulator test.
- Add a pinned Python dependency/environment file and provide cross-platform tool setup instructions.
- The repository currently has no Jupyter notebook or open-source license file. These are required Code-a-Chip submission artifacts and need to be prepared before submission.
- Physical implementation, area, power, and timing are not measured by the current flow.

## Project team

Two-person undergraduate ECE/VLSI team.
