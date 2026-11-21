# Microsoft Store distribution

## Product

**Pyrolysis Furnace Intelligence**

Microsoft Store ID: `9NB6K57T831H`

Public Store page:

https://apps.microsoft.com/detail/9NB6K57T831H?hl=en-us&gl=GB

## Partner Center identity

These values are assigned by Microsoft Partner Center and must match the MSIX manifest exactly.

- Package/Identity/Name: `AbbasRajaei.PyrolysisFurnaceIntelligence`
- Package/Identity/Publisher: `CN=50B235C4-1F76-43FD-A99B-D784B782FF08`
- Package/Properties/PublisherDisplayName: `Abbas Rajaei`

The Store package uses the same public desktop application produced by the Windows build workflow.

## Distribution model

The Windows workflow produces two deliverables:

1. **Microsoft Store MSIX** for Store distribution.
2. **EXE installer** for direct GitHub distribution.

The Store package is a full-trust packaged desktop application because the workbench runs its local Dash/Flask service and desktop executable on the user's machine. The package declares `runFullTrust` for that desktop architecture. It does not request camera, microphone, location, documents, pictures or external plant-control capabilities.

## Signing

The CI workflow uses a temporary self-signed certificate only for build validation. It is not the public trust mechanism.

The Microsoft Store version is distributed through the Store after certification and is the recommended installation route for Windows users. The direct GitHub EXE remains unsigned and can trigger Windows SmartScreen warnings.
