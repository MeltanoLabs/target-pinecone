# `target-pinecone`

Singer target for [Pinecone](https://www.pinecone.io/).

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Capabilities

* `about`
* `stream-maps`
* `schema-flattening`

## Settings

| Setting                   | Required | Default | Description |
|:--------------------------|:--------:|:-------:|:------------|
| api_key                   | True     | None    | Your Pinecone API key. |
| index_name                | True     | None    | Your Pinecone index name to write data to. |
| environment               | False    | None    | Your Pinecone index name to write data to. |
| document_text_property    | True     | text    | The property containing the document text in the input records. |
| embeddings_property       | False    | embeddings | The property containing the embeddings in the input records. |
| metadata_property         | False    | metadata | The property containing the document metadata in the input records. |
| pinecone_metadata_text_key| True     | text    | The key in the Pinecone metadata entry that will contain the text document. |
| dimensions                | False    |    1536 | The amount of dimensions to use if creating a new index. An index is only created if it doesn't already exist. The default is `1536` which is the dimensions of the embeddings using OpenAI's text-embedding-ada-002 model. |
| add_record_metadata       | False    | None    | Add metadata to records. |
| load_method               | False    | append-only | The method to use when loading data into the destination. `append-only` will always write all input records whether that records already exists or not. `upsert` will update existing records and insert new records. `overwrite` will delete all existing records and insert all input records. |
| stream_maps               | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config         | False    | None    | User-defined config values to be used within map expressions. |
| flattening_enabled        | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth      | False    | None    | The max depth to flatten schemas. |

A full list of supported settings and capabilities is available by running: `target-pinecone --about`

## Supported Python Versions

* 3.8
* 3.9
* 3.10
* 3.11

## Usage

You can easily run `target-pinecone` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Target Directly

This target expects the input data to already have embeddings pre-processed so you will either need to extract from a source containing embeddings or use something like the [map-gpt-embeddings](https://github.com/MeltanoLabs/map-gpt-embeddings) mapper to generate embeddings on the fly.

```bash
target-pinecone --version
target-pinecone --help
# Test using the "Carbon Intensity" sample:
cat embeddings.singer | target-pinecone --config /path/to/target-pinecone-config.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `target-pinecone` CLI interface directly using `poetry run`:

```bash
poetry run target-pinecone --help
```

### Testing with [Meltano](https://meltano.com/)

_**Note:** This target will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd target-pinecone
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke target-pinecone --version
# OR run a test `elt` pipeline with the Carbon Intensity sample tap and map-gpt-embeddings:
meltano run tap-carbon-intensity map-gpt-embeddings target-pinecone
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the Meltano Singer SDK to
develop your own Singer taps and targets.
