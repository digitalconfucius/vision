---
title: VPS
tags: [infra, vps, ssh]
created: 2026-04-09
updated: 2026-04-09
---

# VPS

Every VPS I'm running or paying for. Cross-reference with [[infra/tailscale]] for tailnet names and [[infra/cloudflare]] for public hostnames.

> **No secrets in this file.** IPs are OK. SSH keys, passwords, and tokens live in the password manager.

## Inventory

| Name | Provider | Region | Purpose | Tailnet | Public hostname | SSH alias |
|------|----------|--------|---------|---------|-----------------|-----------|
| _TODO_ | Hetzner / DigitalOcean / … | | | `[[infra/tailscale]]` name | via [[infra/cloudflare]] | `ssh name` |

## SSH config

The `~/.ssh/config` aliases that make all of this usable live in [[infra/new-machine-setup]]. Each VPS should have a block like:

```
Host alias
    HostName 1.2.3.4
    User root
    IdentityFile ~/.ssh/id_ed25519
```

## Common commands

```bash
# Copy a local file to a VPS
scp local.txt alias:~/remote.txt

# Quick port forward
ssh -L 8080:localhost:8080 alias

# Docker compose from local
DOCKER_HOST=ssh://alias docker compose up -d
```

## Related

- [[infra/tailscale]] — how these machines talk to each other privately
- [[infra/cloudflare]] — how these machines are exposed to the internet
- [[infra/new-machine-setup]] — how to onboard a new VPS
- [[reference/things-i-forget]] — quirks and one-liners
