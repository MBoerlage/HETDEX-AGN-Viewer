# HAS DATA SIG — HETDEX AGN Viewer

An interactive local browser tool for exploring the HETDEX AGN spectral catalog across multiple data releases, built for the HAS Data Special Interest Group.

Features:
- Browse and filter all AGN by magnitude, redshift, RA, and Dec
- Click any object to fetch and display its spectrum (flux + 1σ error band)
- RA / Dec sky map coloured by survey field
- Magnitude vs. redshift diagram
- Cross-match with the NGC/IC catalog
- Supports multiple HETDEX data releases simultaneously (HDR3 and HDR4)

---

## ⚠️ Data files required

**The FITS data files are not included in this repository.** They must be downloaded separately from the HETDEX public data release page:

> **https://hetdex.org/data-results/#pdr1**

Place the downloaded files in the same folder as `server.py`:

| File | Release | Objects |
|------|---------|---------|
| `hetdex_agn.fits` | HDR3 | 5,322 AGN |
| `hetdex_agn_hdr4.fits` | HDR4 | 15,940 AGN |

The tool works with whichever files are present. If both are available, a release selector appears in the viewer header.

---

## Quick start

```
install.bat   ← run once on a new machine
launch.bat    ← run every time you want to open the viewer
```

The viewer opens at **http://localhost:5000** in your default browser.  
Keep the server window open while using the tool; close it (or press Ctrl+C) to stop.

---

## Installation

### With Python 3.9+ already installed

```
install.bat
```

This installs the required packages and optionally downloads the NGC/IC catalog for cross-matching.

### Without Python

`install.bat` will try to install Python 3.12 via **winget** (available on Windows 10 1903+ and Windows 11). After installation you will be prompted to re-run `install.bat` once so PATH changes take effect.

If winget is unavailable, install Python manually:

1. Go to <https://www.python.org/downloads/>
2. Download Python 3.12 or newer
3. Run the installer — **check "Add Python to PATH"**
4. Re-run `install.bat`

### Required Python packages

```
pip install numpy astropy astroquery flask
```

---

## The three tabs

### Tab 1 — All Spectra

Filter the full AGN catalog and view individual spectra on click.

**Recommended filter order:**

| Filter | Purpose |
|--------|---------|
| **Magnitude ≤** | Brightness cut — removes faint/uncertain objects. Start at ≤ 22 and tighten as needed. Tick *incl. no-phot.* to include objects with no matched photometry. |
| **z range** | Redshift slice — targets a specific cosmic epoch or emission line (Lyα z ≈ 1.9–3.5, C IV z ≈ 1.2–2.6, Mg II z ≈ 0.2–1.0). |
| **RA range** | Selects a right ascension strip. HETDEX has two main survey areas: *dex-spring* (RA ≈ 150–240°) and *dex-fall* (RA ≈ 0–40°, 310–360°). |
| **Dec range** | Combined with RA to isolate a specific survey field. |

The list is sorted brightest-first (up to 200 shown). Search by AGN ID or field name using the text box.

Each spectrum shows flux (blue line) with a 1σ shaded error band over the HETDEX bandpass (3470–5540 Å).

### Tab 2 — Sky Map

RA vs Dec scatter of all AGN, coloured by survey field. RA axis is reversed (East left, standard astronomical convention). NGC/IC cross-matched objects appear as gold stars.

| Colour | Field |
|--------|-------|
| Orange | COSMOS |
| Blue | DEX-Fall |
| Green | DEX-Spring |
| Red-orange | EGS |
| Purple | GOODS-N |
| Peach | NEP |
| Teal | SSA22 (HDR4) |

### Tab 3 — Mag vs z

Magnitude vs redshift for all AGN with photometry. Y-axis is inverted (brighter objects at top).

---

## NGC cross-matching

Run once after downloading a FITS file to match HETDEX AGN against the NGC/IC catalog (requires internet):

```
python match_ngc.py
```

Results are saved to `ngc_matched.json`. The search radius (default 60 arcsec) is configurable at the top of `match_ngc.py`. Restart the server after regenerating.

---

## Adding a future data release

Edit the `DATASET_CONFIG` dictionary at the top of `server.py` — add a new entry following the same pattern as `hdr3` and `hdr4`. The header selector appears automatically when multiple FITS files are present.

---

## File reference

| File | Purpose |
|------|---------|
| `server.py` | Flask server — started by `launch.bat` |
| `viewer.html` | Browser interface served by `server.py` |
| `match_ngc.py` | NGC/IC catalog cross-match — run once |
| `launch.bat` | Starts server and opens browser |
| `install.bat` | One-time setup (Python + packages + NGC match) |
| `hetdex_agn.ipynb` | Original HDR3 data exploration notebook |
| `hetdex_agn_hdr4.ipynb` | HDR4 data exploration notebook |
| `CLAUDE.md` | Guidance for Claude Code AI assistant |

---

## Acknowledgements & Citation

If you use HETDEX data, please include the following acknowledgement:

> HETDEX is led by the University of Texas at Austin McDonald Observatory and Department of Astronomy with participation from the Ludwig-Maximilians-Universität München, Max-Planck-Institut für Extraterrestrische Physik (MPE), Leibniz-Institut für Astrophysik Potsdam (AIP), Texas A&M University, Pennsylvania State University, Institut für Astrophysik Göttingen, The University of Oxford, Max-Planck-Institut für Astrophysik (MPA), The University of Tokyo and Missouri University of Science and Technology.
>
> Observations for HETDEX were obtained with the Hobby-Eberly Telescope (HET), which is a joint project of the University of Texas at Austin, the Pennsylvania State University, Ludwig-Maximilians-Universität München, and Georg-August-Universität Göttingen. The HET is named in honor of its principal benefactors, William P. Hobby and Robert E. Eberly. The Visible Integral-field Replicable Unit Spectrograph (VIRUS) was used for HETDEX observations. VIRUS is a joint project of the University of Texas at Austin, Leibniz-Institut für Astrophysik Potsdam (AIP), Texas A&M University, Max-Planck-Institut für Extraterrestrische Physik (MPE), Ludwig-Maximilians-Universität München, Pennsylvania State University, Institut für Astrophysik Göttingen, University of Oxford, and the Max-Planck-Institut fur Astrophysik (MPA).
>
> The authors acknowledge the Texas Advanced Computing Center (TACC) at The University of Texas at Austin for providing high performance computing, visualization, and storage resources that have contributed to the research results reported within this paper. URL: http://www.tacc.utexas.edu
>
> Funding for HETDEX has been provided by the partner institutions, the National Science Foundation, the State of Texas, the US Air Force, and by generous support from private individuals and foundations.

---

*Built by the HAS Data Special Interest Group.*
