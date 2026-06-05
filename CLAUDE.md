# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jupyter notebook project for exploring and analyzing the HETDEX (Hobby-Eberly Telescope Dark Energy Experiment) AGN catalog. The primary data file is `hetdex_agn.fits` and the analysis is in `hetdex_agn.ipynb`.

## Running the Notebook

```bash
jupyter notebook hetdex_agn.ipynb
# or
jupyter lab
```

## FITS File Structure

`hetdex_agn.fits` has 6 extensions:

| Ext | Name | Type | Description |
|-----|------|------|-------------|
| 1 | `basic_info` | BinTable (5322×159) | One row per unique AGN — the main catalog |
| 2 | `flux_array` | Image (1036×5322) | Spectra for `detectid_best` (extinction-corrected, E(B-V)=0.02) |
| 3 | `error_array` | Image (1036×5322) | Errors for ext 2 |
| 4 | `repeat_info` | BinTable (6004×3) | One row per observation (agnid, nshots, shotid) |
| 5 | `flux_array_repeat` | Image (1036×6004) | Raw spectra for all repeat observations (no extinction correction) |
| 6 | `error_array_repeat` | Image (1036×6004) | Errors for ext 5 |

## Key Data Facts

- **5322 unique AGNs** in the main catalog (ext 1); **6004 rows** in repeat observations (ext 4/5/6)
- **Wavelength grid**: 3470–5540 Å, step = 2 Å, 1036 elements (`wave_start=3470.0`, `wave_step=2.0`)
- **Flux units**: 1×10⁻¹⁷ erg/cm²/s/Å
- AGNs are FOF-grouped with linking lengths Δr = 5 arcsec, Δz = 0.1; `detectid_best` is the detection closest to the FOF center
- Ext 2/3 have extinction correction applied; ext 5/6 are raw

## Standard Patterns

**Open the file and read the main catalog:**
```python
from astropy.io import fits
from astropy.table import Table
import numpy as np

fname = 'hetdex_agn.fits'
hdul = fits.open(fname)
agn = Table.read(fname, format='fits', hdu=1)
```

**Build the wavelength array:**
```python
wave_start, wave_step = 3470.0, 2.0
wave_arr = wave_start + wave_step * np.arange(hdul[2].header['NAXIS1'])
```

**Access spectra for a single AGN (ext 2/3):**
```python
im = hdul[2].data       # shape (5322, 1036)
im_er = hdul[3].data
sel = agn['agnid'] == agnid
flux = im[sel][0]
```

**Access all repeat observations for an AGN (ext 5/6):**
```python
tab = Table.read(fname, format='fits', hdu=4)
im_arr = hdul[5].data   # shape (6004, 1036)
sel = np.where(tab['agnid'] == agnid)
flux_arr = im_arr[sel]
```

## Dependencies

- `numpy`
- `astropy` (io.fits, table)
- `matplotlib`
