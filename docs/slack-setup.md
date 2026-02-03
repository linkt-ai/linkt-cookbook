# Slack MCP Setup

This guide covers setting up Slack MCP for the `/linkt-outreach` skill to post LinkedIn connection requests to a Slack channel.

## Overview

Instead of browser automation, the outreach workflow:
1. Claude drafts a personalized LinkedIn message
2. You approve the draft
3. Claude posts the details to a Slack channel
4. You manually send the connection request on LinkedIn

This approach is more reliable and keeps you in control.

## Step 1: Create a Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"**
3. Select **"From scratch"**
4. Name it (e.g., "Linkt Outreach Bot")
5. Select your workspace
6. Click **"Create App"**

## Step 2: Configure OAuth Scopes

1. In the left sidebar, click **"OAuth & Permissions"**
2. Scroll to **"Bot Token Scopes"**
3. Click **"Add an OAuth Scope"** and add:
   - `chat:write` - Send messages to channels
   - `channels:read` - List public channels

## Step 3: Install to Workspace

1. Scroll up to **"OAuth Tokens for Your Workspace"**
2. Click **"Install to Workspace"**
3. Review the permissions and click **"Allow"**
4. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)

Save this token - you'll need it for the environment variable.

## Step 4: Get Your Team ID

Option A - From browser URL:
1. Open Slack in a web browser
2. Your URL looks like: `https://app.slack.com/client/T01234567/...`
3. The `T01234567` part is your Team ID

Option B - From workspace settings:
1. Click your workspace name → **"Settings & administration"** → **"Workspace settings"**
2. Scroll down to find **"Workspace ID"**

## Step 5: Add Bot to Channel

1. Go to the Slack channel where you want outreach messages posted
2. Type `/invite @YourBotName` (replace with your bot's name)
3. The bot can now post to this channel

Recommended: Create a dedicated `#outreach` or `#linkedin-requests` channel.

## Step 6: Set Environment Variables

Add to your `.env` file in the repository root:

```bash
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_TEAM_ID=T01234567
```

## Step 7: Verify Configuration

Restart Claude Code to load the new MCP server, then verify:

```bash
# Check that Slack MCP is loaded
claude mcp list
```

You should see `slack` in the list of configured servers.

Test the connection by asking Claude: "List my Slack channels"

## Troubleshooting

### "not_in_channel" error

The bot needs to be invited to the channel before it can post:
```
/invite @YourBotName
```

### "invalid_auth" error

Check that:
1. `SLACK_BOT_TOKEN` starts with `xoxb-`
2. The token hasn't been revoked
3. You restarted Claude Code after adding the env var

### "channel_not_found" error

The channel name should not include the `#` prefix. Use `outreach` not `#outreach`.

### Bot not showing in Slack

After creating the app:
1. Make sure you clicked "Install to Workspace"
2. Check the app is enabled (not disabled) in your Slack admin

## Security Notes

1. **Keep tokens secure** - Never commit `.env` to version control
2. **Use environment variables** - The `.mcp.json` uses `${SLACK_BOT_TOKEN}` syntax
3. **Limit channel access** - Only invite the bot to channels where outreach posts should go
4. **Review before posting** - The skill always shows the draft before posting to Slack

## Message Format

When you approve an outreach draft, it posts to Slack like this:

```
📬 LinkedIn Connection Request

To: Sarah Chen (VP of Engineering) at Acme Corp
Profile: https://linkedin.com/in/sarahchen
Signal: AI Hiring - Posted 3 ML Engineer roles

Draft Message (200 char max):
> Hi Sarah, Noticed Acme is scaling the ML team - exciting times! Would love to connect and hear what you're building.

Copy the message above and send via LinkedIn.
```

You then:
1. Click the LinkedIn profile link
2. Click "Connect" → "Add a note"
3. Copy/paste the message from Slack
4. Send the connection request
