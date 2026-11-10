# 3-Trillion Track 2 — 2026-11-10

Open `dist/index.html` directly in a browser. Classic JavaScript includes all data via `assets/data.js`; no runtime fetch, module loader, server, account or installation is needed. All images and dependencies are relative local files. External source links and actual email sending need internet.

Latest grades (33 complete records) and historical additions (67 records) are separate map versions. Latest process-posterior chemistry (230 pairs) and historical descriptive additions (273 pairs) use separate palettes and labels. The source registry retains 575 multilateral relations separately. Evidence includes 777 UNICEF activities and 3,215 result observations with baseline/target/actual text. No UNICEF observations are attributed to bilateral scores.

`language.js`: Korean/English UI, dynamic labels, preference and navigation persistence. Original project names retain source language.
`methods.js`: eight bilingual method explanations with formulas, definitions, sensitivity and validation results.
`team/people/index.html` and `team/contact/index.html`: retained Track 1 content and dependencies.
`assets/flags`: flat local SVG flags (flag-icons MIT; license included). Country metadata ODbL notice included.

Refresh registries and evidence from the course research outputs with `python3 scripts/build-data.py`. The geographic/profile base and original project-level score snapshot remain tracked in `assets/data.json`. Validate with `python3 scripts/validate-data.py`. Check JS with `node --check dist/app.js` and equivalents for language, methods and evidence. Package with `python3 scripts/package-offline.py <absolute-output-folder>`; the packager validates all relative HTML links, anchors, 249 flag files and registry counts.

UI verification used local HTTP preview because the embedded browser blocks file:// navigation. Independent file/dependency checks validate the standalone package structure.

GitHub source note: the People and Contact entry pages link to the existing repository team pages. Automatic upload review rejected duplicating identifiable contact/profile content. The previously delivered local offline bundle remains separate and unchanged.
