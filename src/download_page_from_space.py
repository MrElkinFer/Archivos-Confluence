from atlassian import Confluence
from markdownify import markdownify
import os
import json


class ConfluenceSpaceDocumentDownloader:

    def __init__(self, url, username, token):
        self.confluence = Confluence(
            url=url,
            username=username,
            password=token,
        )

    def Downloader_pages_from_space_md(self, space):

        pages = self.confluence.get_all_pages_from_space(
            space=space,
            start=0,
            expand='body.storage',
            limit=100,
        )

        for page in pages:

            html = page["body"]["storage"]["value"]
            # meta = page["_expandable"]
            # print(meta)

            content_md = markdownify(html)

            page_id = page["id"]
            space_key = page["_expandable"]["space"]
            space_id = space_key.split('/')[-1]

            metadata = self.confluence.history(page_id)
            # print(metadata)

            output_dir = f"knowledge/confluence/spaces/{space_id}/{page_id}"

            os.makedirs(output_dir, exist_ok=True)

            filepath = os.path.join(output_dir, "content.md")
            metadatapath = os.path.join(output_dir, "metadata.json")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content_md)
            with open(metadatapath, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)

    # def Confuence_Page_history(space, page):
