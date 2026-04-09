---
title: Tailscale
tags: [infra, tailscale, network, vpn]
created: 2026-04-09
updated: 2026-04-09
---

# Tailscale

Personal tailnet for zero-config private networking between [[infra/vps]] machines, laptops, and phones.

## Tailnet

- Tailnet name: `TODO`
- Admin console: <https://login.tailscale.com/admin/machines>

## Machines

| Hostname | Tailnet IP | OS | Role | VPS entry |
|----------|-----------|-----|------|-----------|
| _TODO_   | 100.x.x.x | linux/macos | | [[infra/vps]] |

## Bring up a new machine

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh --accept-routes
```

- Use `--ssh` to replace `sshd` auth with tailnet identity on servers.
- Use `--accept-routes` if another machine is advertising subnets.

## Common commands

```bash
tailscale status
tailscale ping hostname
tailscale ssh hostname
tailscale serve https / http://localhost:3000   # expose a local port on tailnet
tailscale funnel 3000                            # expose publicly via Tailscale edge
```

## ACL notes

ACL file lives in the admin console. Keep a copy in this repo under `wiki/infra/tailscale-acl.hujson` when/if you start customizing.

## Related

- [[infra/vps]]
- [[infra/new-machine-setup]]
- [[infra/cloudflare]] — the other side of the network story (public edge)
