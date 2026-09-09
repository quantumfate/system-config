# Shell cheatsheet

Rendered by `roles/zsh`. Edit the templates, not `~/.zshrc`. This file is the
only source for the popup: `roles/zsh/files/cheatsheet.md`.

`Alt-h` opens this file as a picker: one row here is one line there, tagged with
the section it came from. The sections are named after the program they drive,
so a heading is also a search term — type `forgit` in the picker and only its
bindings are left. Enter types the command onto the prompt.

One row is one binding. Where two commands are close relatives they still get a
row each, because a row you cannot search for is a row you will not find.

## fastfetch

The banner every kitty shell opens with. Rows, icons, colours, logo and the
greeting live in `roles/zsh/defaults/main.yml` (`fastfetch_*`); the logo images
ship in `roles/zsh/files/fastfetch/` — drop a new one there and point
`fastfetch_logo` at it.

| Command                        | Effect                                 |
| ------------------------------ | -------------------------------------- |
| `fastfetch`                    | print the banner again                 |
| `fastfetch --list-modules`     | module types available for a new row   |
| `fastfetch --list-logos`       | built-in logos, for `fastfetch_logo_type` other than `kitty` |
| `fastfetch --logo none`        | the text block alone, e.g. to check alignment |

## prompt

What the prompt is telling you. Nothing here is typed.

|                |                                                              |
| -------------- | ------------------------------------------------------------ |
| `~/P/c/q/name` | path, abbreviated — bold is the repo root, last two are full |
| `main`         | branch; the whole git block is absent outside a repo         |
| `⇡2`           | commits ahead of upstream                                    |
| `⇣1`           | commits behind upstream                                      |
| `+n`           | staged changes                                               |
| `!n`           | modified, not staged                                         |
| `?n`           | untracked                                                    |
| `✗n`           | conflicted — resolve before anything else                    |
| `rebase 3/7`   | an operation is in progress; finish or abort it first        |
| `.venv`        | an activated python environment                              |
| `1&`           | background jobs running                                      |
| `4.2s`         | how long the last command took, once it passes 3s            |
| `✗1`           | the last command's exit code (130 means you pressed ^C)      |
| `❯`            | mauve: insert mode, and the cursor is a bar                  |
| `❮`            | blue: normal mode, and the cursor is a block                 |

## zle

The line editor. vi mode, with the emacs keys worth keeping in insert mode.

|          |                                                                        |
| -------- | ---------------------------------------------------------------------- |
| `Esc`    | leave insert mode — then ciw, dd, b, w, 0, $ all work on the line      |
| `v`      | open the line in $EDITOR; saving and quitting runs it                  |
| `V`      | visual-line selection inside the line                                  |
| `/`      | search history backwards (normal mode)                                 |
| `?`      | search history forwards (normal mode)                                  |
| `gg`     | first line of the buffer, or the oldest history entry                  |
| `G`      | last line of the buffer, or the newest                                 |
| `ga`     | what character is under the cursor, in every encoding                  |
| `#`      | comment the line out and push it to history, to come back to           |
| `:`      | run a zle widget by name                                               |
| `^A`     | start of line                                                          |
| `^E`     | end of line                                                            |
| `^K`     | kill to end of line                                                    |
| `^U`     | kill to start of line                                                  |
| `^W`     | kill the word before the cursor                                        |
| `^Y`     | yank back what you just killed                                         |
| `^F`     | forward one word                                                       |
| `^H`     | backspace (and Backspace itself deletes past the insert point)         |
| `^Q`     | quote the next key literally, instead of acting on it                  |
| `^L`     | clear the screen, keeping the line you are typing                      |
| `^X`     | jump to the end of the buffer                                          |
| `Alt-.`  | insert the last word of the previous command; press again for older    |
| `Alt-m`  | copy the word before the cursor from the previous line                 |
| `Alt-<`  | start of the buffer                                                    |
| `Alt->`  | end of the buffer                                                      |
| `Alt-h`  | this cheatsheet, as a picker — enter types the command in              |
| `^Z`     | suspend the foreground job — and again, on an empty line, to resume it |
| `^V`     | paste from the Wayland clipboard                                       |
| `^Space` | accept the whole autosuggestion                                        |
| `^P`     | previous history entry matching what you have typed                    |
| `^N`     | the next one                                                           |
| `k`      | same as ^P, in normal mode                                             |
| `j`      | same as ^N, in normal mode                                             |

## zsh-edit

Word motions that know what a shell word is, and what camelCase is.

|              |                                                             |
| ------------ | ----------------------------------------------------------- |
| `Alt-Left`   | back one shell word — quoted strings and paths count as one |
| `Alt-Right`  | forward one shell word                                      |
| `Ctrl-Left`  | back one subword — stops inside camelCase and snake_case    |
| `Ctrl-Right` | forward one subword                                         |
| `^Alt-B`     | back one subword, without the arrow keys                    |
| `^Alt-F`     | forward one subword                                         |
| `^Alt-H`     | kill the subword behind the cursor                          |
| `^Alt-D`     | kill the subword ahead of it                                |
| `Alt-(`      | kill the whole shell word under the cursor                  |
| `Alt-,`      | complete from history, newer matches first                  |
| `Alt-/`      | complete from history, older matches first                  |

## completion

Tab is fzf-tab; the rest is zsh's completion system, which is worth knowing.

|        |                                                              |
| ------ | ------------------------------------------------------------ |
| `Tab`  | complete through fzf, with a preview of what is highlighted  |
| `<`    | previous completion group (files, then branches, then …)     |
| `>`    | next completion group                                        |
| `^D`   | list what would complete, without completing                 |
| `^G`   | expand the line and show the result, without running it      |
| `^X a` | expand the alias under the cursor into what it stands for    |
| `^X e` | expand the word under the cursor — globs, $vars, `subshells` |
| `^X c` | spell-correct the word under the cursor                      |
| `^X m` | insert the most recently modified file that matches          |
| `^X h` | explain which completion is being used here                  |
| `^X n` | cycle to the next set of completion tags                     |
| `^X ?` | trace why a completion produced what it did                  |

## fzf

Every fzf in the shell shares one theme and one navigation key.

|         |                                                        |
| ------- | ------------------------------------------------------ |
| `^R`    | search history                                         |
| `^T`    | insert a file path, picked                             |
| `Alt-c` | cd into a directory, picked — in both modes                |
| `Tab`   | move down a list — and mark, where marking is possible |
| `S-Tab` | move up                                                |
| `^/`    | toggle the preview pane                                |

## zoxide

Moving, without typing paths.

|           |                                                              |
| --------- | ------------------------------------------------------------ |
| `z proj`  | jump to the best match by frecency                           |
| `zi`      | the same, but pick from a list                               |
| `foo/bar` | a bare path is a cd — AUTO_CD                                |
| `..`      | up one                                                       |
| `...`     | up two, and so on to ......                                  |
| `-`       | back to the previous directory                               |
| `bd name` | up to a named ancestor, however far up it is                 |
| `d`       | the directories you have visited, numbered                   |
| `1`       | jump back into the first of them — through to 9              |
| `mkcd x`  | make a directory and step into it                            |
| `groot`   | cd to the root of this repo                                  |
| `ya`      | yazi; leaves you where you exited, and tells zoxide about it |

## eza

ls is eza. `command ls` still reaches the original.

|      |                          |
| ---- | ------------------------ |
| `ls` | list, directories first  |
| `ll` | long, with ISO dates     |
| `la` | long, including dotfiles |
| `lt` | tree, two levels deep    |

## git

Plain aliases act immediately. The f-prefixed ones ask first.

|             |                                                              |
| ----------- | ------------------------------------------------------------ |
| `g`         | git itself, three letters shorter                            |
| `gs`        | status                                                       |
| `gd`        | diff of what is not staged                                   |
| `gds`       | diff of what is                                              |
| `gdt`       | diff with difftastic — ignores pure reformatting             |
| `gl`        | log, one line per commit                                     |
| `gll`       | log as a graph                                               |
| `glg`       | log with the stat block                                      |
| `glp`       | log with the full patch                                      |
| `gsh`       | show one commit                                              |
| `gbl`       | blame, ignoring whitespace and following moved code          |
| `ga`        | stage a path                                                 |
| `gaa`       | stage everything                                             |
| `gc`        | commit, opening the editor                                   |
| `gcm`       | commit -m                                                    |
| `gca`       | commit -am, staging tracked files on the way                 |
| `gwip`      | a wip commit with hooks skipped — a checkpoint, not a commit |
| `gundo`     | uncommit, keeping the changes staged                         |
| `gfx <sha>` | commit a fixup aimed at that commit                          |
| `gri`       | rebase -i --autosquash, which absorbs the fixups             |
| `gabs`      | git-absorb: works out which commit each hunk belongs to      |
| `grst`      | restore a file to its committed state                        |
| `grss`      | unstage a file, keeping the change                           |
| `grs`       | reset --soft: undo commits, keep everything                  |
| `grh`       | reset --hard: undo commits and throw the work away           |
| `gst`       | stash everything                                             |
| `gsu`       | stash only what is not staged                                |
| `gsl`       | list stashes                                                 |
| `gstp`      | pop the top stash                                            |
| `gb`        | branches, with their upstreams                               |
| `gsw`       | switch to a branch                                           |
| `gswc`      | create a branch and switch to it                             |
| `gco`       | checkout, for the cases switch does not cover                |
| `gcb`       | checkout -b                                                  |
| `gbclean`   | delete the branches already merged (it asks)                 |
| `gcp`       | cherry-pick                                                  |
| `gwt`       | worktree                                                     |
| `gf`        | fetch --all --prune                                          |
| `gp`        | push                                                         |
| `gpl`       | pull --ff-only, so a pull can never write a merge commit     |
| `grl`       | reflog — the log of where HEAD has been, and the real undo   |
| `lg`        | lazygit, for everything the aliases do not cover             |

## forgit

An fzf picker with a preview, every time. The f says it will ask first.

|        |                                                        |
| ------ | ------------------------------------------------------ |
| `fa`   | pick hunks or files to stage                           |
| `fdi`  | pick a file, then a revision, and diff them            |
| `flog` | browse commits with the patch in the preview           |
| `fsh`  | pick a commit and show it                              |
| `fbl`  | pick a file and blame it                               |
| `frl`  | browse the reflog                                      |
| `fco`  | pick a branch to check out                             |
| `fsw`  | pick a branch to switch to                             |
| `fcc`  | pick a commit to check out                             |
| `fct`  | pick a tag to check out                                |
| `fbd`  | pick branches to delete, seeing what is on them        |
| `frb`  | pick the commit to rebase onto                         |
| `ffx`  | pick the commit to fix up                              |
| `fsq`  | pick the commit to squash into                         |
| `frw`  | pick a commit and reword its message                   |
| `frv`  | pick a commit to revert                                |
| `fcp`  | pick commits to cherry-pick, from another branch       |
| `frt`  | pick what to unstage                                   |
| `frs`  | pick what to restore                                   |
| `fcf`  | pick a file and discard its changes, after seeing them |
| `fcl`  | pick untracked files to delete                         |
| `fsp`  | stash a selection rather than everything               |
| `fst`  | browse the stashes                                     |
| `fwt`  | list and pick worktrees                                |
| `fig`  | build a .gitignore from templates                      |

## chezmoi

Dotfiles that live outside this repo.

|         |                                               |
| ------- | --------------------------------------------- |
| `ch`    | chezmoi itself                                |
| `chst`  | what differs from the source state            |
| `chd`   | the diff in full                              |
| `cha`   | add a file to the source state                |
| `chr`   | re-add one that has changed since             |
| `che`   | edit the source of a file                     |
| `chea`  | edit it and apply on save                     |
| `chap`  | apply the source state to the machine         |
| `chup`  | pull and apply in one step                    |
| `chcd`  | cd to the source directory                    |
| `chg`   | run git in the source repo                    |
| `chdoc` | chezmoi doctor, when something will not apply |

## tmux

C-b is the prefix. The session chip fills mauve while it is held.

|           |                                              |
| --------- | -------------------------------------------- |
| `C-b ?`   | a menu of these bindings, which runs them    |
| `C-b /`   | every binding tmux has, the raw list         |
| `C-b C-o` | tms: open or create a session for a project  |
| `C-b C-s` | pick a session                               |
| `C-b C-w` | pick a window, from any session              |
| `C-b s`   | the session tree, most recently active first |
| `C-b (`   | previous session                             |
| `C-b )`   | next session                                 |
| `C-b C-e` | rename this session                          |
| `C-b C-r` | refresh the session list                     |
| `C-b C-k` | kill this session (it asks)                  |
| `t`       | tmux                                         |
| `tl`      | list sessions                                |
| `tm`      | attach, or start one if there is none        |
| `tk`      | kill a session by name                       |

## search

|                  |                                                            |
| ---------------- | ---------------------------------------------------------- |
| `rg`             | ripgrep, smart-case                                        |
| `rg!`            | the same, but also ignored and hidden files                |
| `fd`             | find files by name                                         |
| `fd!`            | the same, but also ignored and hidden files                |
| `sd a b file`    | replace, with no regex dialect surprises                   |
| `loc`            | tokei: lines of code, by language                          |
| `**/*.go`        | zsh globs recursively on its own — no find needed          |
| `*.go~*_test.go` | EXTENDED_GLOB: everything matching, except                 |
| `*(.)`           | only plain files — (/) dirs, (@) symlinks, (*) executables |
| `*(om[1])`       | the newest match — (Om[1]) the oldest, (.Lm+10) over 10MB  |

## files

|                      |                                                            |
| -------------------- | ---------------------------------------------------------- |
| `tp`                 | trash-put — rm is still rm -i                              |
| `tls`                | what is in the trash                                       |
| `tre`                | restore something from it                                  |
| `extract f`          | unpack any archive, without remembering the flags          |
| `bak f`              | a timestamped copy beside the original, before you edit it |
| `mmv '(*).a' '$1.b'` | batch rename by pattern — add -n to see it first           |
| `mcp`                | the same, copying instead of moving                        |
| `mln`                | the same, linking                                          |
| `big`                | the largest files here                                     |
| `rip`                | the most recently modified                                 |
| `v`                  | $EDITOR                                                    |
| `vi`                 | actual vim, when $EDITOR is too much                       |
| `open`               | xdg-open                                                   |
| `cat x.json`         | suffix aliases open by extension: json in jless, md in bat |

## systemd

|          |                                 |
| -------- | ------------------------------- |
| `sc`     | systemctl                       |
| `scu`    | systemctl --user                |
| `jf`     | follow the journal              |
| `jfu`    | follow the user journal         |
| `failed` | units that failed               |
| `jctl`   | this boot, priority 3 and worse |

## logview

A second tmux server on its own socket — see the main README.

|            |                                 |
| ---------- | ------------------------------- |
| `logerr`   | this boot: errors and worse     |
| `logwarn`  | this boot: warnings and worse   |
| `logk`     | the kernel ring buffer          |
| `logaudit` | audit denials                   |
| `logboot`  | this boot, from the top         |
| `logprev`  | the previous boot, from the top |
| `logs`     | what has been captured so far   |

## pacman

|             |                                             |
| ----------- | ------------------------------------------- |
| `update`    | full system upgrade                         |
| `cleanup`   | remove orphans                              |
| `mirror`    | re-rate the mirrorlist                      |
| `fixpacman` | remove a stale db.lck after a killed pacman |
| `grubup`    | regenerate the grub config                  |

## system

du, df, ps and top are dust, duf, procs and btop. `command du` reaches the original.

|                    |                                                  |
| ------------------ | ------------------------------------------------ |
| `du`               | disk usage, as a tree                            |
| `df`               | mounted filesystems                              |
| `ps`               | processes                                        |
| `top`              | btop                                             |
| `psme`             | processes by memory                              |
| `psme10`           | the ten hungriest                                |
| `ports`            | listening sockets, with the process              |
| `myip`             | the public one                                   |
| `hw`               | hardware, short                                  |
| `path`             | $PATH as a readable list                         |
| `hyprclients`      | hyprland's windows, in jless                     |
| `please`           | sudo                                             |
| `serve`            | an http server in this directory                 |
| `tb`               | pipe anything to termbin and get a URL back      |
| `cheat cmd`        | cheat.sh — the manpage's useful half             |
| `timer cmd`        | hyperfine: run it enough times to mean something |
| `watch-run -- cmd` | re-run it on every file change                   |
| `cl`               | clear                                            |
| `reload`           | exec zsh, picking up a re-rendered .zshrc        |

## pipeline

Global aliases: they expand anywhere on the line, not just in front.

|       |                                       |
| ----- | ------------------------------------- |
| `G`   | \| rg                                  |
| `L`   | \| less                                |
| `D`   | \| delta — any diff on stdin, themed   |
| `H`   | \| head -20                            |
| `T`   | \| tail -20                            |
| `S`   | \| sort                                |
| `U`   | \| sort -u                             |
| `WC`  | \| wc -l                               |
| `J`   | \| jq                                  |
| `X`   | \| xargs -r                            |
| `CP`  | \| wl-copy — straight to the clipboard |
| `NOW` | an ISO timestamp, expanded in place   |
| `NE`  | 2>/dev/null                           |
| `DN`  | >/dev/null                            |
| `NUL` | both, silenced                        |

## history

Expansions the shell does before it runs the line. Type ^G to see the result first.

|            |                                                                    |
| ---------- | ------------------------------------------------------------------ |
| `!!`       | the whole previous command — `please !!` after a permission denied |
| `!$`       | its last argument                                                  |
| `!^`       | its first                                                          |
| `!*`       | all of its arguments                                               |
| `!rg`      | the last command that started with rg                              |
| `!?err`    | the last one containing err                                        |
| `^old^new` | run the previous command again, with one substitution              |
| `fc`       | reopen the last command in $EDITOR                                 |
| `r`        | run the last command again                                         |

## maintenance

```
antidote update                      # update the plugins
ansible-playbook … --tags zsh        # re-render everything here
reload                               # exec zsh
```
