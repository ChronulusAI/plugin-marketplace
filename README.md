# plugin-marketplace

The official plugin marketplace for [Chronulus AI](https://chronulus.com): plugins and
skills for building with the Chronulus forecasting and prediction platform. It supports
both [Claude Code](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces) and
[OpenAI Codex](https://developers.openai.com/plugins/build/plugins), so the same plugins
install in either one. The plugin's interactive scorecards and other UIs are built for
the Claude.ai and ChatGPT web apps as well, so it also works there.

## Installation

### Claude Code

Add this marketplace in Claude Code, then install whichever plugins you want:

```
/plugin marketplace add ChronulusAI/plugin-marketplace
/plugin install <plugin-name>
```

Or browse and install interactively:

```
/plugin marketplace add ChronulusAI/plugin-marketplace
/plugin
```

### OpenAI Codex

Add this marketplace from your terminal, then install `ChronulusAI/plugin-marketplace` from the Plugins
directory in Codex:

```
codex plugin marketplace add ChronulusAI/plugin-marketplace
```

If you get `unexpected argument 'marketplace'`, your executable does not expose
this command. Update Codex using the package manager you installed it with (for an
npm installation, `npm install -g @openai/codex@latest`), then check again. Use
`type -a codex` to check whether another installation is taking precedence on PATH.


## Available plugins

| Plugin | Description |
| --- | --- |
| [`chronulus`](plugins/chronulus) | Skills for the Chronulus MCP server: build reusable, de-biased probability predictors for prediction-market questions across sports, elections, politics, culture, crypto, commodities, climate, economics, mentions, finance and tech & science (`predict`), and produce time-series forecasts with the NormalizedForecaster (`forecast`). |

Most plugins here bundle a connection to the hosted Chronulus MCP server at
`https://mcp.chronulus.com/mcp`. Installing a plugin is
enough to wire it up, and you'll be prompted to sign in via OAuth on first use.

## Repository structure

```
plugin-marketplace/
├── .claude-plugin/
│   └── marketplace.json      # Claude Code marketplace manifest listing every plugin below
├── .agents/
│   └── plugins/
│       └── marketplace.json  # Codex marketplace manifest listing every plugin below
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/
        │   └── plugin.json   # Claude Code plugin manifest
        ├── plugin.json        # Codex plugin manifest
        ├── .mcp.json          # MCP servers for Claude Code (optional)
        ├── mcp.json           # MCP servers for Codex (optional)
        ├── skills/            # Agent skills (optional)
        ├── commands/          # Slash commands (optional)
        ├── agents/            # Subagents (optional)
        └── README.md
```

Each plugin is self-contained and independently installable. New Chronulus plugins and
skills are added under `plugins/` and registered in both `.claude-plugin/marketplace.json`
and `.agents/plugins/marketplace.json`.

## Contributing

To add a new plugin:

1. Create `plugins/<plugin-name>/` with a `.claude-plugin/plugin.json` manifest (and a
   `plugin.json` for Codex) and whatever components it needs (`skills/`, `commands/`,
   `agents/`, `hooks/`, `.mcp.json` / `mcp.json`).
2. Add an entry for it to the `plugins` array in both `.claude-plugin/marketplace.json`
   and `.agents/plugins/marketplace.json`.
3. Give it its own `README.md` documenting what it does and any prerequisites.

## License

[MIT](LICENSE)
