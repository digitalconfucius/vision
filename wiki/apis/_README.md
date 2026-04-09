---
title: APIs
tags: [apis, meta]
created: 2026-04-09
updated: 2026-04-09
---

# APIs

Reference hub for every API I interact with. One page per service as needed. **Never write actual keys** — just the variable name (e.g. `OPENAI_API_KEY`) and where the real value lives (password manager, `.env`).

## Services

_Create pages here as you start using APIs. Examples of what each page should include:_

- **Name + URL** to the docs
- **Auth** — env var name, token type, where rotation happens
- **Base URL** and primary endpoints
- **Rate limits** and quirks
- **Gotchas** — versioning, retry strategies, tokenizer oddities

## Template

```markdown
---
title: ServiceName
tags: [apis, servicename]
---

# ServiceName

> One-line summary.

## Auth
- Env var: `SERVICENAME_API_KEY`
- Rotation: TODO

## Endpoints
- Base: `https://api.servicename.com/v1`
- ...

## Quirks
- ...
```

## Related

- [[reference/things-i-forget]] — for the "wait which header was it?" moments
