from fastmcp import FastMCP, Context
import httpx
import os

# Initialize FastMCP server
mcp = FastMCP(name="Planio Redmine Tools")

# Configuration: Set your Plan.io URL and API key as environment variables
REDMINE_URL = os.getenv("REDMINE_URL")
API_KEY = os.getenv("REDMINE_API_KEY")

HEADERS = {
    "X-Redmine-API-Key": API_KEY,
    "Content-Type": "application/json"
}


@mcp.tool(name="get_assigned_issues", description="Retrieve issues assigned to the authenticated user")
async def get_assigned_issues(ctx: Context) -> list[dict]:
    """
    Fetches all Redmine issues assigned to the authenticated user.
    """
    url = f"{REDMINE_URL}/issues.json?assigned_to_id=me&status_id=*"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            issues = response.json().get("issues", [])

            results = []
            for issue in issues:
                results.append({
                    "id": issue["id"],
                    "subject": issue["subject"],
                    "status": issue["status"]["name"],
                    "project": issue["project"]["name"],
                    "created_on": issue["created_on"]
                })

            return results

    except Exception as e:
        await ctx.error(f"Error fetching issues: {str(e)}")
        return []


# Run the MCP server
def main():
    mcp.run()

if __name__ == "__main__":
    main()
