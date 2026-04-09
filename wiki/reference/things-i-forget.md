---
title: Things I Forget
tags: [reference, gotchas, cheatsheet]
created: 2026-04-09
updated: 2026-04-09
---

# Things I Forget

Junk drawer of one-liners, gotchas, and small facts I look up over and over. Keep entries short. If something grows beyond a paragraph, promote it to its own page.

## Shell

- `!!` — previous command; `sudo !!` is the classic
- `!$` — last argument of previous command
- `^old^new` — re-run previous command replacing `old` with `new`
- `cd -` — previous directory
- `Ctrl-R` — reverse history search

## Networking

- `curl -v` shows request+response headers; `-I` is head-only
- `dig +short domain.tld` — quick DNS
- `dig @1.1.1.1 domain.tld` — bypass local resolver
- `ss -tulpn` — listening sockets on linux (modern `netstat`)
- `lsof -i :PORT` — what's on that port

## Docker

- `docker system prune -af --volumes` — reclaim disk (careful)
- `docker logs -f --tail 100 <name>` — tail logs
- `docker compose exec svc sh` — shell into a running service
- `docker context` — switch between local and ssh hosts

## macOS quirks

- Clear DNS cache: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
- Show hidden files in Finder: `⌘ ⇧ .`
- Reset icon cache: `killall Dock`

## Python

- `python -m venv .venv && source .venv/bin/activate`
- `uv pip install -r requirements.txt` — faster than pip
- `python -m http.server 8000` — serve current dir

## Git moments

- Accidental commit to wrong branch: `git reset HEAD~1; git stash; git switch right-branch; git stash pop`
- Recover "lost" work: `git reflog` → `git checkout <sha>`
- Fix author on the last commit: `git commit --amend --reset-author --no-edit`

## Related

- [[reference/shortcuts]]
- [[infra/new-machine-setup]]
