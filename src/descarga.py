from atlassian import Confluence
from markdownify import markdownify
import os


class ConfluenceDownloader:

    def __init__(self, url, username, token, space_key):
        self.confluence = Confluence(
            url=url,
            username=username,
            password=token,
        )
        self.space_key = space_key

    def download_page_as_markdown(self, title, output_dir):
        # creando la carpeta de salida: ok
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{title.replace(' ', '_')}.md"

        # espacio = self.confluence.get_all_pages_from_space(self.space_key)
        page = self.confluence.get_page_by_title(
            space=self.space_key,
            title=title,
            expand='body.storage')

        if not page:
            raise ValueError("Página no encontrada.")
        html_content = page["body"]["storage"]["value"]

        print(html_content)

        contenido_md = markdownify(html=html_content)

        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(contenido_md)

        return filepath
