#!/usr/bin/env python3
"""
Local Flask server for the HAS DATA SIG HETDEX Viewer.

Supports multiple HETDEX data releases simultaneously.
Place the FITS files alongside this script, then run:
    python server.py

FITS files are NOT included in this repository.
Download them from:  https://hetdex.org/data-results/#pdr1

Usage:
    python server.py          # http://localhost:5000
    python server.py 8080     # custom port
"""

import sys
import json
import numpy as np
from pathlib import Path

try:
    from flask import Flask, jsonify, send_file, request
except ImportError:
    sys.exit("Flask not found — run:  pip install flask")

from astropy.io import fits
from astropy.table import Table

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000

# ── Dataset definitions ────────────────────────────────────────────────────────
# Add future releases here following the same pattern.

DATASET_CONFIG = {
    "hdr3": {
        "file":      "hetdex_agn.fits",
        "label":     "HDR3 — 5,322 AGN",
        "mag_col":   "r_aper",
        "mag_label": "r-band",
        "flux_ext":  2,
        "err_ext":   3,
    },
    "hdr4": {
        "file":      "hetdex_agn_hdr4.fits",
        "label":     "HDR4 — 15,940 AGN",
        "mag_col":   "mag_g_wide",
        "mag_label": "g-wide",
        "flux_ext":  2,
        "err_ext":   3,
    },
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def _f(v):
    """Float or None for NaN / Inf / fill sentinel (-99)."""
    try:
        x = float(v)
        return None if (np.isnan(x) or np.isinf(x) or x <= -99) else x
    except Exception:
        return None

def _r(v, n):
    x = _f(v)
    return round(x, n) if x is not None else None

# ── Load each dataset that has a local FITS file ───────────────────────────────

def load_dataset(key, cfg):
    p = Path(cfg["file"])
    if not p.exists():
        return None

    print(f"  [{key}] Loading {cfg['file']} ...", flush=True)
    hdul = fits.open(p)
    agn  = Table.read(p, format="fits", hdu=1)

    n_wave = hdul[cfg["flux_ext"]].header["NAXIS1"]
    wave   = (3470.0 + 2.0 * np.arange(n_wave)).tolist()
    mag_col = cfg["mag_col"]

    meta = [
        {
            "agnid": int(agn["agnid"][i]),
            "ra":    _r(agn["ra"][i],  5),
            "dec":   _r(agn["dec"][i], 5),
            "z":     _r(agn["z"][i],   5),
            "mag":   _r(agn[mag_col][i], 3) if mag_col in agn.colnames else None,
            "field": str(agn["field"][i]).strip(),
            "zflag": int(agn["zflag"][i]),
            "snr":   _r(agn["snr_LyA"][i], 2) if "snr_LyA" in agn.colnames else None,
        }
        for i in range(len(agn))
    ]

    print(f"  [{key}] {len(meta)} AGN ready.", flush=True)
    return {
        "meta":      meta,
        "wave":      wave,
        "flux":      hdul[cfg["flux_ext"]].data,
        "err":       hdul[cfg["err_ext"]].data,
        "id2idx":    {int(agn["agnid"][i]): i for i in range(len(agn))},
        "label":     cfg["label"],
        "mag_label": cfg["mag_label"],
    }


print("Loading datasets...", flush=True)
DS = {}
for _key, _cfg in DATASET_CONFIG.items():
    _ds = load_dataset(_key, _cfg)
    if _ds:
        DS[_key] = _ds
    else:
        print(f"  [{_key}] {_cfg['file']} not found — skipped.", flush=True)

if not DS:
    sys.exit(
        "\nNo HETDEX FITS files found in this directory.\n"
        "Download them from:  https://hetdex.org/data-results/#pdr1\n"
        "Then place them alongside server.py and try again.\n"
    )

# Prefer the newest release as the default
DEFAULT_DS = next((k for k in ["hdr4", "hdr3"] if k in DS), next(iter(DS)))

# ── Flask app ──────────────────────────────────────────────────────────────────

app = Flask(__name__)


def _get_ds():
    key = request.args.get("ds", DEFAULT_DS)
    return DS.get(key, DS[DEFAULT_DS])


@app.route("/")
def index():
    return send_file("viewer.html")


@app.route("/api/datasets")
def api_datasets():
    return jsonify({
        "available": list(DS.keys()),
        "default":   DEFAULT_DS,
        "info":      {k: {"label": v["label"], "mag_label": v["mag_label"]}
                      for k, v in DS.items()},
    })


@app.route("/api/meta")
def api_meta():
    ds = _get_ds()
    return jsonify({"wavelength": ds["wave"], "n_total": len(ds["meta"]), "agn": ds["meta"]})


@app.route("/api/spectrum/<int:agnid>")
def api_spectrum(agnid):
    ds  = _get_ds()
    idx = ds["id2idx"].get(agnid)
    if idx is None:
        return jsonify({"error": "not found"}), 404

    def clean(a):
        return [None if (np.isnan(v) or np.isinf(v)) else round(float(v), 5) for v in a]

    return jsonify({
        "agnid": agnid,
        "flux":  clean(ds["flux"][idx]),
        "error": clean(ds["err"][idx]),
    })


@app.route("/api/ngc")
def api_ngc():
    p = Path("ngc_matched.json")
    if not p.exists():
        return jsonify({"objects": [], "n_matched": 0,
                        "message": "Run match_ngc.py to generate NGC matches."})
    return jsonify(json.loads(p.read_text("utf-8")))


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nOpen  http://localhost:{PORT}  in your browser.")
    print("Press Ctrl+C to stop.\n")
    app.run(port=PORT, debug=False)
