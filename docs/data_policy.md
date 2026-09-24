# Public data policy

Public operating conditions and fuel compositions are independently selected synthetic teaching inputs. They are not rounded exports of an operating case. Only general chemical formulas, mathematical constants, rounded property references and explicitly illustrative architecture are used exactly.

The public YAML contains value, units, case, public provenance, engineering basis and notes. It has no original equipment identifiers or document traceability. Calculations preserve assumption and synthetic dependency categories. Missing physical relationships remain unavailable.

`data/` is the readable dataset. Identical YAML resources under the Python package make a regular wheel installation self-contained. Tests verify that the two copies agree. Edits must update both copies; installing a new package version is required to change installed resources.

Rounded species properties are suitable for teaching arithmetic only. Declared stored compositions are complete and do not represent a real gas supply. In the interactive workbench, changing one selected component proportionally renormalizes the remaining unlocked components before the validated composition is sent to the engineering engine. Normal-volume properties use the explicit ideal normal state stated in the methods. The synthetic thermal allocation is fixed and compatible; no private design envelope is exposed.
