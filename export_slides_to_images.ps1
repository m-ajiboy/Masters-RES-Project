param(
    [Parameter(Mandatory=$true)][string]$PptxPath,
    [Parameter(Mandatory=$true)][string]$OutDir
)

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }

$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open($PptxPath, [Type]::Missing, [Type]::Missing, [Microsoft.Office.Core.MsoTriState]::msoFalse)

$count = $pres.Slides.Count
Write-Output "Total slides: $count"

for ($i = 1; $i -le $count; $i++) {
    $slide = $pres.Slides.Item($i)
    $outPath = Join-Path $OutDir ("slide_{0:D2}.png" -f $i)
    $slide.Export($outPath, "PNG", 1280, 720)
}

$pres.Close()
$ppt.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
Write-Output "Exported $count slides to $OutDir"
