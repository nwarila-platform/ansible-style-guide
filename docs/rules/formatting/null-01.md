---
id: "NULL-01"
title: "NULL-01"
sidebar_label: "NULL-01"
sidebar_position: 6
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/null_01.py` over the generated metadata; the `defaults` comment is `review`."
---

**NULL-01** `auto*`/`review` — Spelled `null`; never `~` or `Null`. **Never written as a substitute
for omitting an option** — ARG-01 omits null-defaulted options instead. Legitimate in `defaults` to
declare "no value — the product's own default applies", with a comment naming what the null means, and
as a module argument **only where the generated toolchain metadata records null as an explicit clear**
(e.g. `microsoft.ad.user`'s `adminCount: null`).
**Why:** the blanket ban was wrong against a documented clear.
**Checked by:** a new `rolecheck/lint/rules/null_01.py` over the generated metadata; the `defaults`
comment is `review`.

