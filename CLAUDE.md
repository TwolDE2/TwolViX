# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is **enigma2**, the C++/Python middleware that runs on Linux-based DVB set-top boxes (the UI, tuner/service handling, timers, plugins, etc. for satellite/cable/terrestrial/IPTV receivers). This specific repository is **TwolViX**, a personal fork of OpenViX's enigma2, tracked on the `Py3E` branch (current active branch; `Py3`, `Py3D`, `Py3F` and `Developer` are related branches built by the same CI workflow).

The repo has many git remotes pointing at sibling enigma2 forks (OpenViX upstream, OpenPLi, OpenATV, BlackHole, teamblue-e2, Huevos, WXbet, etc.) — useful for diffing/cherry-picking fixes between forks with `git fetch <remote>` / `git log <remote>/<branch>`.

This repo builds the enigma2 component in isolation (autotools) for compile/lint checking; a full bootable receiver image is built separately via the oe-alliance/bitbake build environment described in [README.md](README.md), which pulls this repo in as one layer.

## Build

```sh
autoreconf -i
./configure --with-libsdl=no --with-boxtype=nobox --enable-dependency-tracking ac_cv_prog_c_openmp=-fopenmp --with-gstversion=1.0 --with-textlcd
make
```

This is exactly what [.github/workflows/enigma2.yml](.github/workflows/enigma2.yml) runs on every push/PR, after installing enigma2's native dependencies (libdvbsi++, libsigc++-3, tuxtxt/libtuxtxt — see the workflow for the exact clone/build steps for each). `--with-boxtype=nobox` builds without a specific receiver's hardware driver, which is what CI and most local sanity builds use.

`python -m compileall .` is run in CI after the build to catch Python syntax errors across the tree.

## Lint / format

CI lint check (also run with `--exit-zero`, so it never fails the build, but its output should be clean):

```sh
flake8 --builtins="_,ngettext,pgettext" --ignore=W191,W503,W504,E128,E501,E722,F824 .
```

[doc/CONTRIBUTING.md](doc/CONTRIBUTING.md) additionally asks contributors to run `ruff` before submitting:

```sh
ruff check --select E,F,W --ignore W191,E501 .
```

Notes on style enforced by these ignore lists:
- Indentation is **tabs**, not spaces (W191 ignored) — match existing files.
- Line length is not enforced (E501 ignored).
- All files must use Unix line endings (LF only) — CI checks this.

There are `CI/PEP8.sh`, `CI/chmod.sh`, `CI/dos2unix.sh`, and `CI/build.sh` scripts used by this fork's own release pipeline. **Do not run these** as ad-hoc dev commands — each one runs `git add -u / git add * / git commit` (and `build.sh` pushes to `upstream Py3E`), so they mutate git history and push on their own.

## Tests

Python-only tests live under [tests/](tests/) (C++ runtime pieces are stubbed out in Python so components can be tested without a real box). Run the timer test with:

```sh
cd tests
PYTHONPATH=.:..:../lib/python/ python test_timer.py
```

See [tests/README](tests/README) for the testing philosophy (keep components separable, avoid adding test-only hooks into components).

## Architecture

- **`main/`** — process entry point (`enigma.cpp`), the `bsod` crash screen, and version info.
- **`lib/`** — the C++ core, split by subsystem: `base` (event loop, timers, basic types), `dvb`/`dvb_ci` (tuner, demux, CI/CAM handling), `service` (service/playback abstraction), `nav` (navigation between services), `gui`/`gdi` (widget toolkit and graphics/rendering, including the GLES/EGL path), `driver` (hardware abstraction: frontend, RC, LCD, etc.), `network`, `timeshift`, `mmi`, `actions`, `components`.
- **`lib/python/`** — the SWIG bridge (`enigma_python.i` and the other `*.i` files) that exposes the C++ core as the `enigma` Python module, plus the Python application layer:
  - `Screens/` — individual UI screens (one class per screen, e.g. channel selection, EPG, setup dialogs).
  - `Components/` — reusable UI widgets and the config framework (`config.py`), plus `Components/Converter` and `Components/Sources` (the data-binding layer screens use to display live state).
  - `Plugins/Extensions/` and `Plugins/SystemPlugins/` — installable plugins; `Plugin.py`/`newplugin.py` define the plugin descriptor API.
  - `Navigation.py`, `NavigationInstance.py`, `RecordTimer.py`, `PowerTimer.py`, `timer.py`, `Session.py` — core Python-side runtime services (playback navigation, recording/power timers, session/dialog stack).
  - `skin.py` — parses the XML skin files that lay out screens (skin XML assets live under `data/`).
- **`data/`** — non-code assets: skins, fonts, boot/standby graphics, display resolution profiles (`display*` dirs), provider/encoding tables.
- **`po/`** — gettext translation catalogs.
- **`tools/`** — standalone helper scripts (picon generation, skin/SVG conversion, meta-index generation) invoked from the Makefiles or manually.
- **`doc/`** — user/developer-facing reference docs (skin format, setup XML format, button guide, return codes, etc.) — check here before reverse-engineering behavior from code.

Build wiring: each directory has its own `Makefile.am`; the top-level `Makefile.am` lists the built subdirs. `configure.ac` is the single autoconf script covering both the C++ build and Python/SWIG setup (`AX_PYTHON_DEVEL`, `AX_PKG_SWIG`).

## AI-assisted contributions

This project has an explicit AI policy in [doc/CONTRIBUTING.md](doc/CONTRIBUTING.md) that applies to any Claude-assisted work destined for a PR:
- AI use must be disclosed in the PR.
- A human must review and be able to explain all submitted code; PRs that read as "AI slop" are rejected.
- Fully autonomous AI PR submission (generate + open PR with no human review step) is not permitted.
- Don't use AI to write forum/issue/PR discussion text on the contributor's behalf.
