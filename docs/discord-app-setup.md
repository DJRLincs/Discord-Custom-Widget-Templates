# Discord App Setup Checklist

Use this checklist before running the sync workflow.

## 0) JSON import tools

You can import the template JSON with either option:

- The extension in `Discord-Widgets-Extension-main`
- TheCreativeGod extension: [TheCreativeGod/Discord-Widgets-Extension](https://github.com/TheCreativeGod/Discord-Widgets-Extension)

## 1) Create or open your Discord application

1. Open Discord Developer Portal.
2. Create a new application or open your existing Discord application.
3. Copy the Application ID and store it as your `DISCORD_APP_ID` secret.

## 2) Configure required General Information values

Set these required fields in the app page:

- Application name
- Homepage URL
- Description
- Authorization callback URL

They can be placeholders, but must be valid values.

## 3) Enable device flow

In General Information, enable:

- Enable Device Flow

## 4) Create or rotate bot token

1. Open the Bot tab.
2. Generate or reset token.
3. Store it as `DISCORD_BOT_TOKEN` in GitHub Actions secrets.

## 5) Get your Discord user ID

1. Enable Developer Mode in Discord settings.
2. Copy your user ID.
3. Store it as `DISCORD_USER_ID` in GitHub Actions secrets.

## 6) Repository secrets

In your repository settings, add these Actions secrets:

- `DISCORD_BOT_TOKEN`
- `DISCORD_APP_ID`
- `DISCORD_USER_ID`

## 7) Publish the widget

After importing your JSON template through the extension and setting fields, publish the widget in the Developer Portal. If not published, other users may not see updates.
