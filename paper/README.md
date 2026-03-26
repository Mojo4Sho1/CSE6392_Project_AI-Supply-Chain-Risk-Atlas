# Final Report Draft

This directory contains a simple, single-file LaTeX draft for the final project report.

## Files

- `final_report.tex` - repo-local draft intended to stay easy to move into Overleaf later

## Local workflow

If a TeX toolchain is installed locally, a typical build command is:

```bash
cd paper
pdflatex final_report.tex
```

You can also use `latexmk -pdf final_report.tex` if you prefer `latexmk`.

## Overleaf workflow

When you move this draft into Overleaf:

1. Upload `final_report.tex`
2. Upload any figure files you want to keep from `../figures/`
3. Update image paths if you flatten the directory structure in Overleaf

## Notes

- The current draft references `../figures/reused_vulnerable_packages.png`
- A local TeX toolchain is not installed in the current repo environment, so this draft was scaffolded but not compiled here
