
import pathlib
import sys
import time
import requests

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

GITHUB_USER_OR_ORG = "cloudmesh-ai-luc"
BASE_URL = "https://api.github.com"

# Read token from ~/.config/github-token.txt
TOKEN_PATH = pathlib.Path.home() / ".config" / "github-token.txt"

if TOKEN_PATH.is_file():
    GITHUB_TOKEN = TOKEN_PATH.read_text().strip()
    if not GITHUB_TOKEN:
        GITHUB_TOKEN = None
else:
    GITHUB_TOKEN = None

if not GITHUB_TOKEN:
    print(
        "⚠️  No token found – collaborator information will be unavailable.",
        file=sys.stderr,
    )


# ----------------------------------------------------------------------
# Helper: generic GET with optional auth, pagination handling
# ----------------------------------------------------------------------

def gh_get(url, params=None, accept=None):
    headers = {
        "Accept": accept or "application/vnd.github+json"
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )

    # Secondary rate-limit handling
    if response.status_code == 403 and "Retry-After" in response.headers:
        wait = int(response.headers["Retry-After"])
        print(f"Rate-limited, waiting {wait}s …", file=sys.stderr)
        time.sleep(wait)

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=wait + 30,
        )

    # 401 => authentication required
    if response.status_code == 401:
        raise PermissionError(
            f"Authentication required for {url}. "
            "Provide a PAT with the required permissions."
        )

    response.raise_for_status()

    if response.status_code == 204:
        return []

    return response.json()


# ----------------------------------------------------------------------
# 1. All public repositories for the account
# ----------------------------------------------------------------------

def get_all_repos(owner):
    repos = []
    page = 1
    per_page = 100

    while True:
        url = f"{BASE_URL}/users/{owner}/repos"

        data = gh_get(
            url,
            params={
                "per_page": per_page,
                "page": page,
                "type": "owner",
            },
        )

        if not data:
            break

        repos.extend(data)

        if len(data) < per_page:
            break

        page += 1

    return repos


# ----------------------------------------------------------------------
# 2. Contributors (commit-based)
# ----------------------------------------------------------------------

def get_commit_contributors(owner, repo):
    contributors = set()
    page = 1
    per_page = 100

    while True:
        url = f"{BASE_URL}/repos/{owner}/{repo}/contributors"

        data = gh_get(
            url,
            params={
                "per_page": per_page,
                "page": page,
            },
        )

        if not data:
            break

        contributors.update(
            c["login"]
            for c in data
            if c.get("login")
        )

        if len(data) < per_page:
            break

        page += 1

    return contributors


# ----------------------------------------------------------------------
# 3. Collaborators – requires authentication
# ----------------------------------------------------------------------

def get_collaborators(owner, repo):
    if not GITHUB_TOKEN:
        return set()

    collaborators = set()
    page = 1
    per_page = 100

    while True:
        url = f"{BASE_URL}/repos/{owner}/{repo}/collaborators"

        data = gh_get(
            url,
            params={
                "per_page": per_page,
                "page": page,
                "affiliation": "outside",
            },
        )

        if not data:
            break

        collaborators.update(
            c["login"]
            for c in data
            if c.get("login")
        )

        if len(data) < per_page:
            break

        page += 1

    return collaborators


# ----------------------------------------------------------------------
# 4. Basic user profile
#    Cached so we call the API only once per login
# ----------------------------------------------------------------------

_user_cache = {}


def get_user_info(login):
    if login in _user_cache:
        return _user_cache[login]

    url = f"{BASE_URL}/users/{login}"
    data = gh_get(url)

    info = {
        "login": login,
        "name": data.get("name") or "",
        "type": data.get("type"),
        "created_at": (
            data.get("created_at", "")[:10]
            if data.get("created_at")
            else ""
        ),
        "public_repos": data.get("public_repos", 0),
    }

    _user_cache[login] = info
    return info


# ----------------------------------------------------------------------
# 5. Count public SSH keys for a user
# ----------------------------------------------------------------------

def get_ssh_key_count(login):
    url = f"{BASE_URL}/users/{login}/keys"

    try:
        keys = gh_get(url)
        return len(keys)

    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            return 0
        raise


# ----------------------------------------------------------------------
# 6. Enrich repository metadata
# ----------------------------------------------------------------------

def enrich_repo(raw):
    # Topics
    topics_url = raw["url"] + "/topics"

    topics = gh_get(
        topics_url,
        accept="application/vnd.github+json",
    )

    raw["topics"] = topics.get("names", [])

    # License name
    license_info = raw.get("license")
    raw["license_name"] = (
        license_info.get("name", "")
        if license_info
        else ""
    )

    # Keep only the fields printed later
    wanted = {
        "name",
        "html_url",
        "description",
        "stargazers_count",
        "forks_count",
        "open_issues_count",
        "language",
        "default_branch",
        "license_name",
        "topics",
    }

    return {
        key: raw.get(key)
        for key in wanted
    }


# ----------------------------------------------------------------------
# 7. Pretty-print collected data
# ----------------------------------------------------------------------

def print_report(repos):
    for repo in repos:
        print(f"\nRepo: {repo['name']}")
        print(f"  URL            : {repo['html_url']}")
        print(
            f"  Description    : "
            f"{repo.get('description') or '<none>'}"
        )
        print(
            f"  Stars / Forks / Issues : "
            f"{repo['stargazers_count']} ★  "
            f"{repo['forks_count']} ⑂  "
            f"{repo['open_issues_count']} ⚠"
        )
        print(
            f"  Language       : "
            f"{repo.get('language') or '<none>'}"
        )
        print(
            f"  Default branch : "
            f"{repo['default_branch']}"
        )

        if repo["license_name"]:
            print(f"  License        : {repo['license_name']}")

        if repo["topics"]:
            print(f"  Topics         : {', '.join(repo['topics'])}")

        # People
        committers = get_commit_contributors(
            GITHUB_USER_OR_ORG,
            repo["name"],
        )

        collaborators = get_collaborators(
            GITHUB_USER_OR_ORG,
            repo["name"],
        )

        all_people = committers | collaborators

        if not all_people:
            print("  Contributors / collaborators : <none>")
            continue

        print("  Contributors / collaborators:")

        for login in sorted(all_people):
            info = get_user_info(login)
            ssh_count = get_ssh_key_count(login)

            markers = []

            # Collaborator with no commits
            if login in collaborators and login not in committers:
                markers.append("*")

            # Has public SSH key(s)
            if ssh_count > 0:
                markers.append("🔑")

            marker_str = "".join(markers)

            print(
                f"    • {info['login']}{marker_str} "
                f"({info['type']}) – "
                f"name: {info['name'] or '<no name>'}, "
                f"created: {info['created_at']}, "
                f"public repos: {info['public_repos']}, "
                f"SSH keys: {ssh_count}"
            )

        print(
            "    * → collaborator with write access "
            "but no commits yet"
        )
        print(
            "    🔑 → user has at least one public SSH key"
        )


# ----------------------------------------------------------------------
# Main driver
# ----------------------------------------------------------------------

def main():
    print(
        f"Fetching repositories for "
        f"'{GITHUB_USER_OR_ORG}' …"
    )

    raw_repos = get_all_repos(GITHUB_USER_OR_ORG)

    if not raw_repos:
        print(
            "No repositories found "
            "(or the account does not exist)."
        )
        return

    enriched = [
        enrich_repo(repo)
        for repo in raw_repos
    ]

    print(
        f"Found {len(enriched)} public repo(s)."
    )

    print_report(enriched)


if __name__ == "__main__":
    main()

