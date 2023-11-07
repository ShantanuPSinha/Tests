#! /usr/bin/python3

from logger import init_logger, dump_error
import os, sys, argparse
import re, json, psycopg2

localhost_password = os.environ.get("PSQL_Password") or 'postgres'

db_credentials = {
    "dbname": "packages_production",
    "user": "postgres",
    "password": localhost_password,
    "host": "localhost",
    "port": "5432"  # Default PostgreSQL port
}

logger, newline = init_logger()
unique_urls = set()

def get_total_package_count():
    conn = psycopg2.connect(**db_credentials)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM packages;")
    total_count = cursor.fetchone()[0]

    print (f"Total number of Packages in Database: {total_count}")
    
    cursor.close()
    conn.close()


def process_record(record : list) -> None or dict:
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
    parser = argparse.ArgumentParser(description="Extract package information based on the desired ecosystems.")
    parser.add_argument('--maven', action='store_true', help="Extract packages for Maven ecosystem.")
    parser.add_argument('--npm', action='store_true', help="Extract packages for npm ecosystem.")
    parser.add_argument('--pypi', action='store_true', help="Extract packages for PyPI ecosystem.")
    parser.add_argument('--filter-count', type=int, default=100, help="Minimum number of downloads to filter the packages.")
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
        process_ecosystem(ecosystem, args.filter_count)


def process_ecosystem(ecosystem : str, filter_count=10):
    print (f"Processing {ecosystem}...")
    print (f"Excluding packages with less than {filter_count} lifetime downloads.\n")

    conn = psycopg2.connect(**db_credentials)
    cursor = conn.cursor(name="large_result_cursor")

    output_file = f"extracted/{ecosystem}_packages_{filter_count}.ndjson"
    packages_list = []

    # Construct the dynamic SQL query with parameterized query
    query = """
        SELECT 
            id, registry_id, name, ecosystem, licenses,
            repository_url, homepage, normalized_licenses, repo_metadata, downloads
        FROM 
            packages
        WHERE 
            ecosystem = %s AND downloads >= %s;
    """   

    cursor.execute(query, (ecosystem, filter_count))
    records = list(cursor.fetchmany(1000))

    while records:
        for record in records:
            package_info = process_record(record)
            if package_info:
                packages_list.append(package_info)

        records = list(cursor.fetchmany(1000))
       
    # Write all packages to the output file
    packages_list = sorted(packages_list, key=lambda package: package["downloads"], reverse=True)    
    with open(output_file, "w") as f:
        for package in packages_list:
            json.dump(package, f)
            f.write('\n')

    print (f"Dumped {len(packages_list)} items to {output_file}")

    cursor.close()
    conn.close()


# Call the main function to start the program
if __name__ == "__main__":
    main()
    get_total_package_count()
