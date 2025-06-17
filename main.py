# from src.descarga import ConfluenceDownloader
from src.descarga import ConfluenceDownloader
from src.download_page_from_space import ConfluenceSpaceDocumentDownloader
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_URL = os.getenv("URL_CONFLUENCE")
SPACE_KEY = os.getenv("SPACE_KEY")
PAGE_TITLE = os.getenv("PAGE_TITLE")
USERNAME = os.getenv("USERNAME")


"""downloader = ConfluenceDownloader(
    CONFLUENCE_URL, USERNAME, API_TOKEN, SPACE_KEY)"""

"""prueba = downloader.download_page_as_markdown(
    title=PAGE_TITLE, output_dir="descargas")"""


descarga = ConfluenceSpaceDocumentDownloader(
    username=USERNAME, token=API_TOKEN, url=CONFLUENCE_URL)


prueb = descarga.Downloader_pages_from_space_md(space=SPACE_KEY)
