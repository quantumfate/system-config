# gaming

Native gaming (Lutris, the Ankama launcher) plus emulation, which also runs
through Lutris: one launcher owns every game, and its libretro runner owns the
runtime.

- **Runs when** `gaming`.
- **Vars** `gaming_root`, `gaming_dirs`, `gaming_rom_hacks`,
  `gaming_lutris_libretro`, `gaming_lutris_retroarch_dir` (defaults).
- **Touches** `~/Games/**` and `~/.local/share/lutris/runners/retroarch/**`
  only. No system scope; packages come from `gaming_packages` in
  `group_vars/all/packages.yml`.
- **Tag** `gaming`

## The libretro runner

Lutris' libretro runner wants its own RetroArch under
`~/.local/share/lutris/runners/retroarch` — binary, `cores/<core>_libretro.so`,
and the `info` metadata it parses to build the core list. Left alone it pulls
all three from the libretro buildbot, unversioned and only when online.

So the cores come from the repos instead (`retroarch`, `libretro-core-info`,
`libretro-mgba`, `libretro-melonds`, `libretro-desmume`) and this role
symlinks them into that directory. Lutris then sees an installed runner, never
reaches for the buildbot, and `yay -Syu` updates the emulators along with
everything else. Adding a system is one more `libretro-*` in `gaming_packages`;
dropping one removes its symlink on the next run.

mGBA covers GBA, melonDS the DS (DeSmuME is there as the fallback core for the
hacks melonDS mis-emulates). Per-game core choice stays in Lutris.

## ROM hacks and what this repo will not hold

A hack like Run and Bun or Emerald Kaizo ships as a *patch* — the author's own
diff against a retail cartridge. The patch is theirs to distribute; the base
ROM is not. A patched ROM is a derivative of the copyrighted game, so it is no
more distributable than the original.

Consequences for this playbook:

- **Never commit** base ROMs or built ROMs. Not in git, not in `files/`, not
  base64'd into a var, not in the Ansible vault (encryption changes nothing
  about copyright).
- **Patch files are the author's work** and are commonly redistributed, but
  several hack authors ask that only their official mirror serves them — so
  this role does not vendor or download those either.
- You supply both halves by hand, once, out of band. The role only runs the
  patcher.

Layout:

```
~/Games/roms/gba/pokemon-emerald.gba   # your own dump
~/Games/patches/run-and-bun.bps        # from the author's release
~/Games/roms/gba/run-and-bun.gba       # built here, stays here
```

`~/Games` is outside the repo, so nothing above is ever staged.

## Patching

Lutris' game entries live in its own SQLite database, so the games themselves
are added in Lutris (libretro runner, the built ROM as the ROM file, the core
per system) — this role stops at the ROM.

`flips` handles BPS/IPS/UPS. `xdelta3` handles the `.xdelta` patches most DS
hacks ship. The role picks the tool from the patch extension, is idempotent
(an existing output is left alone), and skips any entry whose base or patch is
missing with a message naming what it wanted.
