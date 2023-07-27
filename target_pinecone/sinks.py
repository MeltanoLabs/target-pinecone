"""Pinecone target sink class, which handles writing streams."""

from __future__ import annotations

import hashlib

import pinecone
from singer_sdk.sinks import BatchSink


class PineconeSink(BatchSink):
    """Pinecone target sink class."""

    max_size = 100  # Max records to write in one batch

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        index_name = self.config["index_name"]
        pinecone.init(
            api_key=self.config["api_key"],
            environment=self.config["environment"],
        )

        if index_name not in pinecone.list_indexes():
            # we create a new index
            pinecone.create_index(
                name=index_name,
                metric='cosine',
                dimension=self.config["dimensions"]
            )
        self.index = pinecone.Index(index_name)

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
        self.index.upsert(
            vectors=context["records"],
        )
