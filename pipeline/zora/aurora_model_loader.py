import csv
import os

import requests
from tqdm import tqdm


class ModelDownloader:
    """
    A class responsible for downloading model files from provided URLs, if they don't already exist locally.
    """

    def __init__(self, csv_file, destination_dir):
        """
        Initializes the downloader with a CSV file containing URLs and a destination directory.

        :param csv_file: Path to the CSV file containing URLs to download.
        :param destination_dir: Local directory where files should be saved.
        """
        self.csv_file = csv_file
        self.destination_dir = destination_dir
        self.file_list = self._parse_csv()
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        """Ensure the destination directory exists, if not, create it."""
        if not os.path.exists(self.destination_dir):
            os.makedirs(self.destination_dir)

    def _parse_csv(self):
        """
        Parses the CSV file and returns a list of URLs.

        :return: List of file URLs.
        """
        file_urls = []
        with open(self.csv_file, mode="r") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row:  # Ensure the row is not empty
                    file_urls.append(row[0])
        return file_urls

    def download_file(self, url):
        """
        Downloads a file from a given URL if it does not exist.

        :param url: URL of the file to download.
        """
        file_name = os.path.basename(url)
        file_path = os.path.join(self.destination_dir, file_name)

        # Skip downloading if the file already exists
        if os.path.exists(file_path):
            print(f"{file_name} already exists, skipping download.")
            return

        # Start downloading the file with progress bar
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))

        with open(file_path, "wb") as file, tqdm(
            desc=file_name,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                bar.update(len(data))

    def download_all_files(self):
        """
        Downloads all files listed in the CSV file, if they don't already exist.
        """
        for url in self.file_list:
            self.download_file(url)


if __name__ == "__main__":
    # Set the CSV file location and destination directory
    csv_file = "pipeline/zora/aurora-model-goal-only-links.csv"
    destination_dir = "data/pipeline/aurora_models"

    # Create the downloader instance and download the files
    downloader = ModelDownloader(csv_file, destination_dir)
    downloader.download_all_files()
