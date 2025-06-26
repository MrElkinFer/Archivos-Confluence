from atlassian import Confluence
from markdownify import markdownify
import os
import json
from datetime import datetime, timezone


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
                for id in pageid:
                    page = self.confluence.get_page_by_id(
                        id, expand="body.storage")
                    pages.append(page)
                # Aquí va el metadato para actualizar (/crear si se eliminó)
            except Exception as e:
                print(f"Error inesperado: {e}")
        else:
            pages = self._pages_from_space(space)
            # Aquí va el metadato del espacio nuevo
        pagesid = []
        space_root_path = f"knowledge/confluence/spaces/"

        for page in pages:

            html = page["body"]["storage"]["value"]
            content_md = markdownify(html)
            page_id = page["id"]
            pagesid.append(page_id)
            space_key = page["_expandable"]["space"]
            space_id = space_key.split('/')[-1]
            metadata = self.confluence.history(page_id)
            output_dir = f"{space_root_path}/{space_id}/{page_id}"
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, "content.md")
            metadatapath = os.path.join(output_dir, "metadata.json")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content_md)
            with open(metadatapath, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)

        # TODO: Creaer la estructura del metadato de el espacio:

        self._space_metadata(path=space_root_path,
                             space=space, pagesid=pagesid)

    def read_and_update_space(self, spacepath, space):

        # 1. Carga de información desde el metadato del espacio: número del documento y fecha de actualización
        path = f"{spacepath}/EDP/space_metadata.json"
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

    # Creación y actualización del metadato del espacio en Confluence:
    def _space_metadata(self, path: str, space: str, pagesid: list[str]):
        # TODO si el archivo no existe / actualización del archivo
        # Lectura de las claves ID y valores Lastupdate: de los metadatos de cada page para el registro en pages
        # Lectura de la fecha de última actualización:
        lastupdatepages = []

        for id in pagesid:
            page_path = f"{path}/{space}/{id}"
            metadatapath = os.path.join(page_path, "metadata.json")
            with open(metadatapath, "r") as f:
                # captura de los datos del metadato de cada page
                data = json.load(f)
            lastupdatepages.append(data["lastUpdated"]["when"])
        # fecha en formato ISO 8601 y 'Z' al final
        ahora = datetime.now(timezone.utc)
        iso_time = ahora.isoformat(
            timespec='milliseconds').replace('+00:00', 'Z')
        # Estructura del archivo nuevo
        spacedata = {
            "name": f"{space}",
            "version": 0,
            "when": f"{iso_time}",
            "pages": {}
        }

        # Ruta del archivo
        file_path = f"{path}/{space}"
        # Cración del archivo vacío
        file = os.path.join(file_path, "metadata.json")

        with open(file, "w", encoding="utf-8") as f:
            json.dump(spacedata, f, ensure_ascii=False, indent=4)

    def prueba(self):
        """Insertando la hora de registro
        ahora = datetime.now(timezone.utc)
        # fecha en formato ISO 8601 y 'Z' al final: ejemplo 2025-06-19T16:20:05.386Z
        date_iso = ahora.isoformat(
            timespec='milliseconds').replace('+00:00', 'Z')
        print(date_iso)"""
        """Funciónes dentro de funciones
        a = "función externa"

        def funcioninterna():
            print(a)
        funcioninterna()"""
