import argparse
import json
import os
from xml.etree import ElementTree as ET

import requests
import xmltodict
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

# ORDER MATTERS!
from models.base import Base
from models.author import Author
from models.division import Division
from models.faculty import Faculty
from models.institute import Institute
from models.sdg_prediction import SDGPrediction
from models.sdg_label import SDGLabel
from models.sdg_label_history import SDGLabelHistory
from models.sdg_label_decision import SDGLabelDecision
from models.sdg_user_label import SDGUserLabel
from models.dim_red import DimRed
from models.publication import Publication

from settings.settings import CollectorSettings
collector_settings = CollectorSettings()

# Setup Logging
from utils.logger import logger
logging = logger(collector_settings.COLLECTOR_LOG_NAME)

def save_resumption_token(token, file_path="resumption_token.txt"):
    """Save the resumption token to a text file."""
    with open(file_path, "w") as f:
        f.write(token)
    logging.info(f"Resumption token saved to {file_path}")

def load_resumption_token(file_path="resumption_token.txt"):
    """Load the resumption token from a text file, return None if not found."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            token = f.read().strip()
        logging.info(f"Resumption token loaded from {file_path}")
        return token if token else None
    return None

def save_raw_metadata(metadata, identifier, subfolder):
    """Save raw metadata as a JSON file."""
    # Prepare raw metadata and save copy
    raw_metadata = xmltodict.parse(ET.tostring(metadata, encoding="unicode"))
    raw_file_path = os.path.join(
        f"{CollectorSettings.JSON_PATH}/{subfolder}", f"{identifier.replace(':', '_')}.json"
    )

    # Ensure the directory exists
    os.makedirs(os.path.dirname(raw_file_path), exist_ok=True)

    with open(raw_file_path, "w") as f:
        json.dump(raw_metadata, f, indent=4)

# Function to configure the database engine
def setup_database(engine_str):
    logging.info(f"Setting up database using engine: {engine_str}")
    engine = create_engine(engine_str)
    Base.metadata.create_all(engine)  # Create all tables if they don't exist
    Session = sessionmaker(bind=engine)
    return Session

def setup_mariadb_connection():
    from db.mariadb_connector import engine as mariadb_engine

    return mariadb_engine

def setup_sqlite_connection(db_path="sqlite:///publications.db"):
    return create_engine(db_path)

def reset_database(session):
    # Disable foreign key checks
    session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    session.commit()

    # Drop all tables
    Base.metadata.drop_all(bind=session.get_bind())

    # Re-enable foreign key checks
    session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    session.commit()

    # Re-create all tables
    Base.metadata.create_all(bind=session.get_bind())


def extract_setSpec(setSpec):

    if setSpec is None:
        return (None, None, None)

    parts_setSpec = setSpec.split(":")

    faculty_setSpec, institute_setSpec, division_setSpec = (None, None, None)

    if len(parts_setSpec) == 1:
        faculty_setSpec = parts_setSpec[0].strip()
    elif len(parts_setSpec) == 2:
        faculty_setSpec = parts_setSpec[0].strip()

        institute_setSpec = parts_setSpec[1].strip()
    elif len(parts_setSpec) == 3:
        faculty_setSpec = parts_setSpec[0].strip()
        institute_setSpec = parts_setSpec[1].strip()
        division_setSpec = parts_setSpec[2].strip()

    return faculty_setSpec, institute_setSpec, division_setSpec


def extract_organization_info(setSpec, setName):
    """Extract faculty, institute, and division from set_spec and set_name."""

    if setSpec is None or setName is None:
        return (None, None, None, None, None, None)

    parts_setSpec = setSpec.split(":")
    parts_setName = setName.split(":")

    (
        faculty_setSpec,
        institute_setSpec,
        division_setSpec,
        faculty_setName,
        institute_setName,
        division_setName,
    ) = (None, None, None, None, None, None)

    if len(parts_setSpec) != len(parts_setName):
        if len(parts_setSpec) == 1 and len(parts_setName) == 2:
            faculty_setSpec = parts_setSpec[0].strip()
            faculty_setName = " ".join(parts_setName).strip()

        elif len(parts_setSpec) == 2 and len(parts_setName) == 3:
            faculty_setSpec = parts_setSpec[0].strip()
            faculty_setName = parts_setName[1].strip()

            institute_setSpec = parts_setSpec[0].strip()
            institute_setName = " ".join(parts_setName[1:]).strip()

        elif len(parts_setSpec) == 3 and len(parts_setName) == 4:

            faculty_setSpec = parts_setSpec[0].strip()
            institute_setSpec = parts_setSpec[1].strip()
            division_setSpec = parts_setSpec[2].strip()

            faculty_setName = parts_setName[0].strip()
            institute_setName = parts_setName[1].strip()
            division_setName = " ".join(parts_setName[2:]).strip()
    else:
        if len(parts_setSpec) == 1:
            faculty_setSpec = parts_setSpec[0].strip()
            faculty_setName = parts_setName[0].strip()
        elif len(parts_setSpec) == 2:
            faculty_setSpec = parts_setSpec[0].strip()
            faculty_setName = parts_setName[0].strip()

            institute_setSpec = parts_setSpec[1].strip()
            institute_setName = parts_setName[1].strip()
        elif len(parts_setSpec) == 3:
            faculty_setSpec = parts_setSpec[0].strip()
            faculty_setName = parts_setName[0].strip()

            institute_setSpec = parts_setSpec[1].strip()
            institute_setName = parts_setName[1].strip()

            division_setSpec = parts_setSpec[2].strip()
            division_setName = parts_setName[2].strip()

    # logging.info(f"Sets {faculty_setSpec, institute_setSpec, division_setSpec, faculty_setName, institute_setName, division_setName}")
    return (
        faculty_setSpec,
        institute_setSpec,
        division_setSpec,
        faculty_setName,
        institute_setName,
        division_setName,
    )


def get_or_create_faculty(faculty_setSpec, faculty_name, session):
    """Get or create a faculty in the database."""

    faculty = session.query(Faculty).filter_by(faculty_setSpec=faculty_setSpec).first()
    if not faculty and faculty_setSpec:
        faculty = Faculty(faculty_setSpec=faculty_setSpec, faculty_name=faculty_name)
        session.add(faculty)
        session.flush()  # Ensure faculty is persisted
        # logging.info(f"Faculty created: {faculty.faculty_setSpec}")
    logging.debug(f"Faculty returned: {faculty.faculty_setSpec}")
    return faculty


def get_or_create_institute(institute_setSpec, institute_name, session):
    """Get or create an institute in the database."""
    institute = (
        session.query(Institute).filter_by(institute_setSpec=institute_setSpec).first()
    )
    if not institute and institute_setSpec:
        institute = Institute(
            institute_setSpec=institute_setSpec, institute_name=institute_name
        )
        session.add(institute)
        session.flush()  # Ensure institute is persisted
        # logging.info(f"Institute created: {institute.institute_setSpec}")
    logging.debug(f"Institute returned: {institute.institute_setSpec}")
    return institute


def get_or_create_division(division_setSpec, division_name, session):
    """Get or create a division in the database."""
    division = (
        session.query(Division).filter_by(division_setSpec=division_setSpec).first()
    )
    if not division and division_setSpec:
        division = Division(
            division_setSpec=division_setSpec, division_name=division_name
        )
        session.add(division)
        session.flush()  # Ensure division is persisted
        # logging.info(f"Division created: {division.division_setSpec}")
    logging.debug(f"Division returned: {division.division_setSpec}")
    return division


def insert_organization_hierarchy(session):
    """Crawl the sets from the OAI-PMH ListSets and populate the hierarchy in the database."""
    response = requests.get(collector_settings.ZORA_SET_LIST_URL)
    if response.status_code != 200:
        logging.error(f"Failed to fetch sets, status code: {response.status_code}")
        return

    root = ET.fromstring(response.content)
    ns = {"oai": "http://www.openarchives.org/OAI/2.0/"}

    for set_element in root.findall(".//oai:set", ns):
        set_spec = set_element.find("oai:setSpec", ns).text
        set_name = set_element.find("oai:setName", ns).text

        (
            faculty_setSpec,
            institute_setSpec,
            division_setSpec,
            faculty_name,
            institute_name,
            division_name,
        ) = extract_organization_info(set_spec, set_name)

        if faculty_setSpec is not None:
            get_or_create_faculty(faculty_setSpec, faculty_name, session)
            if institute_setSpec is not None:
                get_or_create_institute(institute_setSpec, institute_name, session)
                if division_setSpec is not None:
                    get_or_create_division(division_setSpec, division_name, session)

    session.commit()
    session.close()
    logging.info("Completed inserting the organization hierarchy.")


def parse_author(author_str):
    """Parses the author string to separate name and ORCID ID if available."""
    parts = author_str.split(";")
    name = parts[0].strip()
    orcid_id = parts[1].strip() if len(parts) > 1 else None
    return name, orcid_id

def fetch_batch(base_url, params, session):
    """Fetch a batch of publications."""
    logging.info("Starting to fetch a batch of publications...")
    publications = []
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        logging.error(f"Failed to fetch data, status code: {response.status_code}")
        return publications, None

    root = ET.fromstring(response.content)
    ns = {
        "oai": "http://www.openarchives.org/OAI/2.0/",
        "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
        "dc": "http://purl.org/dc/elements/1.1/",
    }

    for record in root.findall(".//oai:record", ns)[:]:
        # To have more concise logs
        identifier = record.find(".//oai:identifier", ns).text
        metadata = record.find(".//oai_dc:dc", ns)
        if metadata is None:
            logging.info(
                f"No metadata found for record with ID: {identifier}, skipping."
            )
        elif metadata.findtext(".//dc:description", namespaces=ns, default="") == "":
            logging.info(
                f"No abstract found for record with ID: {identifier}, skipping."
            )
            save_raw_metadata(metadata, identifier, collector_settings.NO_ABSTRACT_PUBLICATIONS_FOLDER_PATH)
        else:
            # Check if already in db
            identifier = record.find(".//oai:identifier", ns).text
            if session.query(Publication).filter_by(oai_identifier=identifier).first():
                logging.info(
                    f"Metadata and abstract found for record with ID: {identifier}, already in db, continuing."
                )
            else:
                logging.info(
                    f"Metadata and abstract found for record with ID: {identifier}, not in db, processing and storing."
                )
                save_raw_metadata(metadata, identifier, collector_settings.PUBLICATIONS_FOLDER_PATH)

    for record in root.findall(".//oai:record", ns)[:]:
        identifier = record.find(".//oai:identifier", ns).text
        metadata = record.find(".//oai_dc:dc", ns)

        if metadata is None:
            continue

        if metadata.findtext(".//dc:description", namespaces=ns, default="") == "":
            continue

        publication = {
            "oai_identifier": identifier,
            "oai_identifier_num": identifier.split(":")[-1],
            "title": metadata.findtext(".//dc:title", namespaces=ns),
            "description": metadata.findtext(
                ".//dc:description", namespaces=ns, default=""
            ),
            "publisher": metadata.findtext(
                ".//dc:publisher", namespaces=ns, default=""
            ),
            "date": metadata.findtext(".//dc:date", namespaces=ns, default=""),
            "source": metadata.findtext(".//dc:source", namespaces=ns, default=""),
            "language": metadata.findtext(".//dc:language", namespaces=ns, default=""),
            "format": metadata.findtext(".//dc:format", namespaces=ns, default=""),
            "authors": [
                creator.text for creator in metadata.findall(".//dc:creator", ns)
            ],
            "set_spec": (
                record.find(".//oai:setSpec", ns).text
                if record.find(".//oai:setSpec", ns) is not None
                else None
            ),
        }
        publications.append(publication)
    resumption_token = root.find(".//oai:resumptionToken", ns)
    resumption_token = resumption_token.text if resumption_token is not None else None

    if resumption_token:
        logging.info(
            f"Storing resumption token: {resumption_token}."
        )
        save_resumption_token(resumption_token)  # Save the token after fetching a batch

    logging.info(f"Batch fetching completed, {len(publications)} records fetched.")
    return publications, resumption_token


def insert_publication_with_org(publication_data, session):
    """Insert a publication and its related organization hierarchy."""
    try:
        if (
            session.query(Publication)
            .filter_by(oai_identifier=publication_data["oai_identifier"])
            .first()
        ):
            logging.debug(
                f"Publication {publication_data['oai_identifier']} already exists. Skipping."
            )
            return

        logging.debug(
            f"Extract organization info from setSpec and use it to lookup hierarchy"
        )
        # Extract organization info from setSpec and use it to lookup hierarchy
        set_spec = publication_data.get("set_spec", "")

        logging.debug(f"Query with {set_spec} to insert publication information")
        faculty_setSpec, institute_setSpec, division_setSpec = extract_setSpec(set_spec)

        logging.debug(
            f"Query with {faculty_setSpec, institute_setSpec, division_setSpec}"
        )

        # Query the database for the existing organization hierarchy
        faculty = (
            session.query(Faculty).filter_by(faculty_setSpec=faculty_setSpec).first()
            if faculty_setSpec
            else None
        )
        institute = (
            session.query(Institute)
            .filter_by(institute_setSpec=institute_setSpec)
            .first()
            if institute_setSpec
            else None
        )
        division = (
            session.query(Division).filter_by(division_setSpec=division_setSpec).first()
            if division_setSpec
            else None
        )

        logging.debug(
            f"Publication {publication_data['oai_identifier']}: {faculty}, {institute}, {division}"
        )

        default_sdg_prediction = SDGPrediction()

        # Insert the publication
        new_publication = Publication(
            oai_identifier=publication_data["oai_identifier"],
            oai_identifier_num=publication_data["oai_identifier_num"],
            title=publication_data["title"],
            description=publication_data.get("description", ""),
            publisher=publication_data.get("publisher", ""),
            date=publication_data.get("date", ""),
            source=publication_data.get("source", ""),
            language=publication_data.get("language", ""),
            format=publication_data.get("format", ""),
            faculty=faculty,
            institute=institute,
            division=division,
            sdg_predictions=[default_sdg_prediction],  # Add default SDGPrediction object in list
            sdg_labels=SDGLabel(), # Init empty
            set_spec=publication_data.get("set_spec", ""),
            embedded=False,
        )

        # Process authors
        for author_str in publication_data.get("authors", []):
            name, orcid_id = parse_author(author_str)
            author = session.query(Author).filter_by(name=name).first()
            if not author:
                author = Author(name=name, orcid_id=orcid_id)
                session.add(author)
                session.flush()
            new_publication.authors.append(author)

        session.add(new_publication)
        session.commit()
        logging.info(f"Inserted publication {new_publication.oai_identifier}")
    except IntegrityError:
        logging.error(
            f"IntegrityError: Duplicate publication {publication_data['oai_identifier']}"
        )
        session.rollback()

def crawl_publications(session, max_count=collector_settings.PUBLICATION_LIMIT):
    """Crawl the publications from the OAI-PMH repository."""
    resumption_token = load_resumption_token()  # Load token from the file if exists
    total_fetched = 0
    params = {"verb": "ListRecords", "metadataPrefix": "oai_dc"}

    if resumption_token:
        params["resumptionToken"] = resumption_token

    while total_fetched < max_count:
        publications, resumption_token = fetch_batch(
            collector_settings.ZORA_BASE_URL, params, session
        )
        if not publications:
            logging.info(
                "No valid records found in this batch, continuing to next batch."
            )
            if resumption_token:
                params["resumptionToken"] = resumption_token
                continue
            else:
                logging.info("No more data to fetch or resumption token available.")
                break

        for publication_data in tqdm(publications, desc="Processing batch"):
            insert_publication_with_org(publication_data, session)

        total_fetched += len(publications)
        logging.info(
            f"Processed a batch of {len(publications)} publications. Total processed: {total_fetched}"
        )

        if not resumption_token:
            logging.info("No more data to fetch or max count reached.")
            break

        params["resumptionToken"] = resumption_token

    session.close()


def main(db, reset, recreate_organizational_structure):
    # Configure database connection based on argument
    if db == "mariadb":
        from db.mariadb_connector import (
            engine as mariadb_engine,  # Use the mariadb connector
        )

        session_maker = sessionmaker(bind=mariadb_engine)
        logging.info("Using MariaDB database.")
        Base.metadata.create_all(
                mariadb_engine
            )  # Ensure tables are created if they don't exist
        if reset == "true":
            reset_database(session_maker())
            logging.info("Reset MariaDB database.")
        else:
            Base.metadata.create_all(
                mariadb_engine
            )  # Ensure tables are created if they don't exist
    else:
        sqlite_engine = setup_sqlite_connection()
        session_maker = sessionmaker(bind=sqlite_engine)
        logging.info("Using SQLite database.")

    session = session_maker()

    if recreate_organizational_structure:
        logging.info("Starting extraction of organizational hierarchy.")
        insert_organization_hierarchy(session)

    logging.info("Starting publication crawling.")
    crawl_publications(session)

    session.close()
    logging.info("Process complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run publication collector with SQLite or MariaDB."
    )
    parser.add_argument(
        "--db",
        choices=["sqlite", "mariadb"],
        default="sqlite",
        help="Specify the database to use: sqlite or mariadb (default: sqlite)",
    )
    parser.add_argument(
        "--reset",
        choices=["true", "false"],
        default="false",
        help="Reset the container database: true or false (default: false)",
    )
    parser.add_argument(
        "--recreate_organizational_structure",
        choices=["true", "false"],
        default="false",
        help="Recreate organizational structure in db: true or false (default: false)",
    )
    args = parser.parse_args()

    main(args.db, args.reset, args.recreate_organizational_structure)

def collector_main(db, reset, recreate_organizational_structure):
    main(db, reset, recreate_organizational_structure)
