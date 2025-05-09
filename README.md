# MCP Enabled Plan.IO (Redmine) Reader
Model Context Protocol (MCP) server exposes a set of tools to read and search plan.io issues. This has been tested on Claude Desktop. 

## Installation

### Prerequisites

#### Windows
1. Install Claude Desktop (or another MCP-enabled AI tool)
   - Download [Claude for Desktop](https://claude.ai/download) 
   - Follow the current installation instructions: [Installing Claude Desktop](https://support.anthropic.com/en/articles/10065433-installing-claude-for-desktop)
     
2. Install Python 3.10 or higher:
   - Download the latest Python installer from [python.org](https://python.org)
   - Run the installer, checking "Add Python to PATH"
   - Open Command Prompt and verify installation with `python --version`

3. Install uv:
   - Open Command Prompt as Administrator
   - Run `pip install --user uv`
   - Verify installation with `uv --version`

#### macOS
1. Install Claude Desktop (or another MCP-enabled AI tool)
   - Download [Claude for Desktop](https://claude.ai/download) 
   - Follow the current installation instructions: [Installing Claude Desktop](https://support.anthropic.com/en/articles/10065433-installing-claude-for-desktop)
     
2. Install Python 3.10 or higher:
   - Using Homebrew: `brew install python`
   - Verify installation with `python3 --version`

3. Install uv:
   - Using Homebrew: `brew install uv`
   - Alternatively: `pip3 install --user uv`
   - Verify installation with `uv --version`

## Configuration

Add the following to your `claude_desktop_config.json`:

```json
{
		"mcp_planio": {
			"command": "uvx",
			"args": [
				"--from",
				"git+https://github.com/karateboss/mcp_planio@main",
				"mcp_planio"
			],
			"env": {
				"REDMINE_URL": "https://<your plan.io>",
				"REDMINE_API_KEY": "<your api key>"
			}
    }
}
```
