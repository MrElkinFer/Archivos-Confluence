# confluence_downloader/downloader.py
from atlassian import Confluence
import os


class ConfluenceDownloader:
    def __init__(self, url: str, username: str, token: str, space_key: str):
        self.confluence = Confluence(
            url=url,
            username=username,
            password=token
        )
        self.space_key = space_key

    def download_page_as_markdown(self, title: str, output_dir: str):

        page = self.confluence.get_page_by_title(self.space_key, title)
        if not page:
            raise ValueError(f"No se encontró la página con título '{title}'")

        html = page["body"]["storage"]["value"]
        md_content = md(html)

        os.makedirs(output_dir, exist_ok=True)
        filename = f"{title.replace(' ', '_')}.md"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        return filepath
