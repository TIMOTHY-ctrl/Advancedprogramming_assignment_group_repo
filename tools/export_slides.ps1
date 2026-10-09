$ErrorActionPreference = 'Stop'
$deckPath = Join-Path $PSScriptRoot '../presentation/coursework-slides.pptx'
$deckPath = (Resolve-Path -LiteralPath $deckPath).Path
$previewPath = Join-Path (Split-Path $deckPath) 'preview'
New-Item -ItemType Directory -Force -Path $previewPath | Out-Null
$pptApp = New-Object -ComObject PowerPoint.Application
try {
    $deck = $pptApp.Presentations.Open($deckPath, -1, 0, 0)
    if ($deck.Slides.Count -ne 15) { throw 'Expected exactly 15 slides.' }
    foreach ($slide in $deck.Slides) {
        foreach ($shape in $slide.Shapes) {
            if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
                $textBottom = $shape.TextFrame.TextRange.BoundTop + $shape.TextFrame.TextRange.BoundHeight
                if ($textBottom -gt $deck.PageSetup.SlideHeight) {
                    throw "Text extends beyond slide $($slide.SlideIndex): $($shape.Name)"
                }
            }
        }
        $imageName = 'slide-{0:00}.png' -f $slide.SlideIndex
        $slide.Export((Join-Path $previewPath $imageName), 'PNG', 1600, 900)
    }
    $deck.SaveAs((Join-Path (Split-Path $deckPath) 'coursework-slides.pdf'), 32)
    Write-Output 'PowerPoint validation passed: 15 slides; no text beyond slide boundaries; PDF and previews exported.'
    $deck.Close()
} finally {
    $pptApp.Quit()
}
