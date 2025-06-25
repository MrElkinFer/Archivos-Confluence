from atlassian import Confluence
from markdownify import markdownify
import os
import json

# TODO: si son mas de 20 páginas cargar por partes para no saturar


class ConfluenceSpaceDocumentDownloader:

    def __init__(self, url, username, token):
        self.confluence = Confluence(
            url=url,
            username=username,
            password=token,
        )

    # TODO Cargar una cantidad de páginas en ciclo si hay mas de 100 por cargar.
    def _pages_from_space(self, space: str, start=0, limit=100):
        pages = self.confluence.get_all_pages_from_space(
            space=space,
            start=start,
            expand='body.storage',
            limit=limit,
        )
        return pages

    def downloader_pages_from_space_md(self, space, pageid: list[str] | None = None):

        if pageid is not None:
            try:
                pages = []
                for id in pageid:
                    page = self.confluence.get_page_by_id(
                        id, expand="body.storage")
                    pages.append(page)
            except Exception as e:
                print(f"Error inesperado: {e}")
        else:
            pages = self._pages_from_space(space)

        for page in pages:

            html = page["body"]["storage"]["value"]
            content_md = markdownify(html)
            page_id = page["id"]
            space_key = page["_expandable"]["space"]
            space_id = space_key.split('/')[-1]
            metadata = self.confluence.history(page_id)
            output_dir = f"knowledge/confluence/spaces/{space_id}/{page_id}"
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, "content.md")
            metadatapath = os.path.join(output_dir, "metadata.json")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content_md)
            with open(metadatapath, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)

        # TODO: Creaer la estructura del metadato de el espacio:

    def read_and_update_space(self, spacepath, space):

        # 1. Carga de información desde el metadato del espacio: número del documento y fecha de actualización
        path = f"{spacepath}/EDP/metadata.json"
        with open(path, "r") as f:
            data = json.load(f)
        # Cantidad de páginas:
        localpages = len(data)
        # Parejas ordenadas "id": "lastUpdate" del metadato de el space:
        localpaires = data["pages"]

        # 2. Carga de los datos actuales de las páginas:
        pairs = {}
        pages = self._pages_from_space(space)
        for page in pages:
            idpage = page["id"]
            pagehistory = self.confluence.history(idpage)
            lastUpdate = pagehistory["lastUpdated"]["when"]
            pairs[idpage] = lastUpdate

        # Comparación entre pares locales y pares obtenidos o actuales:

        if pairs == localpaires:
            print(f"L84: No hay cambios en el espacio: {space}")
        else:
            # lista de id de las páginas que no están en local (páginas nuevas)
            newpairs = list(set(pairs.keys())-set(localpaires.keys()))
            # TODO Marcar en el metadato que la página fue eliminada de confluence y crear método para guardar en carpeta eliminados con su nota en metadato
            deletepairs = list(set(localpaires.keys())-set(pairs.keys()))

            if newpairs is not None and deletepairs is not None:
                self.downloader_pages_from_space_md(
                    space=space, pageid=newpairs)
                print("L94 nuevas páginas y crear en carpeta para las borradas")
            elif newpairs is not None:
                self.downloader_pages_from_space_md(
                    space=space, pageid=newpairs)
                print("L98: Ejecutando solo nuevos pares")
            else:
                print("L100: crear en carpeta para las borradas")
