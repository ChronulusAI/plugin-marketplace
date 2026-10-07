# plugin-marketplace

The official [Claude Code plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
for [Chronulus AI](https://chronulus.com) — Claude Code plugins and skills for
building with the Chronulus forecasting and prediction platform. It also works as an
[OpenAI Codex plugin marketplace](https://developers.openai.com/plugins/build/plugins), so
the same plugins install in Codex.

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

Use a Codex CLI build that supports plugin marketplaces. Check your installation:

```bash
codex --version
codex plugin marketplace --help
```

The marketplace command is supported by the locally checked `codex-cli 0.159.3`.
If you get `unexpected argument 'marketplace'`, your executable does not expose
this command. Update Codex using the package manager you installed it with (for an
npm installation, `npm install -g @openai/codex@latest`), then check again. Use
`type -a codex` to check whether another installation is taking precedence on PATH.

Add this marketplace from your terminal, then install `chronulus` from the Plugins
directory in Codex:

```
codex plugin marketplace add ChronulusAI/plugin-marketplace
```

To test the Codex compatibility branch before it is merged:

```bash
codex plugin marketplace add ChronulusAI/plugin-marketplace --ref feat/openai-codex-plugin
```

Alternatively, register your current checkout from the repository root:

```bash
codex plugin marketplace add .
```

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
