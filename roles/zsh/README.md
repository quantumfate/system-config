# Shell cheatsheet

Rendered by `roles/zsh`. Edit the templates, not `~/.zshrc`.

## Prompt

```
~/P/c/q/system-config/roles/zsh  main ⇡2 +1 !8 ?2  .venv  1&  4.2s  ✗1
❯
```

|                      |                                                           |
| -------------------- | --------------------------------------------------------- |
| `~/P/c/q/`           | abbreviated; **bold** = repo root, full = last two        |
| `⇡2 ⇣1`              | ahead / behind upstream                                   |
| `+n !n ?n ✗n`        | staged / modified / untracked / conflicted                |
| `rebase 3/7`         | operation in progress — finish or abort it first          |
| `1&` `4.2s` `✗1`     | background jobs · duration (>3s) · exit code (`^C` = 130) |
| `❯` mauve / `❮` blue | vi insert / normal (cursor changes too)                   |

## Keys

|                     |                                                         |
| ------------------- | ------------------------------------------------------- |
| `Esc`               | normal mode — `ciw`, `dd`, `b/w`, `/` to search history |
| `v` (normal)        | open the line in nvim, save to run it                   |
| `^Space`            | accept autosuggestion · `^F` accept one word            |
| `^R` `^T` `Alt-C`   | fzf: history · files · cd                               |
| `^P` `^N` / `j` `k` | history matching what you typed                         |
| `^A ^E ^K ^U ^W ^Y` | line editing in insert mode                             |
| `^Z`                | suspend — and `^Z` again on an empty line resumes       |
| `^V`                | paste from the Wayland clipboard                        |
| `Tab` `S-Tab` | move in **any** fzf; in a multi-select list Tab also marks |
| `<` `>` | fzf-tab: switch completion group |

## Moving

|              |                                                   |
| ------------ | ------------------------------------------------- |
| `foo/bar`    | plain path is a `cd` (AUTO_CD)                    |
| `z proj`     | jump by frecency · `..` `...` `....`              |
| `bd name`    | jump up to a named ancestor                       |
| `d`, `1`–`9` | visited directories, and jump back into one       |
| `ya`         | yazi; leaves you in the directory you exited from |
| `mkcd x`     | make it and enter it                              |

## git

Plain aliases act. **`f`-prefixed ask first** (fzf picker + preview).

|                                     |                                                       |
| ----------------------------------- | ----------------------------------------------------- |
| `gs` `gd` `gds` `gl` `gll`          | status · diff · staged diff · log · graph             |
| `ga` `gaa` `gc` `gca` `gcm`         | add · add all · commit -m · -am · amend               |
| `gsw` `gswc` `gco` `gcb`            | switch · switch -c · checkout · checkout -b           |
| `gf` `gp` `gpl`                     | fetch --all --prune · push · pull --ff-only           |
| `gfx <sha>` → `gri`                 | fixup, then rebase -i --autosquash                    |
| `gabs`                              | git-absorb: finds the commit to fix up from the diff  |
| `gundo` `grl`                       | uncommit (keep staged) · reflog, the undo log         |
| `gbl` `gdt`                         | blame -w -C -C -C · difftastic (ignores reformatting) |
| `gbclean` `groot`                   | delete merged branches (asks) · cd to repo root       |
| `fa` `fdi` `flog` `fco` `frb` `fcf` | pick: stage · diff · log · branch · rebase · discard  |
| `lg`                                | lazygit                                               |

## Tools

`du df ps top` are `dust duf procs btop`; `command du` reaches the original.

|                                  |                                                           |
| -------------------------------- | --------------------------------------------------------- |
| `rg` `fd`                        | `rg!` / `fd!` also search ignored and hidden files        |
| `sd a b file`                    | replace, no regex dialect surprises                       |
| `watch-run -- cmd`               | re-run on file change · `timer cmd` benchmark · `loc` LOC |
| `tp` `tls` `tre`                 | trash-put / list / restore (`rm` is still `rm -i`)        |
| `sc` `scu` `jf` `failed`         | systemctl · --user · journal -f · failed units            |
| `logerr` `logwarn` `logk` `logs` | log viewer (own tmux server, see main README)             |
| `extract f` `bak f` `cheat cmd`  | any archive · timestamped copy · cheat.sh                 |
| `update` `cleanup` `big` `rip`   | pacman upgrade · orphans · largest · recent               |

## Pipeline shorthand

Global aliases — they expand anywhere on the line.

```
rg TODO G test H          # | rg test | head -20
journalctl -u nginx L     # | less
git branch U CP           # | sort -u | wl-copy
```

`G L H T WC J S U X CP` · `NE DN NUL` silence stderr / stdout / both.

## tmux

`C-b` prefix. The session chip fills mauve while it is held.

|                               |                                              |
| ----------------------------- | -------------------------------------------- |
| `C-b C-o`                     | tms — open or create a session for a project |
| `C-b C-s` `C-b C-w`           | pick a session · pick a window, anywhere     |
| `C-b (` `C-b )`               | previous / next session                      |
| `C-b C-e` `C-b C-r` `C-b C-k` | rename · refresh · kill session              |

## Maintenance

```
antidote update                      # update plugins
ansible-playbook … --tags zsh        # re-render everything here
exec zsh                             # reload (alias: reload)
```
