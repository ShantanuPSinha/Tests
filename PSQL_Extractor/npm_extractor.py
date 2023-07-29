import psycopg2
import json
from logger import init_logger, dump_error
import os

localhost_password = os.environ.get("PSQL_Password") or ''

db_credentials = {
    "dbname": "packages_production",
    "user": "postgres",
    "password": localhost_password,
    "host": "localhost",
    "port": "5432"  # Default PostgreSQL port
}

logger, newline = init_logger()
unique_urls = set()

def process_record(record : list):
    package_name = None
    package_licenses = None
    package_language = None
    package_starcount = None
    package_owner_github = None
    package_ecosystem = record[3]
    package_repo = record[5]

    if (record[6] == record[5]) or (package_repo == None):
        package_repo = record[6]

    if (package_repo == None) or (package_repo == "") or (package_repo == " "):
        package_repo = None
    
    repo_metadata = record[8]
    
    if repo_metadata == {}:
        logger.error(f"Package {record[2]} at id {record[0]} has no Repo Metadata. Possible Repo URLs - {record[6]} or {record[5]}")
        dump_error (record)

        if package_repo == None:
            return None
    else:
        package_name = repo_metadata["full_name"].split('/')[-1]
        package_licenses = {"Normalised License" : record[4], "licenses" : record[7], "GitHub_License" : repo_metadata["license"]}
        package_language = repo_metadata["language"]
        package_starcount = repo_metadata["stargazers_count"]
        package_owner_github = repo_metadata["owner"]

        # If either owner or name is empty, return None
        if package_owner_github == None or package_owner_github == "" or package_name == None or package_name == "":
            return None
        
        # Guess GitHub URL. Might be wrong
        package_repo = f"https://github.com/{package_owner_github}/{package_name}"
    
    if package_repo not in unique_urls:
        unique_urls.add(package_repo)

        return {
            "package_repo" : package_repo, 
            "package_name" : package_name, 
            "repo_owner" : package_owner_github, 
            "package_ecosystem" : package_ecosystem, 
            "package_licenses" : package_licenses, 
            "package_language" : package_language, 
            "package_starcount" : package_starcount
        }
    
    return None

def main():
    init_logger()
    output_file = f"extracted/npm_packages.ndjson"

    # List to store package information
    packages_list = []

    conn = psycopg2.connect(**db_credentials)
    cursor = conn.cursor(name="large_result_cursor")

    # Construct the dynamic SQL query with parameterized query
    query = """
        SELECT 
            id, registry_id, name, ecosystem, licenses,
            repository_url, homepage, normalized_licenses, repo_metadata
        FROM 
            packages
        WHERE 
            ecosystem = 'npm';
    """

    # Pass the user input as a tuple to cursor.execute
    cursor.execute(query)
    records = list(cursor.fetchmany(1000))

    while records:
        for record in records:
            package_info = process_record(record)
            if package_info:
                packages_list.append(package_info)

        records = list(cursor.fetchmany(1000))

    # Write all packages to the output file
    with open(output_file, "w") as f:
        for package in packages_list:
            json.dump(package, f)
            f.write('\n')

    cursor.close()
    conn.close()

# Call the main function to start the program
if __name__ == "__main__":
    main()
