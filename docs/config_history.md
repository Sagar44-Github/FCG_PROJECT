# Initial parameter record

The first implementation uses the four shelf-label colours, three lighting scenarios, and scenario definitions supplied in the master development instruction. `config.json` is the sole configuration source used by the research pipeline.

| Date (Asia/Colombo) | Change | Reason |
|---|---|---|
| 2026-11-15 | Initial values recorded: G `#2E9E4F`, Y `#F5B700`, O `#F07C1E`, R `#D62828`; L1 CIE D65; L2 and L3 LED approximations targeting 4000 K and 3000 K. | User-specified fixed starting parameters. |
| 2026-11-15 | Added explicit virtual-print, observer, donation and sustainability assumptions. | The prompt requires reproducible simulations where physical data or Nigam parameters are unavailable. Values are labeled model assumptions, not measurements or Nigam's formula. |

No original colour or illuminant parameter has been changed. Subsequent changes must be added to this table with date and reason.
# 2026-11-15 — application integration assumptions

- Added low-impact (1.5), central (2.5), and high-impact (3.5) emissions-factor scenarios in kg CO2e/kg to support transparent sustainability sensitivity displays. The low/high values are illustrative ±40% sensitivity bounds around the pre-existing central assumption, not measured factors or published product footprints. The original 2.5 central value is unchanged.
- The API now accepts optional observer parameters on each donation-simulation request. The original configuration remains the default; each request and result stores the effective parameter values and a hash of the research configuration.

