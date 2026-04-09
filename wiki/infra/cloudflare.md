---
title: Cloudflare
tags: [infra, cloudflare, dns, tunnels]
created: 2026-04-09
updated: 2026-04-09
---

# Cloudflare

DNS, tunnels, workers, and edge caching. The public-facing complement to [[infra/tailscale]] (which handles the private side).

> **No secrets in this file.** API token name: `CLOUDFLARE_API_TOKEN` (value in password manager). Account ID and zone IDs are OK to write down — they aren't secret.

## Zones

| Domain | Zone ID | Registrar | Notes |
|--------|---------|-----------|-------|
| _TODO_ | | | |

## Tunnels (cloudflared)

| Tunnel name | Target VPS | Hostname(s) | Service |
|-------------|-----------|-------------|---------|
| _TODO_ | [[infra/vps]] alias | `sub.domain.tld` | `http://localhost:8080` |

### Set up a tunnel on a VPS

```bash
cloudflared tunnel login
cloudflared tunnel create <name>
cloudflared tunnel route dns <name> sub.domain.tld
# Create /etc/cloudflared/config.yml then:
cloudflared tunnel run <name>
```

## Workers

| Worker | Route | What it does |
|--------|-------|--------------|
| _TODO_ | | |

## Quirks

- DNS changes can take a minute to propagate even on orange-cloud records.
- Tunnels can silently rebind if you recreate them with the same name — if a route stops working, check `cloudflared tunnel list` for dupes.
- To bypass the cache during debug, append `?cf-nocache=1` or disable via page rules.

## Related

- [[infra/vps]]
- [[infra/tailscale]]
