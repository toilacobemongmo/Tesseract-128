# Manuscript and submission bundle

Everything needed to reproduce the Tesseract-128 manuscript lives in this
directory. The paper is **not** maintained on Overleaf; this directory is the
single source of truth.

## Layout

```
paper/
  manuscript.tex                  authoritative manuscript source
  create_paper.py                 assembles build/manuscript_submission.tex
  generate_figures.py             regenerates the five figures from results
  build_paper.ps1                 one-shot build script
  audit_submission.py             checks the bundle (emails, highlights, pages)
  figures/                        fig_*.png used by \includegraphics
  build/                          generated .tex/.pdf/.log (gitignored)
  submission/                     upload-ready bundle
```

## Build

```powershell
powershell -ExecutionPolicy Bypass -File paper/build_paper.ps1
```

Or step by step:

```powershell
python paper/create_paper.py                 # manuscript.tex -> build/*.tex
cd paper/build
pdflatex -interaction=nonstopmode manuscript_submission.tex   # run twice
cd ../..
python paper/audit_submission.py             # verify the bundle
```

Expected result: **70 pages, 0 LaTeX errors, 0 undefined references**, and
`audit_submission.py` reports `Highlights ... PASSED`, `File presence: ALL
PRESENT`, target email present / old email absent everywhere.

Pass `-SkipFigures` to reuse the checked-in PNGs instead of regenerating them
(the figure script needs `matplotlib` and the JSON/`txt` outputs under
`reports/` and `cryptanalysis/`).

## Why `create_paper.py` exists

`manuscript.tex` is written as a standalone article with `\section{...}`
headings. `create_paper.py` extracts those sections and re-wraps them in the
Elsevier `elsarticle` front matter (title, authors, abstract, highlights).

Two failure modes are guarded, both of which produced a corrupt PDF in an
earlier revision of this repository:

1. **Missing section anchor.** Section lookups used `str.find()` without
   checking for `-1`. A renamed heading made `find()` return `-1`, and the slice
   `src[-1:N]` silently returned nearly the whole document, so the assembled
   file contained the paper twice (two bibliographies, two `\end{document}`)
   and expanded from 70 to 81 pages. Anchors are now resolved through
   `_anchor()`, which aborts with a clear error instead.
2. **Overlapping slices.** The assembled document is asserted to contain
   exactly one `\begin{thebibliography}`, one `\end{document}`, and no empty
   section.

Do **not** run `sync_jisa_to_article.py` from the working directory: it
overwrites `manuscript.tex` with the flattened output, destroying the section
anchors that `create_paper.py` depends on. Keeping the source here, in version
control, is what makes that round-trip unnecessary.

## Submission bundle (`submission/`)

| File | Purpose |
|---|---|
| `manuscript_submission.pdf` | compiled manuscript (70 pages) |
| `manuscript_submission.tex` | LaTeX source for the above |
| `Cover_Letter.docx` / `.txt` | cover letter |
| `Highlights.txt` | Elsevier highlights (max 85 chars each) |
| `CRediT_Author_Statement.txt` | author contribution statement |
| `Declaration_of_Competing_Interests.txt` | competing-interests declaration |
| `fig_*.png` | figures, in case the venue asks for them separately |
| `Lena_cryptanalysis_result.png`, `Baboon_cryptanalysis_result.png` | case-study images |
| `trail_weight_experiment_log.txt` | differential trail-weight log |
| `tesseract128_text_only.txt` | plain-text extraction of the manuscript |
| `README_SUBMISSION_GUIDE.txt` | venue checklist |

## Reproducing the numbers in the paper

All empirical claims trace back to artifacts in `../reports/` and
`../cryptanalysis/`. See `../reports/benchmark_provenance_audit.txt` for the
claim-by-claim mapping between statements in the manuscript and the files that
back them.
