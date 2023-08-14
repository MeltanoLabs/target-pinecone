"""Tests standard target features using the built-in SDK tests library."""

from __future__ import annotations

import typing as t
from unittest import mock

from singer_sdk.testing import TargetTestRunner

from target_pinecone.target import TargetPinecone

# TODO: Initialize minimal target config
SAMPLE_CONFIG: dict[str, t.Any] = {
    "api_key": "FOO",
    "index_name": "target-pinecone-index",
    "environment": "asia-southeast1-gcp-free",
    "document_text_property": "doc_text",
    "embeddings_property": "embeddings_data",
    "metadata_property": "embedding_metadata",
    "pinecone_metadata_text_key": "text",
    "load_method": "upsert"
}

def get_mock_method_call(mock_calls, name):
    for call in mock_calls:
        if call[0] == f"().{name}":
            return call
    return None

@mock.patch('target_pinecone.sinks.PineconeWrapper')
def test_recreate_upsert(wrapper):
    SAMPLE_CONFIG["load_method"] = "overwrite"
    runner = TargetTestRunner(
        TargetPinecone,
        config=SAMPLE_CONFIG,
        input_filepath="tests/target_test_streams/test_stream.singer"
    )
    runner.sync_all()
    assert get_mock_method_call(wrapper.mock_calls, "recreate_index") is not None
    assert get_mock_method_call(wrapper.mock_calls, "upsert").args == ('target-pinecone-index', [('123', [1.0, 2.0], {'key': 'val', 'text': 'foo'})])

@mock.patch('target_pinecone.sinks.PineconeWrapper')
def test_existing_append_upsert(wrapper):
    runner = TargetTestRunner(
        TargetPinecone,
        config=SAMPLE_CONFIG,
        input_filepath="tests/target_test_streams/test_stream.singer"
    )
    runner.sync_all()
    assert get_mock_method_call(wrapper.mock_calls, "create_index") is None
    assert get_mock_method_call(wrapper.mock_calls, "upsert").args == ('target-pinecone-index', [('123', [1.0, 2.0], {'key': 'val', 'text': 'foo'})])

@mock.patch('target_pinecone.sinks.PineconeWrapper')
def test_non_existing_upsert(wrapper):
    wrapper.return_value.index_exists.return_value = False
    runner = TargetTestRunner(
        TargetPinecone,
        config=SAMPLE_CONFIG,
        input_filepath="tests/target_test_streams/test_stream.singer"
    )
    runner.sync_all()
    assert get_mock_method_call(wrapper.mock_calls, "create_index") is not None
    assert get_mock_method_call(wrapper.mock_calls, "upsert").args == ('target-pinecone-index', [('123', [1.0, 2.0], {'key': 'val', 'text': 'foo'})])
