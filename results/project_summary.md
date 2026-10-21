# AutoAccel Project Summary

Generated: 2026-10-21

## Project objective

Evaluate conventional and Karatsuba multiplier architectures using RTL simulation, synthesis-based generic logic-cell comparison, and formal verification.

## Synthesis comparison and recommendations

| Width | Conventional cells | Karatsuba cells | Recommended architecture | Cell-count reduction |
|---:|---:|---:|---|---:|
| 8 | 404 | 516 | Conventional | 21.71% |
| 16 | 1,903 | 1,733 | Karatsuba | 8.93% |
| 32 | 8,306 | 6,064 | Karatsuba | 26.99% |
| 64 | 34,837 | 21,821 | Karatsuba | 37.36% |

## Verification status

- RTL simulations: previously reported as passing at tested configurations.
- Formal equivalence: 8-bit proof passed.
- 16-bit formal equivalence: unresolved; direct SAT proof did not complete.
- Selector unit tests: 4 tests passed in the latest reported run.

## Interpretation and limitations

Recommendations minimize the generic logic-cell count reported by the current synthesis flow. These counts are not physical silicon area measurements and do not establish power consumption or timing.

The recommendations apply to the tested operand widths and current RTL and synthesis configuration. Further verification and technology-specific implementation are needed before making broader hardware performance claims.
