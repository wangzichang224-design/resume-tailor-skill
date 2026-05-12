# Build PDF from Markdown resume using Pandoc + Chromium/Edge
# Usage: .\build_pdf.ps1 <input.md> [output.pdf]

param(
    [string]$Input = "draft_resume.md",
    [string]$Output = "resume.pdf"
)

if (-not (Test-Path $Input)) {
    Write-Error "Input file '$Input' not found"
    exit 1
}

# Check available renderers
$hasPandoc = Get-Command pandoc -ErrorAction SilentlyContinue
$hasChrome = Get-Command "google-chrome" -ErrorAction SilentlyContinue
$hasEdge = Get-Command msedge -ErrorAction SilentlyContinue -ErrorVariable ev
$hasChromium = Get-Command chromium -ErrorAction SilentlyContinue

$browser = $null
if ($hasChrome) { $browser = "google-chrome" }
elseif ($hasChromium) { $browser = "chromium" }
elseif ($hasEdge) { $browser = "msedge" }

if ($browser -and $hasPandoc) {
    $htmlFile = [System.IO.Path]::ChangeExtension($Output, ".html")
    pandoc $Input -o $htmlFile --self-contained
    & $browser --headless --disable-gpu --print-to-pdf="$Output" "$htmlFile"
    Remove-Item $htmlFile
    Write-Host "PDF generated: $Output"
}
elseif ($hasPandoc) {
    pandoc $Input -o $Output --pdf-engine=weasyprint
    Write-Host "PDF generated: $Output"
}
else {
    Write-Error "No PDF renderer found. Install Chrome/Edge or Pandoc+weasyprint."
    exit 1
}
