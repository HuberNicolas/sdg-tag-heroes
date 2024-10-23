from prefect import flow, task
from pipeline.zora.collector import collector_main
from pipeline.zora.predictor import predictor_main
from pipeline.zora.loader import loader_main
from pipeline.zora.reducer import reducer_main
from settings.settings import PrefectSettings

# Setup Logging
prefect_settings = PrefectSettings()
from utils.logger import logger
logging = logger(prefect_settings.PREFECT_LOG_NAME)

# Define Prefect tasks
@task(log_prints=True)
def run_collector(db_type, reset, batch_size):
    logging.info("Start Collector")
    collector_main(db_type, reset, batch_size)
    logging.info("Collector finished")

@task(log_prints=True)
def run_predictor(db_type, batch_size):
    logging.info("Start Predictor")
    predictor_main(db_type, batch_size)
    logging.info("Predictor finished")

@task(log_prints=True)
def run_loader(db_type, batch_size):
    logging.info("Start Loader")
    loader_main(db_type, batch_size)
    logging.info("Loader finished")

@task(log_prints=True)
def run_reducer(db_type):
    logging.info("Start Reducer")
    reducer_main(db_type)
    logging.info("Reducer finished")

# Define the main flow
@flow(log_prints=True, name="Prepare SDG System")
def orchestrator_workflow():
    # Call each task in sequence, Prefect will ensure that each task completes before moving to the next one
    run_collector(prefect_settings.DB_TYPE, prefect_settings.COLLECTOR_RESET, prefect_settings.COLLECTOR_BATCH_SIZE)
    run_predictor(prefect_settings.DB_TYPE, prefect_settings.PREDICTOR_BATCH_SIZE)
    run_loader(prefect_settings.DB_TYPE, prefect_settings.LOADER_BATCH_SIZE)
    run_reducer(prefect_settings.DB_TYPE)

# Entry point for running the flow
if __name__ == "__main__":
    orchestrator_workflow()
