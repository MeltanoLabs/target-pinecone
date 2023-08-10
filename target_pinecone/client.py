import pinecone
import time

class PineconeWrapper:

    def __init__(
            self,
            api_key,
            environment,
            logger
    ):
        pinecone.init(
            api_key=api_key,
            environment=environment,
        )
        self.logger = logger

    def index_exists(self, index_name) -> bool:
        if index_name in pinecone.list_indexes():
            return True
        else:
            return False

    def upsert(self, index_name, vectors):
        pinecone.Index(index_name).upsert(vectors=vectors)

    def recreate_index(self, index_name):
        index_spec = pinecone.Index(index_name).describe_index_stats()
        pinecone.delete_index(index_name)
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
        self.wait_until_index_ready()

    def create_index(self, index_name, dimensions):
        pinecone.create_index(
            name=index_name,
            metric='cosine',
            dimension=dimensions,
            # Wait a max of 10 minutes to create index, it should never take this long
            timeout=600,
        )
        self._wait_until_index_ready()

    def index_has_vectors(self, index_name):
        index = pinecone.Index(index_name)
        stats = index.describe_index_stats()
        if stats["total_vector_count"] > 0:
            return True
        else:
            return False

    def _wait_until_index_ready(self, index_name):
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
