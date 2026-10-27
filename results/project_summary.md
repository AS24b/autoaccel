# AutoAccel Project Summary

Generated: 2026-10-27

## Project objective

Evaluate conventional and Karatsuba multiplier architectures using RTL simulation, synthesis-based generic logic-cell comparison, and formal verification.

## Synthesis comparison and recommendations

| Width | Conventional cells | Karatsuba cells | Recommended architecture | Cell-count reduction |
|---:|---:|---:|---|---:|
| 8 | 404 | 492 | Conventional | 17.89% |
| 16 | 1,903 | 1,685 | Karatsuba | 11.46% |
| 32 | 8,306 | 5,943 | Karatsuba | 28.45% |
| 64 | 34,837 | 21,581 | Karatsuba | 38.05% |

## Verification status

- Conventional simulation: 108 vectors each passed at N=8, N=16, and N=32 in the recorded audit run.
- Karatsuba simulation: 1,045 vectors each passed at N=8, N=16, and N=32 in the recorded audit run.
- Formal equivalence: N=8 passed with SymbiYosys and Bitwuzla.
- N=16 formal equivalence: unresolved; the full 32-bit output proof timed out. Bit 0 passed, but that does not prove the full output. No confirmed counterexample was established by the timeout runs.
- Selector unit tests: 4 tests passed in the recorded audit run.

## Interpretation and limitations

Recommendations minimize the generic logic-cell count reported by the current synthesis flow. These counts are not physical silicon area measurements and do not establish power consumption or timing.

The recommendations apply to the tested operand widths and current RTL and synthesis configuration. Further verification and technology-specific implementation are needed before making broader hardware performance claims.

The current repository does not include the openly licensed Jupyter notebook or open-source license required by the IEEE SSCS Code-a-Chip submission instructions.
