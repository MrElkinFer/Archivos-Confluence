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
    def downloader_pages_from_space_md(self, space, pageid: list[str] | None = None):

        space_root_path = f"knowledge/confluence/spaces/"
        pagesid = []

        # Sí llega pageid descarga solo el contenido "body.storage.value" en get_page_by_id
        if pageid is not None:
            try:
                for id in pageid:
                    page = self.confluence.get_page_by_id(
                        id, expand="body.storage")
                    pages.append(page)
            except Exception as e:
                print(f"Error inesperado: {e}")
        # Si no llega pageid se asume que se debe descargar todos los archivos del espacio
        else:
            pages = self._pages_from_space(space)
            self._space_metadata(space=space, path=space_root_path)

        # Se genera cada página obtenida en "pages" en formato markdown
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

        # Creación del metadato del espacio
        self._space_metadata(path=space_root_path,
                             space=space, pagesid=pageid)

    # Envía petición para verificar cambios en un espacio. Si hay cambios actualiza en local
    def read_and_update_space(self, localpath, space):

        # 1. Carga de información desde el metadato del espacio: número del documento y fecha de actualización
        try:
            path = f"{localpath}/{space}/space_metadata.json"
            with open(path, "r") as f:
                data = json.load(f)
                # Parejas ordenadas "id": "lastUpdate" del metadato en el space:
            localpaires = data["pages"]
        except FileNotFoundError:
            print(
                f"El directorio o espacio indicados no existen\n   Directorio: {localpath}\n   Espacio: {space}\n\n")
        except FileExistsError:
            print(
                f"El directorio o espacio indicados no existen\n   Directorio: {localpath}\n   Espacio: {space}\n\n")

        # 2. Carga de los datos actuales de las páginas en linea:
        pairs = {}
        pages = self._pages_from_space(space)
        for page in pages:
            idpage = page["id"]
            pagehistory = self.confluence.history(idpage)
            lastUpdate = pagehistory["lastUpdated"]["when"]
            pairs[idpage] = lastUpdate

        # 3. Comparación entre pares locales y pares obtenidos o actuales en linea:
        if pairs == localpaires:
            print(f"L98: No hay cambios en el espacio: {space}")
        else:
            # fecha en formato ISO 8601 y 'Z' al final
            ahora = datetime.now(timezone.utc)
            iso_time = ahora.isoformat(
                timespec='milliseconds').replace('+00:00', 'Z')
            # lista de id de las páginas que no están en local (páginas nuevas)
            newpairs = list(set(pairs.keys())-set(localpaires.keys()))
            # lista de id de las páginas que fueron eliminadas en confluence
            deletepairs = list(set(localpaires.keys())-set(pairs.keys()))
            if newpairs:
                for new in newpairs:
                    data["updates"] = f"UPDATE - {iso_time}"
                # En caso de que se creen y borren páginas en el espacio
                self.downloader_pages_from_space_md(
                    space=space, pageid=newpairs)
            if deletepairs:
                for deleted in deletepairs:
                    del data["pages"][deleted]
                    data["updates"][deleted] = f"DELETE - {iso_time}"

    # Creación y actualización del metadato del espacio:

    def _space_metadata(self, path: str, space: str, pagesid: list[str] | None = None):
        # Ruta del archivo
        file_path = f"{path}/{space}"
        # Creación de la ruta del archivo vacío
        file = os.path.join(file_path, "space_metadata.json")
        # verificación de la existencia del archivo space_metadata.json:
        update = os.path.isfile(file)
        # fecha en formato ISO 8601 y 'Z' al final
        ahora = datetime.now(timezone.utc)
        iso_time = ahora.isoformat(
            timespec='milliseconds').replace('+00:00', 'Z')

        # En caso de actualización:
        if update:
            with open(file, "r", encoding="utf-8") as f:
                spacedata = json.load(f)
            version = spacedata["version"]
            version += 1
            spacedata["version"] = version
            spacedata["when"] = iso_time
            spacedata["name"] = space
            updatedref = "UPDATE"

        # Esquema del metadato en caso de espacio nuevo
        else:
            spacedata = {
                "name": f"{space}",
                "version": 1,
                "when": f"{iso_time}",
                "pages": {},
                "updates": {}
            }
            updatedref = "REGISTER"

        # Escritura de los pares "ID: LastUpdated.when"
        for id in pagesid:
            page_path = f"{path}/{space}/{id}"
            metadatapath = os.path.join(page_path, "metadata.json")
            with open(metadatapath, "r") as f:
                # captura de los datos del metadato de cada page
                data = json.load(f)
            # Ingresando los pares clave-valor a el archivo spacedata:
            spacedata["pages"][id] = data["lastUpdated"]["when"]
            spacedata["updates"][id] = f"{updatedref} - {iso_time}"

            # Guardando el metadato del espacio
        with open(file, "w", encoding="utf-8") as f:
            json.dump(spacedata, f, ensure_ascii=False, indent=4)

    # Se encarga de actualizar escribir el id: "Cambio - LastUpdate"
    def _writer_update(self, )
