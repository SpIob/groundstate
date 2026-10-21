# Pipeline environment

Created 2026-10-20 (macOS 26.4, Apple M5, arm64) by Hermes for task T-001.

## What this machine runs

- **Python:** 3.12.13 (Homebrew `python@3.12`), in `pipeline/.venv` (gitignored)
- **uv:** 0.13.3 (Homebrew) — used to create the venv and install packages
- **CHGNet device:** `mps` (Apple GPU) — verified; the load message prints "CHGNet will run on mps"
- **torch:** 2.14.1 (MPS build), **numpy:** 2.5.4

## Direct dependencies (the only four allowed)

| package | version |
|---|---|
| pymatgen | 2026.9.24 |
| mp-api | 0.47.0 |
| ase | 3.29.0 |
| chgnet | 0.4.2 |

Full transitive freeze at creation time (78 packages):

```
annotated-types==0.8.0
arro3-core==0.9.1
ase==3.29.0
bibtexparser==1.4.4
blake3==1.0.11
boto3==1.43.115
botocore==1.43.115
certifi==2026.10.19
charset-normalizer==3.5.2
chgnet==0.4.2
cloudpickle==3.1.2
contourpy==1.4.0
cycler==0.12.1
cython==3.3.0
deltalake==1.5.1
deprecated==3.0.0
emmet-core==0.88.0
filelock==4.2.4
fonttools==4.67.0
fsspec==2026.9.0
idna==3.20
inflect==7.5.0
jinja2==3.1.6
jmespath==1.1.0
joblib==1.6.0
kiwisolver==1.5.1
latexcodec==3.0.1
lxml==6.1.3
markdown-it-py==4.2.0
markupsafe==3.0.4
matplotlib==3.11.2
mdurl==0.1.2
monty==2026.7.16
more-itertools==11.2.1
mp-api==0.47.0
mpmath==1.3.0
narwhals==2.27.1
networkx==3.7
numpy==2.5.4
nvidia-ml-py3==7.352.0
orjson==3.13.0
packaging==26.3
palettable==3.3.3
pandas==3.0.6
pillow==13.0.0
plotly==7.1.0
pubchempy==1.0.5
pyarrow==26.0.0
pybtex==0.26.1
pydantic-core==2.50.1
pydantic-settings==2.16.0
pydantic==2.14.1
pygments==2.21.0
pymatgen-core==2026.10.16
pymatgen-io-validation==0.1.4
pymatgen==2026.9.24
pyparsing==3.3.3
python-dateutil==2.9.0.post0
python-dotenv==1.2.4
pyyaml==6.0.3
requests==2.34.2
rich==15.0.0
ruamel-yaml==0.19.1
s3transfer==0.19.3
scipy==1.18.1
setuptools==84.2.0
six==1.17.0
spglib==2.8.0
sympy==1.14.0
tabulate==0.10.0
torch==2.14.1
tqdm==4.70.1
typeguard==4.6.0
typing-extensions==4.16.0
typing-inspection==0.4.4
uncertainties==3.2.3
urllib3==2.8.0
wrapt==2.5.1
```

## Recreate from scratch

```bash
# one-time tool install (already done on this machine):
brew install uv

# create and fill the venv:
cd pipeline
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python pymatgen mp-api ase chgnet

# activate:
source .venv/bin/activate
```

`MP_API_KEY` must be set in the environment before any mp-api call. It is never written to
any file in this repo (`.env` is gitignored and was not used for setup).

## Smoke tests (all passing, 2026-10-20)

### a. Imports and versions

```
python: 3.12.13
pymatgen: 2026.9.24
mp_api: 0.47.0
ase: 3.29.0
chgnet: 0.4.2
```

### b. CHGNet energy prediction (2-atom Si, diamond structure)

```
CHGNet v0.3.0 initialized with 412,525 parameters
CHGNet will run on mps
pred e/atom: -3.1236684322357178
```

### c. mp-api fetch by formula (LiFePO4, key from environment, never printed)

```
70 polymorphs returned; first three:
mp-1661570 LiFePO4
mp-1661648 LiFePO4
mp-1662030 LiFePO4
```

## Notes / pitfalls hit during setup

- `pymatgen` has no `__version__` attribute; use `importlib.metadata.version("pymatgen")`.
- mp-api 0.47.0 summary-search field names: `nsites` (not `num_sites`), symmetry comes as a
  nested `symmetry` object with `.number` / `.symbol` (there is no `spacegroup_number`
  field). Check the installed client's fields before querying — names drift between versions.
- First `CHGNet.load()` downloads model weights (~45 MB) and built the matplotlib font cache;
  expect a slow first call.
