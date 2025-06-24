# from src.descarga import ConfluenceDownloader
# from src.descarga import ConfluenceDownloader
from src.download_page_from_space import ConfluenceSpaceDocumentDownloader
# from src.confluence_space_listener import dircount
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_URL = os.getenv("URL_CONFLUENCE")
SPACE_KEY = os.getenv("SPACE_KEY")
PAGE_TITLE = os.getenv("PAGE_TITLE")
USERNAME = os.getenv("USERNAME")


# prueba = dircount("knowledge/confluence/spaces")
# prueba = load_space_state("knowledge/confluence/spaces")

descarga = ConfluenceSpaceDocumentDownloader(
    username=USERNAME, token=API_TOKEN, url=CONFLUENCE_URL)

# prueba = descarga.pages_from_space("EDP")
# prueba = descarga.read_and_update_space(
#  spacepath="knowledge/confluence/spaces", space=SPACE_KEY)
prueba = descarga.downloader_pages_from_space_md(space="EDP")
print(prueba)
