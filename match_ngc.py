#!/usr/bin/env python3
"""
Cross-match the HETDEX AGN catalog with the NGC/IC catalog (VizieR VII/118)
and generate a self-contained local HTML viewer with two tabs:
  • Spectra   — select a matched NGC/IC object and plot its flux spectrum
  • Sky Map   — RA vs Dec scatter of all 5322 AGN, NGC matches highlighted

Requirements:
    pip install astroquery astropy numpy

Usage:
    python match_ngc.py

Output:
    ngc_viewer.html   (open in any modern browser — no local server needed)
"""

import sys
import json
import numpy as np
from pathlib import Path
from astropy.io import fits
from astropy.table import Table
from astropy.coordinates import SkyCoord
import astropy.units as u

FITS_FILE           = "hetdex_agn.fits"
MATCH_RADIUS_ARCSEC = 60.0      # increase if too few matches
OUTPUT_JSON         = "ngc_matched.json"


# ── NGC catalog ────────────────────────────────────────────────────────────────

def fetch_ngc():
    try:
        from astroquery.vizier import Vizier
    except ImportError:
        sys.exit("astroquery not found — run:  pip install astroquery")

    print("Downloading NGC 2000.0 catalog from VizieR (VII/118)...")
    v = Vizier(columns=["*"], row_limit=-1)
    tables = v.get_catalogs("VII/118")

    for t in tables:
        if any(c in t.colnames for c in ("RAJ2000", "_RAJ2000", "RA2000", "RAB2000")):
            print(f"  {len(t)} entries  |  cols: {t.colnames}")
            return t

    t = tables[0]
    print(f"  Using first table: {len(t)} entries  |  cols: {t.colnames}")
    return t


def _parse_rab2000(ra_str):
    """'HH MM.m' -> decimal degrees."""
    parts = ra_str.strip().split()
    h = float(parts[0])
    m = float(parts[1]) if len(parts) > 1 else 0.0
    return (h + m / 60.0) * 15.0


def _parse_deb2000(dec_str):
    """'+DD MM' or '-DD MM' -> decimal degrees."""
    s = dec_str.strip()
    sign = -1.0 if s.startswith("-") else 1.0
    s = s.lstrip("+-")
    parts = s.split()
    d = float(parts[0])
    m = float(parts[1]) if len(parts) > 1 else 0.0
    return sign * (d + m / 60.0)


def ngc_skycoord(ngc):
    cols = set(ngc.colnames)

    if "RAB2000" in cols and "DEB2000" in cols:
        ra_deg  = np.array([_parse_rab2000(str(v)) for v in ngc["RAB2000"]])
        dec_deg = np.array([_parse_deb2000(str(v)) for v in ngc["DEB2000"]])
        return SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg)

    for ra_col, dec_col, unit in [
        ("RAJ2000", "DEJ2000", (u.hourangle, u.deg)),
        ("_RAJ2000", "_DEJ2000", (u.deg, u.deg)),
        ("RA2000",  "DE2000",   (u.hourangle, u.deg)),
        ("RA",      "Dec",      (u.deg, u.deg)),
    ]:
        if ra_col in cols and dec_col in cols:
            for trial_unit in [(u.hourangle, u.deg), (u.deg, u.deg)]:
                try:
                    return SkyCoord(ngc[ra_col], ngc[dec_col], unit=trial_unit)
                except Exception:
                    pass

    raise RuntimeError(f"Cannot parse coordinates from columns: {ngc.colnames}")


def ngc_name(ngc, row_idx):
    for col in ("Name", "NGC", "name", "ID"):
        if col in ngc.colnames:
            raw = str(ngc[row_idx][col]).strip()
            if raw.startswith("I") and raw[1:].strip().isdigit():
                return f"IC {raw[1:].strip()}"
            elif raw.isdigit():
                return f"NGC {raw}"
            return raw
    return f"row_{row_idx}"


# ── Helpers ────────────────────────────────────────────────────────────────────

def clean_spectrum(arr):
    out = []
    for v in arr:
        try:
            f = float(v)
            out.append(None if (np.isnan(f) or np.isinf(f)) else round(f, 5))
        except Exception:
            out.append(None)
    return out


def sort_key(obj):
    name = obj["name"]
    for prefix in ("NGC ", "IC "):
        if name.startswith(prefix):
            try:
                return (0 if prefix[0] == "N" else 1, int(name[len(prefix):].strip()))
            except ValueError:
                pass
    return (2, name)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"Reading {FITS_FILE} ...")
    hdul  = fits.open(FITS_FILE)
    agn   = Table.read(FITS_FILE, format="fits", hdu=1)
    flux  = hdul[2].data    # (5322, 1036) — extinction-corrected spectra
    err   = hdul[3].data    # (5322, 1036) — corresponding errors

    n_wave = hdul[2].header["NAXIS1"]
    wave   = (3470.0 + 2.0 * np.arange(n_wave)).tolist()

    ngc    = fetch_ngc()
    ngc_sc = ngc_skycoord(ngc)
    agn_sc = SkyCoord(ra=agn["ra"].data.astype(float) * u.deg,
                      dec=agn["dec"].data.astype(float) * u.deg)

    idx, sep, _ = agn_sc.match_to_catalog_sky(ngc_sc)
    mask = sep < MATCH_RADIUS_ARCSEC * u.arcsec

    n = int(mask.sum())
    print(f"Matched {n} AGN within {MATCH_RADIUS_ARCSEC:.0f} arcsec of an NGC/IC object.")
    if n == 0:
        print(f"No matches. Try increasing MATCH_RADIUS_ARCSEC (currently {MATCH_RADIUS_ARCSEC}).")

    # NGC-matched objects with spectra
    objects = []
    for i in np.where(mask)[0]:
        objects.append({
            "name":       ngc_name(ngc, idx[i]),
            "agnid":      int(agn["agnid"][i]),
            "ra":         round(float(agn["ra"][i]),  6),
            "dec":        round(float(agn["dec"][i]), 6),
            "z":          round(float(agn["z"][i]),   5),
            "zflag":      int(agn["zflag"][i]),
            "sep_arcsec": round(float(sep[i].to(u.arcsec).value), 2),
            "flux":       clean_spectrum(flux[i]),
            "error":      clean_spectrum(err[i]),
        })
    objects.sort(key=sort_key)

    payload = {
        "wavelength":           wave,
        "match_radius_arcsec":  MATCH_RADIUS_ARCSEC,
        "n_agn_total":          int(len(agn)),
        "n_matched":            n,
        "objects":              objects,
    }

    Path(OUTPUT_JSON).write_text(json.dumps(payload), encoding="utf-8")
    print(f"Saved {n} matched objects to {OUTPUT_JSON}.")
    print("Start the viewer with:  python server.py")


if __name__ == "__main__":
    main()
