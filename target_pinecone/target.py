"""Pinecone target class."""

from __future__ import annotations

from singer_sdk import typing as th
from singer_sdk.target_base import Target

from target_pinecone.sinks import (
    PineconeSink,
)


class TargetPinecone(Target):
    """Singer target for Pinecone."""

    name = "target-pinecone"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,
            description="Your Pinecone API key.",
        ),
        th.Property(
            "index_name",
            th.StringType,
            required=True,
            description="Your Pinecone index name to write data to.",
        ),
        th.Property(
            "environment",
            th.StringType,
            description="Your Pinecone index name to write data to.",
            examples=["us-west1-gcp"],
        ),
        th.Property(
            "document_text_property",
            th.StringType,
            description="The property containing the document text in the input records.",
            default="text",
            required=True,
        ),
        th.Property(
            "embeddings_property",
            th.StringType,
            description="The property containing the embeddings in the input records.",
            default="embeddings",
        ),
        th.Property(
            "metadata_property",
            th.StringType,
            description="The property containing the document metadata in the input records.",
            default="metadata",
        ),
        th.Property(
            "pinecone_metadata_text_key",
            th.StringType,
            description="The key in the Pinecone metadata entry that will contain the text document.",
            default="text",
            required=True,
        ),
        th.Property(
            "dimensions",
            th.IntegerType,
            description="The amount of dimensions to use if creating a new index. "
                "An index is only created if it doesn't already exist. "
                "The default is `1536` which is the dimensions of the embeddings using OpenAI's text-embedding-ada-002 model.",
            default=1536,
        ),
    ).to_dict()

    default_sink_class = PineconeSink


if __name__ == "__main__":
    TargetPinecone.cli()
