#! /usr/bin/python3

import os, argparse
import re, json, psycopg2

localhost_password = os.environ.get("PSQL_Password") or 'postgres'

db_credentials = {
    "dbname": "packages_production",
    "user": "postgres", # Default User
    "password": localhost_password, 
    "host": "localhost",
    "port": "5432"  # Default PostgreSQL port
}

unique_urls = set()

def get_total_package_count(ecosystem : str) -> int:
    """
    Retrieves the total count of packages for a given ecosystem.

    Parameters:
    - ecosystem (str): Ecosystem Name.

    Returns:
    - total_count (int): Total package count for specified ecosystem.
    """

    conn = psycopg2.connect(**db_credentials)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM packages WHERE ecosystem = %s;", (ecosystem,))
    total_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return total_count


def process_record(record : list) -> None or dict:
    """
    Process a single database record and extract package information.

    Parameters:
    - record (list): A list of values representing a single database record.

    Returns:
    - JSON with processed package information, or None if crucial fields are missing.
    """

    package_name = None
    package_licenses = None
    package_language = None
    package_starcount = None
    package_owner_github = None
    package_ecosystem = record[3]
    package_repo = record[5]
    
    if (record[6] == record[5]) or (package_repo == None):
        package_repo = record[6]

    if not package_repo or not package_repo.strip():
        package_repo = None
    
    repo_metadata = record[8]

    if repo_metadata is None:
        if package_repo == None:
            return None
    else:
        package_name = repo_metadata.get("full_name", "").split('/')[-1]

        package_licenses = {
            "Normalised License": record[4],
            "licenses": record[7],          
            "GitHub_License": repo_metadata.get("license")
        }
        
        package_language = repo_metadata.get("language")
        package_starcount = repo_metadata.get("stargazers_count")
        package_owner_github = repo_metadata.get("owner")

        # If either owner or name is empty, return None
        if not package_owner_github or not package_name:
            return None
        
        # Guess GitHub URL. Might be wrong
        package_repo = f"https://github.com/{package_owner_github}/{package_name}"
    
    if package_repo is not None and package_repo not in unique_urls:
        unique_urls.add(package_repo)

        if package_name is None or package_owner_github is None:
            match = re.match(r"https?://(?:www\.)?(github|gitlab)\.com/([^/]+)/([^/]+)", package_repo)
            if match:
                package_name = match.group(3)
                package_owner_github = match.group(2)

        return {
            "package_repo" : package_repo, 
            "package_name" : package_name, 
            "repo_owner" : package_owner_github, 
            "package_ecosystem" : package_ecosystem, 
            "package_licenses" : package_licenses, 
            "package_language" : package_language, 
            "package_starcount" : package_starcount,
            "downloads" : record[9]
        }
    
    return None

def main():
    parser = argparse.ArgumentParser(description="Extract package information based on the desired ecosystems.", allow_abbrev=False)
    parser.add_argument('--maven', action='store_true', help="Extract packages for Maven ecosystem.")
    parser.add_argument('--npm', action='store_true', help="Extract packages for npm ecosystem.")
    parser.add_argument('--pypi', action='store_true', help="Extract packages for PyPI ecosystem.")
    parser.add_argument('--filter-count', type=int, default=100, help="Minimum number of downloads to filter the packages.")
    parser.add_argument('--display-db-size', action='store_true', help="Display the size of the database.")
    args = parser.parse_args()

    ecosystems = [ecosystem for ecosystem in ['maven', 'npm', 'pypi'] if getattr(args, ecosystem)]

    if not ecosystems:
        # If no ecosystems are provided, prompt the user for input
        user_input_ecosystem = input("Enter the ecosystem (maven, npm, or pypi): ").lower()
        if user_input_ecosystem not in ['maven', 'npm', 'pypi']:
            print("Invalid ecosystem. Please choose from 'maven', 'npm', or 'pypi'.")
            return
        ecosystems = [user_input_ecosystem]

    for ecosystem in ecosystems:
        process_ecosystem(ecosystem, args.filter_count, args.display_db_size)


def process_ecosystem(ecosystem : str, filter_count=10, display_db_size=False):
    """
    Processes packages in a given ecosystem from the database based on filters and display options.

    Parameters:
    - ecosystem (str): The ecosystem to be processed.
    - filter_count (int, optional): The minimum number of downloads required to process a package.
    - display_db_size (bool, optional): Flag to display the total number of packages in the ecosystem.

    Side effects:
    - Writes processed package information into a .ndjson file.
    """

    print (f"Processing {ecosystem}...")

    conn = psycopg2.connect(**db_credentials)
    cursor = conn.cursor(name="large_result_cursor")

    output_file = f"extracted/{ecosystem}_packages_{filter_count}.ndjson"
    packages_list = []

    query = """
        SELECT 
            id, registry_id, name, ecosystem, licenses,
            repository_url, homepage, normalized_licenses, repo_metadata, downloads
        FROM 
            packages
        WHERE 
            ecosystem = %s AND downloads >= %s;
    """

    # Query returns list. Each field is a list item in-order. 
    # So, id field is record[0], registry_id is record[1], name is record[2] and so on

    cursor.execute(query, (ecosystem, filter_count))
    records = list(cursor.fetchmany(1000))

    while records:
        for record in records:
            package_info = process_record(record)
            if package_info:
                packages_list.append(package_info)

        records = list(cursor.fetchmany(1000))

    # Sort isn't necessary, but helps with running diff
    packages_list = sorted(packages_list, key=lambda package: package["downloads"], reverse=True) 

    with open(output_file, "w") as f:
        for package in packages_list:
            json.dump(package, f)
            f.write('\n')

    out_pkg_cnt = len(packages_list)

    print (f"Dumped {out_pkg_cnt} items to {output_file}")

    if display_db_size:
        pkg_count = get_total_package_count(ecosystem)
        print (f"{ecosystem} database has {pkg_count} packages. Filtered out {pkg_count - out_pkg_cnt} packages")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()