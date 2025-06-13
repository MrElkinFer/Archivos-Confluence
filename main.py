# from src.descarga import ConfluenceDownloader
from src.descarga import ConfluenceDownloader
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_URL = os.getenv("URL_CONFLUENCE")
SPACE_KEY = os.getenv("SPACE_KEY")
PAGE_TITLE = os.getenv("PAGE_TITLE")
USERNAME = os.getenv("USERNAME")


downloader = ConfluenceDownloader(
    CONFLUENCE_URL, USERNAME, API_TOKEN, SPACE_KEY)

prueba = downloader.download_page_as_markdown(
    title="Resumen gravedad cuática", output_dir="descargas")
