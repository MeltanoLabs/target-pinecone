"""Pinecone target sink class, which handles writing streams."""

from __future__ import annotations

import hashlib

from singer_sdk.sinks import BatchSink
from singer_sdk.helpers.capabilities import TargetLoadMethods
from target_pinecone.client import PineconeWrapper

class PineconeSink(BatchSink):
    """Pinecone target sink class."""

    max_size = 100  # Max records to write in one batch

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = None

        index_name = self.config["index_name"]
        if self.client.index_exists(index_name):
            self.logger.info(f"Index `{index_name}` found")
            if self.config["load_method"] == TargetLoadMethods.OVERWRITE:
                if self.client.index_has_vectors(index_name):
                    self.logger.info(f"Deleting index because load_method is {TargetLoadMethods.OVERWRITE}")
                    self.client.recreate_index(index_name)
                else:
                    self.logger.info(f"The load_method is {TargetLoadMethods.OVERWRITE} but the index is empty, not re-creating.")
        else:
            self.client.create_index(
                index_name,
                self.config["dimensions"]
            )

    @property
    def client(self) -> PineconeWrapper:
        if not self._client:
            self._client = PineconeWrapper(
                self.config["api_key"],
                self.config["environment"],
                self.logger,
            )
        return self._client

    @property
    def document_text_property(self) -> str:
        return self.config["document_text_property"]

    @property
    def metadata_property(self) -> str:
        return self.config["metadata_property"]

    @property
    def embeddings_property(self) -> str:
        return self.config["embeddings_property"]

    @property
    def pinecone_metadata_text_key(self) -> str:
        return self.config["pinecone_metadata_text_key"]

    def process_record(self, record: dict, context: dict) -> None:
        if "records" not in context:
            context["records"] = []

        text = record[self.document_text_property]
        embedding = [float(deci) for deci in record[self.embeddings_property]]
        metadata = record[self.metadata_property]
        metadata[self.pinecone_metadata_text_key] = text
        # calculate an md5 hash of the document text
        if not self.key_properties:
            id = hashlib.md5(
                record[self.document_text_property].encode("utf-8")
            ).hexdigest()
        else:
            id = ":".join([record[key] for key in self.key_properties])

        context["records"].append(
            (id, embedding, metadata)
        )

    def process_batch(self, context: dict) -> None:
        """Write out any prepped records and return once fully written.

        Args:
            context: Stream partition or context dictionary.
        """
        self.client.upsert(
            self.config["index_name"],
            context["records"],
        )
