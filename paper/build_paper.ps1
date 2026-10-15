# Build the submission manuscript from paper/manuscript.tex.
#
#   powershell -ExecutionPolicy Bypass -File paper/build_paper.ps1
#
# Steps:
#   1. regenerate the five figures from cryptanalysis outputs (optional, -SkipFigures)
#   2. assemble paper/build/manuscript_submission.tex from paper/manuscript.tex
#   3. run pdflatex twice so cross-references and the bibliography settle
#   4. copy the .tex and .pdf into paper/submission/ for upload
#   5. audit the bundle (emails, highlights, page count)
param([switch]$SkipFigures)

$ErrorActionPreference = 'Stop'
$PaperDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $SkipFigures) {
    Write-Host '[1/5] Regenerating figures ...'
    python (Join-Path $PaperDir 'generate_figures.py')
} else {
    Write-Host '[1/5] Skipping figure regeneration (-SkipFigures)'
}

Write-Host '[2/5] Assembling manuscript ...'
python (Join-Path $PaperDir 'create_paper.py')

$BuildDir = Join-Path $PaperDir 'build'
Write-Host '[3/5] Running pdflatex (twice) ...'
Push-Location $BuildDir
try {
    pdflatex -interaction=nonstopmode manuscript_submission.tex | Out-Null
    pdflatex -interaction=nonstopmode manuscript_submission.tex | Out-Null
    $pages = (Select-String -Path manuscript_submission.log -Pattern 'Output written.*\((\d+) pages').Matches.Groups[1].Value
    $undef = (Select-String -Path manuscript_submission.log -Pattern 'undefined' -CaseSensitive:$false).Count
    Write-Host ("      PDF: {0} pages, {1} undefined reference(s)" -f $pages, $undef)
    if ($undef -gt 0) { Write-Warning 'Undefined references remain - inspect manuscript_submission.log' }
} finally {
    Pop-Location
}

Write-Host '[4/5] Copying artifacts to paper/submission ...'
$SubDir = Join-Path $PaperDir 'submission'
Copy-Item (Join-Path $BuildDir 'manuscript_submission.pdf') $SubDir -Force
Copy-Item (Join-Path $BuildDir 'manuscript_submission.tex') $SubDir -Force

Write-Host '[5/5] Auditing submission bundle ...'
python (Join-Path $PaperDir 'audit_submission.py')

Write-Host 'Done.'
