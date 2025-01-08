import re
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from db.mariadb_connector import engine as mariadb_engine
from models.sdg_label_summary import SDGLabelSummary
from models.sdg_label_history import SDGLabelHistory

# Initialize session
Session = sessionmaker(bind=mariadb_engine)

def load_sdg_label_data(file_path, batch_size=100):
    # Read the file containing SDG label data
    with open(file_path, 'r') as f:
        file_content = f.read()

    # Extract tuples from the file
    tuples = re.findall(r"\(([^)]+)\)", file_content)

    data_summary = []
    data_history = []
    current_timestamp = datetime.now()

    for index, tuple_str in enumerate(tuples):
        if not tuple_str.strip():
            continue

        try:
            # Parse the tuple fields
            fields = [field.strip() for field in tuple_str.split(',')]
            publication_id = int(fields[0])
            sdg_labels = [int(fields[i]) for i in range(1, 18)]  # SDG labels from sdg1 to sdg17

            print(f"Processing publication_id={publication_id} with SDG labels: {sdg_labels}")

            # Create SDGLabelHistory object
            history = SDGLabelHistory(
                active=True,
                created_at=current_timestamp,
                updated_at=current_timestamp
            )
            data_history.append(history)

            # Create SDGLabelSummary object (initially without history_id)
            summary = SDGLabelSummary(
                publication_id=publication_id,
                sdg1=sdg_labels[0],
                sdg2=sdg_labels[1],
                sdg3=sdg_labels[2],
                sdg4=sdg_labels[3],
                sdg5=sdg_labels[4],
                sdg6=sdg_labels[5],
                sdg7=sdg_labels[6],
                sdg8=sdg_labels[7],
                sdg9=sdg_labels[8],
                sdg10=sdg_labels[9],
                sdg11=sdg_labels[10],
                sdg12=sdg_labels[11],
                sdg13=sdg_labels[12],
                sdg14=sdg_labels[13],
                sdg15=sdg_labels[14],
                sdg16=sdg_labels[15],
                sdg17=sdg_labels[16],
                created_at=current_timestamp,
                updated_at=current_timestamp
            )
            data_summary.append(summary)

            # Commit the batch when the size limit is reached
            if len(data_summary) == batch_size:
                with Session() as session:
                    session.add_all(data_history)
                    session.flush()  # Ensure IDs are generated for history
                    for i, summary_obj in enumerate(data_summary):
                        summary_obj.history_id = data_history[i].history_id
                    session.add_all(data_summary)
                    session.commit()
                    print(f"Committed batch of {batch_size} SDG label summaries.")
                data_summary.clear()
                data_history.clear()

        except (IndexError, ValueError, TypeError) as e:
            print(f"Skipping invalid line: {tuple_str} - Error: {e}")
            continue

    # Commit any remaining data
    if data_summary:
        with Session() as session:
            session.add_all(data_history)
            session.flush()
            for i, summary_obj in enumerate(data_summary):
                summary_obj.history_id = data_history[i].history_id
            session.add_all(data_summary)
            session.commit()
            print(f"Committed final batch of {len(data_summary)} SDG label summaries.")

# Call the loader with the file path
file_path = "./data/db/sdg_label_summary.txt"
load_sdg_label_data(file_path, batch_size=500)
