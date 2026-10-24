
# Arctic Fuse 3 (BigDaddy)

LibreELEC adaptation of [CE-Repo's Arctic Fuse 3 (U3k)](https://github.com/CE-Repo/skin.arctic.fuse.3),
originally by jurialmunkey, with U3k changes by jamal2362.
Updated through CE-Repo commit `9c5b98fa44d5918a059e395617d6359e73933d54`
(U3k 20.3.4.8 / original Arctic Fuse 3.4.8), released as BigDaddy 1.0.2.

## Target and installation

Target: [CroqueMr LibreELEC x86 DV R1.0.0-Beta4](https://github.com/CroqueMr/libreelec-x86-DV/releases/tag/R1.0.0-Beta4),
LibreELEC 13.0 with Kodi 22 RC1 and GUI API 5.18.0.
Kodi declares backward compatibility with the skin's required GUI API 5.17.0;
the helper dependency minimums have not been lowered.

Install **Arctic Fuse 3 (BigDaddy)** from **Look and feel > Skin** in the
bigdaddy-cpm Kodi repository at https://bigdaddy-cpm.github.io/.
Its separate ID, `skin.arctic.fuse.3.bigdaddy`, keeps the original skin and its
widget settings untouched. This skin starts with its own settings; it does not
automatically copy the original configuration or switch the active skin.

Required helpers remain Skin Variables 2.2.9+, Texture Maker 0.2.9+ and
TMDbHelper 6.17.9+, plus the listed font/weather/studio resources.
These were already present at sufficient versions in the target's October 19 log.
For a fresh Kodi installation, install helpers from their official repositories first.

## Adaptations

- Distinct identity throughout shortcut generation, skin users, settings and version labels.
- Platform-aware LibreELEC/CoreELEC/Kodi startup label and accurate Kodi build text.
- Optional Arctic Splash 1.0.6+ and Arctic Weather 1.0.4+ resources: bundled
  backgrounds keep startup and weather cards usable without them. Install/update
  these resources from their upstream repository for animated weather artwork.
  No resource packages are silently downloaded or mirrored by this fork.
- Removed the Android/NAND reboot shortcut from this LibreELEC-targeted fork.
- Retained U3k artwork and information-bar features. The playback-info OSD button
  prefers **BigDaddy Playback Info** when enabled (skin 1.0.1+), with the original
  TinyPPI action as a fallback. Install the new overlay separately from
  **Program add-ons** in the bigdaddy-cpm repository; no new mandatory dependency.
- Added conditional DV rendering, display, transport, profile, enhancement-layer
  and render-usage fields to player information using Beta4's native window properties.
  These fields hide when the build's enhanced player information is disabled or absent.
  Beta4's native O-key handler still cycles from player information to its rendering menu.
- Native Kodi video settings remain in use; no Dolby Vision renderer, firmware,
  passthrough or playback pipeline changes are made by this skin.

XML/JSON, identity, dependencies and ZIP layout are checked offline. Visual layout,
remote navigation and playback overlays still require testing on the target box.

## Validation and packaging

```sh
python tools/check_skin.py
python tools/check_skin.py --build
```

The second command produces a reproducible installable ZIP in `dist/`.
Publishing also requires updating the skin entry and checksum in the separate
`bigdaddy-cpm.github.io` Kodi repository. Upstream-only repository dispatch has
been replaced with validation, so this fork does not dispatch to the author's repository.

## License and attribution

This work is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
or send a letter to Creative Commons, 171 Second Street, Suite 300, San Francisco, California, 94105, USA.
