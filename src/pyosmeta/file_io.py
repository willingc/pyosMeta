"""File I/O Utilities"""
import pickle
import urllib.error
import urllib.request

import ruamel.yaml
from ruamel.yaml import YAML
from typing import Dict


def load_pickle(filename):
    """Opens a pickle and return its contents"""
    with open(filename, "rb") as f:
        return pickle.load(f)


def _list_to_dict(source, a_key: str) -> Dict:
    """Takes a yaml file opened and turns into a dictionary
    The dict structure is key (gh_username) and then a dictionary
    containing all information for the username

    source :
        A list of dictionary objects returned from load website yaml
    a_key : str
        A string representing the dict key to use as the main key to call
        each sub dict in the object.

    """

    return {a_dict[a_key].lower(): a_dict for a_dict in source}


def create_paths() -> list[str] | str:
    """Create paths by composing URLs and repos"""
    base_url = "https://raw.githubusercontent.com/pyOpenSci/"
    end_url = "/main/.all-contributorsrc"
    repos = [
        "python-package-guide",
        "software-peer-review",
        "pyopensci.github.io",
        "software-review",
        "update-web-metadata",
    ]

    # Compose paths for all of the repos
    all_paths = [base_url + repo + end_url for repo in repos]

    return all_paths


def load_website_yml(key: str, url: str):
    """
    This opens a website contrib yaml file and turns it in a
    dictionary
    """
    contributors = open_yml_file(url)

    return _list_to_dict(contributors, key)


def open_yml_file(file_path: str) -> Dict:
    """Open & deserialize YAML file to dictionary.

    Parameters
    ----------
    file_path : str
        Path to the YAML file to be opened.

    Returns
    -------
        Dictionary containing the structured data in the YAML file.
    """
    try:
        with urllib.request.urlopen(file_path) as f:
            yaml = YAML(typ="safe", pure=True)
            return yaml.load(f)
    except urllib.error.URLError as url_error:
        print("Oops - can find the url", file_path, url_error)


def export_yaml(filename: str, data):
    """Update website contrib file with the information grabbed from GitHub
    API

    Serialize contrib data from dictionary to YAML file.

    Parameters
    ----------

    filename : str
        Name of the output contributor filename ().yml format)
    data :
        Contributor data for the website.

    Returns
    -------
    """

    with open(filename, "w") as file:
        # Create YAML object with RoundTripDumper to keep key order intact
        yaml = ruamel.yaml.YAML(typ="rt")
        yaml.default_flow_style = False
        # Set the indent parameter to 2 for the yaml output
        yaml.indent(mapping=4, sequence=4, offset=2)
        yaml.dump(data, file)


def clean_string(source: str) -> str:
    """Clean - remove strings starting with "*id0" and "[]".

    Parameters
    ----------
    source : str
        The string to be cleaned.

    Returns
    -------
    str
        The cleaned string.

    Examples
    --------
    >>> input_string = "packages-submitted: &id003 []"
    >>> clean_string(input_string)
    "packages-submitted: []"

    """
    patterns = ["*id001", "*id002", "*id003", "*id004"]
    for pattern in patterns:
        source = source.replace(pattern, "")
    return source.replace("[]", "")


def clean_yaml_file(filename):
    """Open a yaml file and remove extra indents and spacing"""
    with open(filename, "r") as f:
        lines = f.readlines()

    fix_indent = False
    cleaned_lines = []
    for i, line in enumerate(lines):
        if i == 0 and line.startswith("  "):
            # check for 2 spaces in the first line
            fix_indent = True
        if fix_indent:
            line = line.replace("  ", "", 1)
        line = clean_string(line)
        cleaned_lines.append(line)

    cleaned_text = "".join(cleaned_lines).replace("''", "")

    with open(filename, "w") as f:
        f.write(cleaned_text)


def clean_export_yml(source, filename: str) -> None:
    """Inputs a dictionary with keys - contribs or packages.
    It then converse to a list for export, and creates a cleaned
    YAML file that is jekyll friendly

    Parameters
    ----------
    source : Dict
        A collection of pyos metadata information
    filename : str
        Name of the YML file to export

    Returns
    -------
    None
        Outputs a yaml file with the input name containing the pyos meta
    """

    # Export to yaml
    export_yaml(filename, source)
    clean_yaml_file(filename)
