from atlassian import Confluence
from markdownify import markdownify
import os
import json
import shutil
from datetime import datetime, timezone


class ConfluenceSpaceDocumentDownloader:

    def __init__(self, url, username, token):
        self.confluence = Confluence(
            url=url,
            username=username,
            password=token,
        )

    # Descarga las páginas de un espacio determinado
    def _pages_from_space(self, space: str, start=0, limit=100):
        pages = self.confluence.get_all_pages_from_space(
            space=space,
            start=start,
            expand='body.storage',
            limit=limit,
        )
        return pages

    # Guarda las páginas en una carpeta local en formato markdown
    def Downloader_pages_from_space_md(self, space, pageid: list[str] | None = None):

        space_root_path = f"knowledge/confluence/spaces/"
        pagesid = []
        pages = []

        # Sí llega pageid descarga solo el contenido "body.storage.value" en get_page_by_id
        if pageid is not None:
            for id in pageid:
                page = self.confluence.get_page_by_id(
                    id, expand="body.storage")
                pages.append(page)
                pagesid.append(id)

        # Si no llega pageid se asume que se debe descargar todos los archivos del espacio
        else:
            pages = self._pages_from_space(space)
            for page in pages:
                pagesid.append(page["id"])

        # Se genera cada página obtenida en "pages" en formato markdown
        for page in pages:
            html = page["body"]["storage"]["value"]
            content_md = markdownify(html)
            page_id = page["id"]
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

        # Creación del metadato del espacio
        self._space_metadata(path=space_root_path,
                             space=space, pagesid=pagesid)

    # Envía petición para verificar cambios en un espacio. Si hay cambios actualiza en local
    def Read_and_update_space(self, localpath, space):
        localpaires = None

        # 1. Carga de información desde el metadato del espacio: número del documento y fecha de actualización
        try:
            path = f"{localpath}/{space}/space_metadata.json"
            with open(path, "r") as f:
                data = json.load(f)
                # Parejas ordenadas "id": "lastUpdate" del metadato en el space:
            localpaires = data["pages"]
        except FileNotFoundError:
            return print(
                f"El directorio o espacio indicados no existen\n   Directorio: {localpath}\n   Espacio: {space}")
        except FileExistsError:
            return print(
                f"El directorio o espacio indicados no existen\n   Directorio: {localpath}\n   Espacio: {space}")

        # 2. Carga de los datos actuales de las páginas en linea:
        pairs = {}
        createdAt = {}

        pages = self._pages_from_space(space)
        for page in pages:
            idpage = page["id"]
            pagehistory = self.confluence.history(idpage)
            lastUpdate = pagehistory["lastUpdated"]["when"]
            createdAt[idpage] = pagehistory["createdDate"]
            pairs[idpage] = lastUpdate

        # 3. Comparación entre pares locales y pares obtenidos o actuales en linea:
        if pairs == localpaires:
            print(f"L101: No hay cambios en el espacio: {space}")
        else:

            updatedkeys = []
            keys = set(pairs.keys())
            localkeys = set(localpaires.keys())

            # lista de id de las páginas que no están en local (páginas nuevas)
            newpairs = list(keys-localkeys)

            # lista de id de las páginas que fueron eliminadas en confluence
            deletepairs = list(localkeys-keys)

            if newpairs:
                for news in newpairs:
                    if news not in data["updates"]:
                        data["updates"][news] = []
                    data["updates"][news].append(
                        f"CREATED - {createdAt[news]}")
                    data["updates"][news].append(
                        f"REGISTER - {pairs[news]}")
                    data["pages"][news] = pairs[news]
                self.Downloader_pages_from_space_md(
                    space=space, pageid=newpairs)

            if deletepairs:
                for deleted in deletepairs:
                    pagepath = f"{localpath}/{space}/{deleted}"
                    shutil.rmtree(path=pagepath)
                    del data["pages"][deleted]
                    if deleted not in data["updates"]:
                        data["updates"][deleted] = []
                    data["updates"][deleted].append(
                        f"DELETE - {self._iso_time()}")

            for id in pairs:
                if id in localpaires and pairs[id] != localpaires[id]:
                    if id not in data["updates"]:
                        data["updates"][id] = []
                    data["updates"][id].append(
                        f"UPDATED - {pairs[id]}")
                    # Guarda la actualización de la pareja ID y lastUpdate en el metadato del espacio:
                    data["pages"][id] = pairs[id]
                    updatedkeys.append(id)
                self.Downloader_pages_from_space_md(
                    space=space, pageid=updatedkeys)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # Creación y actualización del metadato del espacio:
    def _space_metadata(self, path: str, space: str, pagesid: list[str] | None = None):
        # Ruta del archivo
        file_path = f"{path}/{space}"
        # Creación de la ruta del archivo vacío
        file = os.path.join(file_path, "space_metadata.json")
        # verificación de la existencia del archivo space_metadata.json:
        update = os.path.isfile(file)

        # En caso de actualización o nueva página:
        if update:
            with open(file, "r", encoding="utf-8") as f:
                spacedata = json.load(f)
            version = spacedata["version"]
            version += 1
            spacedata["version"] = version
            spacedata["last_update"] = self._iso_time()
            spacedata["name"] = space

        # Esquema del metadato en caso de espacio nuevo
        else:
            spacedata = {
                "name": f"{space}",
                "version": 1,
                "when": f"{self._iso_time()}",
                "lastUpdate": f"{self._iso_time()}",
                "pages": {},
                "updates": {}
            }

        # Escritura de los pares "ID: LastUpdated.when"
        for id in pagesid:
            page_path = f"{path}/{space}/{id}"
            metadatapath = os.path.join(page_path, "metadata.json")
            with open(metadatapath, "r", encoding="utf-8") as f:
                # captura de los datos del metadato de cada page
                data = json.load(f)
            # En caso de que el archivo meatadato del espacio exista pero se actualice la página:

            # si el metadato del espacio no existe crea los registros en la sección "pages"
            if not update:
                if id not in spacedata["updates"]:
                    spacedata["updates"][id] = []
                spacedata["updates"][id].append(
                    f"CREATED - {data["createdDate"]}")
                spacedata["updates"][id].append(
                    f"REGISTER - {self._iso_time()}")
                spacedata["pages"][id] = data["lastUpdated"]["when"]

        # Guardando el metadato del espacio
        with open(file, "w", encoding="utf-8") as f:
            json.dump(spacedata, f, ensure_ascii=False, indent=4)

    # Función encargada de dar fecha del momento que se llama
    def _iso_time(self) -> str:
        # fecha en formato ISO 8601 y 'Z' al final
        ahora = datetime.now(timezone.utc)
        iso_time = ahora.isoformat(
            timespec='milliseconds').replace('+00:00', 'Z')
        return iso_time
