from atlassian import Confluence
from markdownify import markdownify
import os
from pathlib import Path


class ConfluenceDownloader:

    def __init__(self, url: str, username: str, token: str, space_key: str):
        self.confluence = Confluence(
            url=url,
            username=username,
            password=token,
        )
        self.space_key = space_key

    def download_page_as_markdown(self, title: str, output_dir: str):
        # creando la carpeta de salida: ok
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{title.replace(' ', '_')}.md"

        # espacio = self.confluence.get_all_pages_from_space(self.space_key)

        pagina = self.confluence.get_page_by_title(
            space=self.space_key, title=title)

        cuerpo = pagina["body"]

        print(f"nombre nuevo archivo: {filename}")
        print(f"se descarga en : {output_dir}")
        print(f" El cuerpo del archivo es:\n {cuerpo}")
