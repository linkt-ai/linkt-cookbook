# Linkt Cookbook

Use direct HTTP requests or selected MCP tools with Signal V2. No client SDK is required.

## Run a bounded HTTP example

Python 3.10 or later is sufficient. Create `.env` in this repository root with `LINKT_API_KEY` from your organization.
Keep the file private. The runner loads it without overriding existing environment variables.

```sh
python3 v2/run.py list-campaigns
python3 v2/run.py list-accounts
python3 v2/run.py list-people
python3 v2/run.py list-signals
python3 v2/run.py list-runs
```

Each command reads one page of at most five records. It does not start discovery or paid workers.
Set `LINKT_API_ENVIRONMENT=staging` for staging credentials. The default is production.
The runner rejects a `LINKT_API_URL` that differs from the selected environment.

Read the [V2 workflows](v2/README.md) for campaign creation, membership, monitors, runs, and MCP authentication.

## Legacy V1

The [Python SDK examples](python/README.md) and existing customer skills target deprecated V1 interfaces.
Their paths remain available for existing integrations. Existing package versions remain installable.
The root `.mcp.json` remains a labelled legacy configuration for those skills.
New V2 MCP sessions use the separate configuration in [v2/mcp.json](v2/mcp.json).
Do not load both configurations under the same server name.

See [legacy skills](docs/skills-overview.md) and [Slack setup](docs/slack-setup.md) for existing workflows.

## Qualification

`v2/examples.json` is copied from the backend candidate bundle. `v2/source.json` records its exact source and digest.
The Signal wrapper validates this copy against the candidate HTTP and MCP contracts.
Backend fixture tests execute those same definitions through real HTTP routes and MCP tools without paid workers.
Local runner tests check request construction, environment isolation, redirects, timeouts, and mutation admission:

```sh
python3 -m unittest discover -s tests -v
```

## License

MIT
