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
    Fetches the full description, metadata, and all comments/journals of a single issue by its ID.
    """
    url = f"{REDMINE_URL}/issues/{issue_id}.json?include=journals,relations,attachments,watchers,children"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        issue = response.json().get("issue", {})
        
        # Extract journals (comments and updates)
        journals = []
        for journal in issue.get("journals", []):
            journal_data = {
                "id": journal.get("id"),
                "user": journal.get("user", {}).get("name"),
                "created_on": journal.get("created_on"),
                "notes": journal.get("notes", ""),
                "details": journal.get("details", [])
            }
            journals.append(journal_data)
        
        # Extract attachments
        attachments = []
        for attachment in issue.get("attachments", []):
            attachment_data = {
                "id": attachment.get("id"),
                "filename": attachment.get("filename"),
                "filesize": attachment.get("filesize"),
                "content_type": attachment.get("content_type"),
                "author": attachment.get("author", {}).get("name"),
                "created_on": attachment.get("created_on"),
                "description": attachment.get("description", "")
            }
            attachments.append(attachment_data)
        
        # Extract custom fields
        custom_fields = {}
        for field in issue.get("custom_fields", []):
            custom_fields[field.get("name")] = field.get("value")
        
        # Extract related issues
        relations = []
        for relation in issue.get("relations", []):
            relation_data = {
                "id": relation.get("id"),
                "issue_id": relation.get("issue_id"),
                "issue_to_id": relation.get("issue_to_id"),
                "relation_type": relation.get("relation_type"),
                "delay": relation.get("delay")
            }
            relations.append(relation_data)
        
        # Build comprehensive issue data
        return {
            "id": issue.get("id"),
            "subject": issue.get("subject"),
            "description": issue.get("description"),
            "status": issue.get("status", {}).get("name"),
            "priority": issue.get("priority", {}).get("name"),
            "project": issue.get("project", {}).get("name"),
            "tracker": issue.get("tracker", {}).get("name"),
            "author": issue.get("author", {}).get("name"),
            "assigned_to": issue.get("assigned_to", {}).get("name") if "assigned_to" in issue else None,
            "category": issue.get("category", {}).get("name") if "category" in issue else None,
            "fixed_version": issue.get("fixed_version", {}).get("name") if "fixed_version" in issue else None,
            "parent": issue.get("parent", {}).get("id") if "parent" in issue else None,
            "start_date": issue.get("start_date"),
            "due_date": issue.get("due_date"),
            "done_ratio": issue.get("done_ratio"),
            "estimated_hours": issue.get("estimated_hours"),
            "spent_hours": issue.get("spent_hours"),
            "created_on": issue.get("created_on"),
            "updated_on": issue.get("updated_on"),
            "closed_on": issue.get("closed_on"),
            "journals": journals,
            "attachments": attachments,
            "custom_fields": custom_fields,
            "relations": relations,
            "watchers": issue.get("watchers", []),
            "children": issue.get("children", [])
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
    description="Retrieve the total number of hours booked to a Redmine issue, handling pagination"
)
async def get_issue_hours_booked(issue_id: int) -> dict:
    """
    Retrieves and sums all time entries for a given issue ID using pagination.
    """
    base_url = f"{REDMINE_URL}/time_entries.json"
    limit = 100
    offset = 0
    total_hours = 0.0
    total_entries = 0

    async with httpx.AsyncClient() as client:
        while True:
            url = f"{base_url}?issue_id={issue_id}&limit={limit}&offset={offset}"
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()

            data = response.json()
            entries = data.get("time_entries", [])
            total_count = data.get("total_count", 0)

            total_hours += sum(entry.get("hours", 0) for entry in entries)
            total_entries += len(entries)

            offset += limit
            if offset >= total_count:
                break

        return {
            "issue_id": issue_id,
            "total_hours": total_hours,
            "entries_count": total_entries
        }


# Run the MCP server
def main():
    mcp.run()

if __name__ == "__main__":
    main()
