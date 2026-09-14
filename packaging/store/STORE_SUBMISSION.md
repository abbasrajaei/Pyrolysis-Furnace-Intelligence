# Microsoft Store submission

## Product

**Pyrolysis Furnace Intelligence**

Store product type: **MSIX or PWA app**

## Partner Center identity

The following values are assigned by Microsoft Partner Center and must match the MSIX manifest exactly.

- Package/Identity/Name: `AbbasRajaei.PyrolysisFurnaceIntelligence`
- Package/Identity/Publisher: `CN=50B235C4-1F76-43FD-A99B-D784B782FF08`
- Package/Properties/PublisherDisplayName: `Abbas Rajaei`
- Store ID: `9NB6K57T831H`

The Store package uses the public desktop application produced by the same PyInstaller build as the normal Windows installer.

## Distribution model

The GitHub Windows workflow creates two separate Windows deliverables:

1. **EXE installer** — direct GitHub distribution.
2. **MSIX Store package** — intended for upload to Microsoft Partner Center.

The Store submission package is a full-trust packaged desktop application because the existing engineering workbench runs a local Flask/Dash server and embeds it in a desktop window.

The package declares only the `runFullTrust` restricted capability. It does not request camera, microphone, location, documents, pictures or external plant-control capabilities.

## Signing

The CI workflow applies a temporary self-signed certificate whose subject matches the Partner Center Publisher identity so the package can be installed and smoke-tested inside the Windows runner.

That certificate is **not** the public trust mechanism.

For Microsoft Store distribution, Partner Center re-signs accepted MSIX packages with a Microsoft certificate. The Store package therefore does not require a purchased CA-trusted code-signing certificate.

## Upload

In Partner Center:

1. Open **Pyrolysis Furnace Intelligence**.
2. Click **Start submission**.
3. Complete pricing/availability, properties and age ratings.
4. On **Packages**, upload:
   `Pyrolysis-Furnace-Intelligence-Store-v2.3.0.msix`
5. Complete the Store listing and certification notes.
6. Submit for certification.

Do not distribute the CI self-signed MSIX to end users for sideloading. End users should install the Microsoft-signed package from the Store after certification.
