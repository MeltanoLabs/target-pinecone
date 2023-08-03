"""Pinecone target sink class, which handles writing streams."""

from __future__ import annotations

import hashlib

import pinecone
import time
from singer_sdk.sinks import BatchSink
from singer_sdk.helpers.capabilities import TargetLoadMethods

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
        if index_name in pinecone.list_indexes():
            self.logger.info(f"Index `{index_name}` found")
            if self.config["load_method"] == TargetLoadMethods.OVERWRITE:
                self._recreate_index(index_name)
        else:
            self.logger.info(f"Creating index `{index_name}`, this could take several minutes...")
            pinecone.create_index(
                name=index_name,
                metric='cosine',
                dimension=self.config["dimensions"],
                # Wait a max of 10 minutes to create index, it should never take this long
                timeout=600,
            )
            self.logger.info(f"Index `{index_name}` created.")
        self.index = pinecone.Index(index_name)

    def _recreate_index(self, index_name):
        index = pinecone.Index(index_name)
        index_spec = pinecone.describe_index(index_name)
        stats = index.describe_index_stats()
        if stats["total_vector_count"] > 0:
            self.logger.info(f"Deleting index because load_method is {TargetLoadMethods.OVERWRITE}")
            pinecone.delete_index(index_name)
            self.logger.info(f"Re-creating index {index_name} with existing settings, this could take several minutes...")
            pinecone.create_index(
                name=index_name,
                dimension=int(index_spec.dimension),
                metric=index_spec.metric,
                replicas=index_spec.replicas,
                shards=index_spec.shards,
                pods=index_spec.pods,
                pod_type=index_spec.pod_type,
                source_collection=index_spec.source_collection,
                metadata_config=index_spec.metadata_config,
                # Wait a max of 10 minutes to create index, it should never take this long
                timeout=600,
            )
            self.logger.info(f"Index `{index_name}` created.")
            index_spec = pinecone.describe_index(index_name)
            wait_time_s = 0
            max_wait_time_s = 300 # 5 minutes
            sleep_time_s = 10
            while not index_spec.status["ready"]:
                self.logger.info(f"Waiting for index to be ready...{wait_time_s}s /{max_wait_time_s}s Max")
                time.sleep(sleep_time_s)
                index_spec = pinecone.describe_index(index_name)
                wait_time_s += sleep_time_s
                if wait_time_s >= max_wait_time_s:
                    raise Exception(
                        f"Index `{index_name}` not ready after {wait_time_s} seconds, "
                        f"status is {index_spec.status}"
                    )
            self.logger.info("Index ready!")
        else:
            self.logger.info(f"The load_method is {TargetLoadMethods.OVERWRITE} but the index is empty, not re-creating.")

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
