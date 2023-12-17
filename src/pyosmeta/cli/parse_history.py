"""Parse local commit history.

This is a script that only needs to be run once.

The script performs the following:

1. gets a list of all contributors
2. parses through the commit history (locally) to figure out when they
   were added to the `contributor.yml` file
3. then it adds a date_Added key for that person

This will allow us to ensure the yaml file retains order when users are
highlighted as "new" and also for diff's in git.

"""

import os
import pickle

import git

from pyosmeta.file_io import open_yml_file


def main():
    """Parse repo history for contributor metadata"""
    base_url = "https://raw.githubusercontent.com/pyOpenSci/"
    web_yaml_path = base_url + "pyopensci.github.io/main/_data/contributors.yml"

    web_contribs = open_yml_file(web_yaml_path)

    def find_name(search_name: str, contributors) -> str:
        """Find a name in a collection of contributors"""
        for contributor in contributors:
            if search_name.lower() in contributor["name"].lower():
                return contributor["github_username"]

    repo_path = os.path.join("/Users/leahawasser/Documents/GitHub/pyos/", "pyopensci.github.io")

    file_path = os.path.join("_data", "contributors.yml")

    if not os.path.isfile(os.path.join(repo_path, file_path)):
        raise ValueError
        # 'The file {file_path} does not exist in the repository.'

    repo = git.Repo(repo_path)
    all_commits = list(repo.iter_commits("main", paths=file_path))
    all_rev = reversed(all_commits)

    # One time fix for ppl with missing gh usernames early on
    contrib_dates = {}
    for commit in all_rev:
        commit_date = commit.committed_datetime

        # Extract the content of the file at the specific commit date
        blob = repo.git.show(f"{commit}: {file_path}")
        file_contents = blob.splitlines()
        # Parse through each line and find github_username, add it to list
        # username:date
        for line in file_contents:
            if " name:" in line:
                name = line.split(":")[1].strip().lower()

            if "github_username:" in line:
                gh_user = line.split(":")[1].strip().lower()
                # TODO confusing
                if not gh_user:
                    gh_user = find_name(name, web_contribs)
                elif gh_user not in contrib_dates.keys():
                    contrib_dates[gh_user] = commit_date.strftime("%Y-%m-%d")
                continue

    # Export to pickle which supports updates after parsing reviews
    with open("contrib_dates.pickle", "wb") as f:
        pickle.dump(contrib_dates, f)


if __name__ == "__main__":
    main()
