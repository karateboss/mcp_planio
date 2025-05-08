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

@mcp.tool(name="search_issues_by_assignee", description="Search Redmine issues assigned to a user by login or ID")
async def search_issues_by_assignee(username: str = "", user_id: int = None) -> list[dict]:
    async with httpx.AsyncClient() as client:
        if user_id is None:
            users_url = f"{REDMINE_URL}/users.json?name={username}"
            user_resp = await client.get(users_url, headers=HEADERS)
            user_resp.raise_for_status()
            users = user_resp.json().get("users", [])
            if not users:
                return [{"error": f"No user found for '{username}'"}]
            user_id = users[0]["id"]

        issues_url = f"{REDMINE_URL}/issues.json?assigned_to_id={user_id}&status_id=*"
        issue_resp = await client.get(issues_url, headers=HEADERS)
        issue_resp.raise_for_status()
        issues = issue_resp.json().get("issues", [])

        return [{
            "id": i["id"],
            "subject": i["subject"],
            "status": i["status"]["name"],
            "project": i["project"]["name"],
            "created_on": i["created_on"]
        } for i in issues]


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

@mcp.tool(name="search_issues_by_keyword", description="Search for issues across all projects using a keyword")
async def search_issues_by_keyword(keyword: str) -> list[dict]:
    """
    Performs a full-text search across all accessible issues in all projects.
    """
    search_url = f"{REDMINE_URL}/search.json?q={keyword}&scope=all&all_words=1&issues=1"

    async with httpx.AsyncClient() as client:
        response = await client.get(search_url, headers=HEADERS)
        response.raise_for_status()
        results = response.json().get("results", [])

        # Filter only "issue" results (Redmine returns wiki, docs, etc. too)
        issues = [r for r in results if r.get("type") == "issue"]

        return [
            {
                "id": i["id"],
                "title": i["title"],
                "description": i.get("description", ""),
                "url": i["url"],
                "project": i.get("project", {}).get("name")
            }
            for i in issues
        ]
        
@mcp.tool(
    name="get_issue_hours_booked",
    description="Retrieve the total number of hours booked to a Redmine issue"
)
async def get_issue_hours_booked(issue_id: int) -> dict:
    """
    Retrieves and sums time entries for a given issue ID.
    """
    url = f"{REDMINE_URL}/time_entries.json?issue_id={issue_id}&limit=100"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        entries = response.json().get("time_entries", [])

        total_hours = sum(entry.get("hours", 0) for entry in entries)

        return {
            "issue_id": issue_id,
            "total_hours": total_hours,
            "entries_count": len(entries)
        }


# Run the MCP server
def main():
    mcp.run()

if __name__ == "__main__":
    main()
