from prometheus_client import Counter, Histogram

MEMORY_UPSERTED = Counter("rag_memory_upsert_total", "Total number of memory upserts")
MEMORY_DELETED = Counter("rag_memory_delete_total", "Total number of memory deletes")
MEMORY_SEARCH_TOTAL = Counter(
    "rag_memory_search_total",
    "Total number of memory searches partitioned by cache usage",
    ["cache"],
)
MEMORY_SEARCH_DURATION = Histogram(
    "rag_memory_search_duration_seconds",
    "Memory search request duration in seconds",
)
