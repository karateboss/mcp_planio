from mcp.server.fastmcp import FastMCP
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
async def get_assigned_issues() -> list[dict]:
    """
    Fetches all Redmine issues assigned to the authenticated user.
    """
    url = f"{REDMINE_URL}/issues.json?assigned_to_id=me&status_id=*"

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

@mcp.tool(name="get_issue_details", description="Retrieve the full body and metadata of a specific Redmine issue by ID")
async def get_issue_details(issue_id: int) -> dict:
    """
    Fetches the full description and metadata of a single issue by its ID.
    """
    url = f"{REDMINE_URL}/issues/{issue_id}.json?include=journals"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        issue = response.json().get("issue", {})

        return {
            "id": issue.get("id"),
            "subject": issue.get("subject"),
            "description": issue.get("description"),
            "status": issue.get("status", {}).get("name"),
            "priority": issue.get("priority", {}).get("name"),
            "project": issue.get("project", {}).get("name"),
            "author": issue.get("author", {}).get("name"),
            "created_on": issue.get("created_on"),
            "updated_on": issue.get("updated_on")
        }

# Run the MCP server
def main():
    mcp.run()

if __name__ == "__main__":
    main()
