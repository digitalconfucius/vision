---
title: New Machine Setup
tags: [infra, setup, checklist, macos, linux]
created: 2026-04-09
updated: 2026-04-09
---

# New Machine Setup

Bootstrap a fresh laptop or VPS from zero to working. Fill in your specifics under each step as you go.

## macOS laptop

1. **System**
   - [ ] Install from App Store: 1Password, Things, Obsidian (or your list)
   - [ ] Settings → Trackpad → enable tap to click
   - [ ] Settings → Keyboard → shorten key repeat, turn off caps lock mapping

2. **Homebrew**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   Typical brew bundle:
   ```
   brew install git gh zsh-autosuggestions fzf ripgrep fd bat eza starship nvim tmux
   brew install --cask iterm2 visual-studio-code rectangle raycast
   ```

3. **Dotfiles**
   - [ ] `git clone TODO://dotfiles.git ~/.dotfiles && ~/.dotfiles/install.sh`

4. **SSH**
   ```bash
   ssh-keygen -t ed25519 -C "me@host"
   gh auth login
   gh ssh-key add ~/.ssh/id_ed25519.pub
   ```
   Then populate `~/.ssh/config` with aliases — see [[infra/vps]].

5. **Tailscale**
   - [ ] `brew install --cask tailscale`
   - [ ] Sign in. See [[infra/tailscale]].

6. **Dev stacks (as needed)**
   - [ ] `brew install python@3.12 node pnpm uv`
   - [ ] `curl -fsSL https://get.docker.com | sh` or Docker Desktop

## Linux VPS

1. **Update + firewall**
   ```bash
   apt update && apt upgrade -y
   apt install -y ufw fail2ban
   ufw allow 22/tcp && ufw enable
   ```

2. **Non-root user**
   ```bash
   adduser me
   usermod -aG sudo me
   rsync -a ~/.ssh /home/me/ && chown -R me: /home/me/.ssh
   ```

3. **SSH hardening** (`/etc/ssh/sshd_config`)
   - `PermitRootLogin no`
   - `PasswordAuthentication no`

4. **Tailscale** — see [[infra/tailscale]].

5. **Cloudflared tunnel** (if exposing publicly) — see [[infra/cloudflare]].

6. **Docker**
   ```bash
   curl -fsSL https://get.docker.com | sh
   usermod -aG docker me
   ```

## Things I always forget

Tracked over in [[reference/things-i-forget]] to keep this file from turning into a junk drawer.

## Related

- [[infra/vps]]
- [[infra/tailscale]]
- [[infra/cloudflare]]
- [[reference/shortcuts]]
