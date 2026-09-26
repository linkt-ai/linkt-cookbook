# V2 HTTP and MCP workflows

These examples use campaigns, accounts, people, campaign membership, signals, monitors, and runs.
See the [HTTP reference](https://docs.linkt.ai/api-reference/) for the complete contract.

## Authentication and environments

HTTP requests send an organization API key in `x-api-key`. Private web tokens do not replace that key.
Production uses `https://api.linkt.ai`; staging uses `https://api-staging.linkt.ai` with separate credentials.
The Python runner reads `LINKT_API_KEY` and `LINKT_API_ENVIRONMENT` from the root `.env` or process environment.
It sends one request with a 15-second timeout. It rejects redirects and does not retry mutations.

## Campaigns

Read existing campaigns with `python3 v2/run.py list-campaigns`.
Create a campaign only when you intend to change your organization:

```sh
python3 v2/run.py create-campaign --allow-write
```

This example creates an empty campaign with company and person entity types.
Creating a campaign does not submit discovery. The response contains the campaign identifier.

## Accounts and people

Use `list-accounts` and `list-people` to inspect existing organization records.
Pagination responses contain `data` and `next_cursor`.
The examples read one page with `limit=5`; they do not automatically drain the collection.
A null `next_cursor` means there is no next page.

## Membership

Set `CAMPAIGN_ID` and `ACCOUNT_ID` to real UUIDs from your organization.
Then run `python3 v2/run.py add-account --allow-write`.
The runner replaces catalog fixture IDs with those values. It rejects missing or invalid IDs.
Adding an account associates an existing account with the campaign. It does not discover a new account.

## Signals

Run `python3 v2/run.py list-signals` to read existing signal events.
The response uses the V2 signal model. Do not assume that V1 entity fields or filter names apply.

## Monitors

Set `CAMPAIGN_ID`, then run `python3 v2/run.py list-monitors`.
Monitor configuration is available through HTTP. The selected MCP inventory does not expose every monitor operation.
Read the current HTTP reference before creating or changing a monitor. Scheduled work can consume paid capacity.

## Runs

Run `python3 v2/run.py list-runs` to inspect existing runs.
The example does not start or cancel work. Submission can enqueue paid research.
Cancellation can race execution and is not a method for making a smoke test free.

## MCP setup

Connect an HTTP MCP client to `https://api.linkt.ai/v2/mcp`.
Use `https://api-staging.linkt.ai/v2/mcp` for staging and sign in to the same environment.
The configuration in [mcp.json](mcp.json) targets production.

MCP uses OAuth authorization code flow with PKCE S256 and the `signal:user` scope.
Let the client discover authorization metadata and open the sign-in flow.
An organization API key is for HTTP requests; do not copy the legacy `x-api-key` configuration into V2 MCP.
Never paste private web tokens into the MCP configuration.

Ask the connected client to list tools before a workflow. Selected examples include:

| Resource | Tool | Bounded initial arguments |
|---|---|---|
| Campaigns | `list_campaigns` | `{"limit":5}` |
| Accounts | `search_accounts` | `{"limit":5}` |
| People | `search_people` | `{"limit":5}` |
| Signals | `list_signals` | `{"limit":5}` |
| Runs | `list_runs` | `{"limit":5}` |

`create_campaign` and `add_accounts_to_campaign` change data and need user intent for that change.
The catalog records their input shapes. Replace fixture UUIDs with organization IDs before use.
MCP covers selected operations; the HTTP reference remains the source for unsupported tools.

## Legacy migration

V1 SDKs, entity filters, and legacy MCP tool names are not the V2 interface.
Existing V1 example paths remain in the repository with Legacy V1 labels.
Migrate one workflow at a time and verify identifiers, authentication, and response shapes.
