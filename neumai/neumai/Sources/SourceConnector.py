from Connectors.Connector import Connector
from Connectors import as_connector
from Chunkers.Chunker import Chunker
from Chunkers import as_chunker
from Loaders.Loader import Loader
from Loaders import as_loader
from neumai_tools import NeumDocument
from typing import List, Generator
from Shared.LocalFile import LocalFile
from Shared.CloudFile import CloudFile
from starlette.exceptions import HTTPException
from datetime import datetime
from abc import ABC

class SourceConnector(ABC):
    def __init__(self, connector:Connector, chunker:Chunker = None, loader:Loader = None, customMetadata:dict = {}):
        self.connector = connector
        self.chunker = chunker
        self.loader = loader
        self.customMetadata = customMetadata
    
    # Add validation step to check compatibility between connectors, chunkers, loaders

    def list_files_full(self) -> Generator[CloudFile, None, None]:
        yield from self.connector.connect_and_list_full()

    def list_files_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        yield from self.connector.connect_and_list_delta(last_run=last_run)

    def download_files(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        yield from self.connector.connect_and_download(cloudFile=cloudFile)

    def load_data(self, file:LocalFile) -> Generator[NeumDocument, None, None]:
        yield from self.loader.load(file=file)

    def chunk_data(self, document:NeumDocument) -> Generator[List[NeumDocument], None, None]:
        yield from self.chunker.chunk(documents=[document])
    
    def validation(self) -> bool:
        core_validation = self.connector.validate() and self.loader.validate() and self.chunker.validate()
        loader_validation = self.loader.loader_name in self.connector.compatible_loaders
        return core_validation and loader_validation

    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['customMetadata'] = self.customMetadata
        json_to_return['connector'] = self.connector.toJson()
        json_to_return['chunker'] = self.chunker.toJson()
        json_to_return['loader'] = self.loader.toJson()
        return json_to_return
    
    def to_model(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..
        This is different han toJson, here we use it to create a model, we don't want to return the api key in the body back. Eventualyl this should be its own class...
        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['customMetadata'] = self.customMetadata
        json_to_return['connector'] = self.connector.to_model()
        json_to_return['chunker'] = self.chunker.to_model()
        json_to_return['loader'] = self.loader.to_model()
        return json_to_return

    def as_source_connector(dct:dict):
        if dct == None:
            raise HTTPException(status_code=500, detail="[x001] An error occured on our end, please email kevin@tryneum.com to unblock you!")
        return SourceConnector(
            customMetadata=dct.get('customMetadata', {}),
            connector=as_connector(dct.get("connector", None)),
            chunker=as_chunker(dct.get("chunker", None)),
            loader=as_loader(dct.get("loader", None))
        )
