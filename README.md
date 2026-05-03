# dv-hardware

Hardware (KiCad) projects for the Driverless section of U-Motorsport (URJC Formula Student).

Firmware lives in [UM-Driverless/kart_medulla](https://github.com/UM-Driverless/kart_medulla). Pair board revisions with firmware releases via matching git tags (e.g. `medulla-v1.2` here, `medulla-v1.2-fw` there).

## Layout
```
lib/                 shared symbols, footprints, 3D models — referenced by every project
projects/<board>/    one folder per board (KiCad project + EasyEDA source archive)
fab/<board>/<rev>/   released Gerbers, BOM, pick-and-place, JLC zip
docs/                cross-board notes
.agents/             agent-readable project knowledge (history, errors)
```

## Migration status
Projects originate in EasyEDA Pro and are being migrated to KiCad 9. Each `projects/<board>/` keeps:
- `easyeda-source/` — original `.epro` exports for reference (do not edit)
- `<board>.kicad_pro` (and friends) — the live KiCad project after import

## Workflow
1. `git pull --rebase` before starting work.
2. One person per board at a time — coordinate in chat. KiCad files are text but not line-mergeable.
3. Commit small, commit often.
4. Run `kicad-cli sch erc` and `kicad-cli pcb drc` before fab. CI does this automatically (TODO).
