# CV – Daniele Trisotto

Un'unica fonte (`cv.yaml`) da cui si generano il PDF in LaTeX e il sito web, in italiano e in inglese.

Sito: <https://dantrisi.github.io/CV/> (italiano) · <https://dantrisi.github.io/CV/en/> (inglese)

| File | A cosa serve |
|---|---|
| `cv.yaml` | **Contenuti** (testi IT/EN). Si modifica solo questo per aggiornare il CV. |
| `foto.jpg` | Ritratto (meglio quadrato, viso centrato). Se manca, il CV esce senza foto. |
| `private.yaml` | Dati solo per il PDF locale (telefono). **Non** va su GitHub; vedi `private.example.yaml`. |
| `templates/cv.tex.j2` | Impaginazione e colori del PDF (LaTeX). |
| `templates/index.html.j2` | Aspetto e colori della pagina web. |
| `build.py` | Genera tutto. |
| `pdf/` | PDF generati in locale, con il telefono: da stampare o inviare. Non versionati. |
| `site/` | Sito generato (non versionato: lo ricrea GitHub a ogni push). |

## Generare in locale

```
uv run build.py            # PDF + sito (serve pdflatex con babel-italian e tikz)
uv run build.py --no-pdf   # solo sito
```

## Pubblicazione

A ogni push su `main` la Action `.github/workflows/deploy.yml` ricompila i PDF (senza telefono,
perché `private.yaml` non è nel repository) e pubblica il sito su GitHub Pages.
Impostazione necessaria una sola volta: *Settings → Pages → Source: GitHub Actions*.
