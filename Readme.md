
# Arctic Fuse 3 (BigDaddy)

LibreELEC adaptation of [CE-Repo's Arctic Fuse 3 (U3k)](https://github.com/CE-Repo/skin.arctic.fuse.3),
originally by jurialmunkey, with U3k changes by jamal2362.
Updated through CE-Repo commit `0dc1747ebaf3378a90f101edd354876c791b77ca`
(U3k 21.3.5.11, piers branch), released as BigDaddy 1.0.8.
Includes add-on browser search, Simple hubs, layout/icon selectors, per-hub
play/browse actions, ratings/subtitle fixes and weather/FlixArt options.

## Target and installation

Target: [CroqueMr LibreELEC x86 DV R1.0.0-Beta4](https://github.com/CroqueMr/libreelec-x86-DV/releases/tag/R1.0.0-Beta4),
LibreELEC 13.0 with Kodi 22 RC1 and GUI API 5.18.0.
This release follows upstream's move to Kodi 22 and requires GUI API 5.18.0;
it is not an update for Kodi 21. The helper dependency minimums have not been lowered.

Install **Arctic Fuse 3 (BigDaddy)** from **Look and feel > Skin** in the
bigdaddy-cpm Kodi repository at https://bigdaddy-cpm.github.io/.
Its separate ID, `skin.arctic.fuse.3.bigdaddy`, keeps the original skin and its
widget settings untouched. This skin starts with its own settings; it does not
automatically copy the original configuration or switch the active skin.

Required helpers are Skin Variables 2.3.12+, Texture Maker 0.2.9+ and
TMDbHelper 6.22.2+, plus the listed font/weather-icon/studio resources.
Update Skin Variables and TMDbHelper from [Jurialmunkey's repository](https://jurialmunkey.github.io/repository.jurialmunkey/) before
installing this release if your versions are below these minimums.
For a fresh Kodi installation, install helpers from their official repositories first.

Before updating, switch temporarily to Estuary. If Arctic Splash is installed,
update it to 1.1.1 or newer first: Kodi enforces the minimum version even for an
optional dependency when it is already installed. An outdated installed Splash
can abort the update after Kodi unloads the active skin. Restart Kodi after
installation, then switch back to BigDaddy. Do not delete your skin settings.

## Adaptations

- Distinct identity throughout shortcut generation, skin users, settings and version labels.
- Platform-aware LibreELEC/CoreELEC/Kodi startup label and accurate Kodi build text.
- Optional Arctic Splash 1.1.1+: bundled backgrounds keep startup and weather
  cards usable without it. Upstream now uses Splash for forecast-card artwork
  and no longer requires the separate Arctic Weather pack. Background style
  packs are optional and use upstream's simple-background fallback when absent.
  Weather cards also fall back to bundled artwork if an installed resource pack
  lacks the requested weather image; style-pack weather works without Splash.
  No resource packages are silently downloaded or mirrored by this fork.
- Removed the Android/NAND reboot shortcut from this LibreELEC-targeted fork.
- Retained U3k artwork and information-bar features. The playback-info OSD button
  prefers **BigDaddy Playback Info** when enabled (skin 1.0.1+), with the original
  TinyPPI action as a fallback. Install the new overlay separately from
  **Program add-ons** in the bigdaddy-cpm repository; no new mandatory dependency.
- Added conditional DV rendering, display, transport, profile, enhancement-layer
  and render-usage fields to player information using Beta4's native window properties.
  All eight fields are retained as scrollable video-row cards in the new process
  display, including the GPU-availability guard. Empty/unsupported fields stay hidden.
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
