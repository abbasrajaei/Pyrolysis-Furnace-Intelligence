param(
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

function New-PfiTile {
    param(
        [int]$Size,
        [string]$Path
    )

    $bitmap = New-Object System.Drawing.Bitmap($Size, $Size)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $graphics.Clear([System.Drawing.Color]::FromArgb(7, 18, 29))

    $margin = [Math]::Max(2, [int]($Size * 0.10))
    $accent = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(54, 167, 233))
    $graphics.FillRectangle($accent, $margin, $margin, $Size - 2 * $margin, $Size - 2 * $margin)

    $fontSize = [Math]::Max(8, [single]($Size * 0.28))
    $font = New-Object System.Drawing.Font("Segoe UI", $fontSize, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
    $textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center

    $rect = New-Object System.Drawing.RectangleF(0, 0, $Size, $Size)
    $graphics.DrawString("PFI", $font, $textBrush, $rect, $format)

    $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)

    $format.Dispose()
    $textBrush.Dispose()
    $font.Dispose()
    $accent.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
}

New-PfiTile -Size 50 -Path (Join-Path $OutputDirectory "StoreLogo.png")
New-PfiTile -Size 150 -Path (Join-Path $OutputDirectory "Square150x150Logo.png")
New-PfiTile -Size 44 -Path (Join-Path $OutputDirectory "Square44x44Logo.png")
