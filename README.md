# dv-hardware

Hardware (KiCad) projects for the Driverless section of U-Motorsport (URJC Formula Student).

Firmware lives in [UM-Driverless/kart-medulla](https://github.com/UM-Driverless/kart-medulla). Pair board revisions with firmware releases via matching git tags (e.g. `medulla-v1.2` here, `medulla-v1.2-fw` there).

## Layout
```
lib/                 shared symbols, footprints, 3D models — referenced by every project
projects/<board>/    one folder per board (KiCad project + EasyEDA source archive)
fab/<board>/<rev>/   released Gerbers, BOM, pick-and-place, JLC zip
docs/                cross-board notes
.agents/             agent-readable project knowledge (history, errors)
```

## Board identity
A manufactured board is identified by the commit in this repo that its gerbers were exported from,
written on the board as a QR code or label (short hash is enough). Firmware repos quote that hash to
declare which hardware they target. Because rework exists on a physical board and in no commit, each
board also carries a rework list alongside its hash. Worked example and the boards that exist:
[`projects/kart-medulla/README.md`](projects/kart-medulla/README.md).

## Migration status
Projects originate in EasyEDA Pro and are being migrated to KiCad 9. Each `projects/<board>/` keeps:
- `easyeda-source/` — original `.epro` exports for reference (do not edit)
- `<board>.kicad_pro` (and friends) — the live KiCad project after import

## First-time setup

Install **KiCad 10.x** with the **3D shapes** package included (default in the official installer). The boards reference `${KICAD10_3DMODEL_DIR}` for standard parts (caps, resistors, SOIC, SOT, headers, …); without that variable set, the 3D viewer comes up empty.

After installing, verify the path:

- macOS: `KiCad → Settings… → Configure Paths…` → row `KICAD10_3DMODEL_DIR` should point to `/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels`
- Linux: `/usr/share/kicad/3dmodels`
- Windows: `C:\Program Files\KiCad\10.0\share\kicad\3dmodels`

Project-specific 3D models (parts not in KiCad's standard library — connectors, the MAX4660, …) live next to the board under `projects/<board>/3dmodels/` and are referenced via `${KIPRJMOD}/3dmodels/...` so they travel with the repo.

## Workflow
1. `git pull --rebase` before starting work.
2. One person per board at a time — coordinate in chat. KiCad files are text but not line-mergeable.
3. Commit small, commit often.
4. Run `kicad-cli sch erc` and `kicad-cli pcb drc` before fab. CI does this automatically (TODO).
