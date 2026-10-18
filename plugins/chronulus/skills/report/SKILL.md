---
name: report
description: >
  How to report a problem or an idea to Chronulus, or to ask to talk to someone there,
  using the Chronulus MCP server's draft_feedback and submit_feedback tools. Use whenever
  a user wants to report a bug, an incident, a billing or cost question, a result that
  looks wrong, confusing documentation or a feature idea, or asks for a demo, a design
  partnership, a custom enterprise build or integration, or to speak with the Chronulus
  team (including investor questions). Also use to offer a report, once, after a failure
  that looks like a Chronulus problem rather than a mistake in the inputs. Covers the
  draft-then-approve flow, the report types, what evidence to attach, and what never to
  include.
---

# Reporting to Chronulus

<!-- plugin-version -->Plugin version: 0.2.12<!-- /plugin-version -->

Two tools of the Chronulus MCP server send a report to the Chronulus team: `draft_feedback`
builds a draft and sends nothing, and `submit_feedback` sends it. If either tool is missing,
say so rather than improvising another way to send the report.

## The flow: draft, show, approve, send

1. **Draft.** Call `draft_feedback` with the type and a one-line summary, plus whatever you
   know. It returns `draft` (formatted for the user), `fields` (to send), `missing` (what
   must still be added) and `next_step`.
2. **Fill the gaps.** If `missing` is not empty, ask the user for those fields, then draft
   again. Do not make them up.
3. **Show the user the draft and wait.** Show it as it is. Never send a report the user has
   not seen and approved. A report you want to make on your own initiative is an offer:
   ask first.
4. **Send.** After the user says to send it, call `submit_feedback` with the same fields and
   `approved=true`. Tell the user the reference id it returns (`FB-…` for feedback, `CT-…`
   for a request to talk to someone) so they can quote it later.

If a report is refused (for example it is over the daily limit), tell the user the reason
the tool gives. Do not retry in a loop or split one report into several to get around it.

## Pick a type

| Type | Use it when |
|---|---|
| `bug` | Something behaved wrongly. A `repro` is required. |
| `incident` | Something is failing now, or failed for a while. Say when it started and what it affects. |
| `billing` | A charge, an estimate or a balance looks wrong. `request_ids` are required. |
| `idea` | A feature or change the user would like. It is an idea, not a requirement. |
| `docs` | A tool description, a skill or a doc was unclear or wrong. Say which one. |
| `quality` | A result is in doubt: unsupported claims, wrong numbers, odd reasoning. Give the request id. |
| `demo` | The user wants a hands-on walkthrough. |
| `partnership` | The user wants to be a design partner. |
| `enterprise` | The user wants a custom build or an integration. Say what it would connect and the rough timing. |
| `investor` | An investor question. |
| `other` | The user wants to talk to someone about something else. |

The first six are feedback about the product. The last five are requests to talk to someone
at Chronulus.

## What to put in

- **Quote the user's own words** where there are words to quote, and set `source` to `user`.
  Set it to `agent` when the report is your own observation, such as an error you hit.
- **Attach evidence by id**: `request_ids`, `session_id` and `agent_id`. A request id lets
  the team look at the request itself.
- **Pass the plugin version.** Set `plugin_version` to the version at the top of this file
  (the line that starts "Plugin version"). The server adds its own version and the name of the
  client you are connected through, so don't guess those.
- **Severity** is optional: `blocked` (cannot continue), `degraded` (works, but badly) or
  `cosmetic`.
- **For a request to talk to someone**, put the user's company in `company` and when they
  would like to talk in `preferred_time` if they say. Reports go with the email of the user's
  account, so only add `contact_method` and `contact_details` if the user wants to be reached
  another way. Ask; never guess a contact detail.

## What never to include

- **The inputs of a request.** Send ids, not the content, which may be sensitive.
- **Secrets**: API keys, tokens, passwords, or anything that looks like one.
- **Personal data** of anyone but the user, and anything the user has not agreed to share.

Keep `summary` to one line and put the rest in `details`. A quick report needs only a type
and a summary; a bug also needs `repro`, and a billing report also needs `request_ids`.

## When to offer a report

- **The user asks** to report something or to talk to someone. Go straight to the draft.
- **A call fails in a way that looks like Chronulus's problem**, such as a service error
  that repeats, a result that contradicts the documentation, or a cost that does not match
  what the tool reported. Offer a report once and carry on if the user declines. Do not
  offer for the user's own mistakes (a missing field, an empty balance, a horizon over the
  limit) or for an ordinary question about how to use Chronulus; answer those instead.
- **Never file a report in the background** or without the user having seen it.
