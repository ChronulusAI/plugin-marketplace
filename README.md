# plugin-marketplace

The official [Claude Code plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
for [Chronulus AI](https://chronulus.com) — Claude Code plugins and skills for
building with the Chronulus forecasting and prediction platform.

## Installation

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
│   └── marketplace.json      # Marketplace manifest listing every plugin below
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/
        │   └── plugin.json   # Plugin manifest
        ├── skills/            # Agent skills (optional)
        ├── commands/          # Slash commands (optional)
        ├── agents/            # Subagents (optional)
        └── README.md
```

Each plugin is self-contained and independently installable. New Chronulus plugins and
skills are added under `plugins/` and registered in `.claude-plugin/marketplace.json`.

## Contributing

To add a new plugin:

1. Create `plugins/<plugin-name>/` with a `.claude-plugin/plugin.json` manifest and
   whatever components it needs (`skills/`, `commands/`, `agents/`, `hooks/`,
   `.mcp.json`).
2. Add an entry for it to the `plugins` array in `.claude-plugin/marketplace.json`.
3. Give it its own `README.md` documenting what it does and any prerequisites.

## License

[MIT](LICENSE)
