from src.download_page_from_space import ConfluenceSpaceDocumentDownloader
import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

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
# Descarga y guardado de todos las páginas de un espacio en Confluence en formato markdown
# downloadPagesFromSpace = descarga.Downloader_pages_from_space_md(space="EDP")

# Actualización en local de las páginas de un espacio en Confluence
# updatePages = descarga.Read_and_update_space(
#    localpath="knowledge/confluence/spaces", space=SPACE_KEY)


scheduler = BlockingScheduler()

# scheduler.add_job(lambda: descarga.downloader_pages_from_space_md(
#   space=SPACE_KEY), 'cron', minute=0)
scheduler.add_job(lambda: descarga.Read_and_update_space(
    spacepath="knowledge/confluence/spaces", space=SPACE_KEY), 'interval', seconds=60)

scheduler.start()
# prueba = descarga.pages_from_space("EDP")
# prueba = descarga.read_and_update_space(
#  spacepath="knowledge/confluence/spaces", space=SPACE_KEY)
