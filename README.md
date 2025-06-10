# SDG-Indexer

Scalable SDG Indexing for the SDG Dashboard

## Rationale 

The SDG Indexer analyses any incoming records and identifies the SDGs that are associated with the record. This Indexer uses a matching term approach to identify the SDGs. The matching terms are provided via a separate repository (see [keywords](https://github.com/sustainability-zhaw/keywords)). The indexer listens to system events to capture new matching terms or new records. The indexer uses a two step approach to identify the SDGs:

1. Isolate a candidate set of potential mathing elements (either matching terms or information objects).
2. NLP-based matching of the candidate set with the given record.

The SDG Indexer is designed to be horizontally scalable and can be run with multiple replicas. Running multiple replicas can speed up the indexing process significantly, if many overlapping indexing requests are received.

## Configuration

The SDG-Indexer is configured via a configuration file that contains a JSON object. The configuration file is mounted into the container at `/etc/app/config.json`.

The following options can be configured:

`DB_HOST` - The hostname of the dgraph database.
`BATCH_SIZE` - Number of records that are processed in a single batch. Default is `100`.
`BATCH_INTERVAL` - Interval in seconds to wait between two batches. Default is `180` (3 Minutes). 
`LOG_LEVEL` - Log level for the indexer. Default is `DEBUG`. Set the log level to `INFO` or `WARNING` for production.
`MQ_HOST` - Hostname of the AQMP message queue. Default is `mq`. 
`MQ_EXCHANGE` - Name of the message queue exchange. Default is `zhaw-km`.
`MQ_QUEUE` - Name of the indexer's message queue. Default is `indexerqueue`. 
`MQ_BINDKEYS` - Keys to bind the indexer's queue to the exchange. This is of type list. Default is `["indexer.*", "importer.object"]`. Keep at default for production.
`MQ_HEARTBEAT` - Seconds between two heartbeat messages to the message queue. Default is `500` seconds. This must not exceed 50 Minutes. 
`MQ_TIMEOUT` - Seconds to wait for the message queue to recover from blocked state. Default is `300` seconds. This must not exceed 50 Minutes.

The capitalisation of the configuration options is ignored.

## Architecture

The SDG-Indexer is part of a three component subsystem.

- A [dgraph-database](https://github.com/sustainability-zhaw/dgraph-schema), 
- The SDG-Indexer (this repo), and
- A [set of indexing keywords](https://github.com/sustainability-zhaw/keywords)

The SDG-Indexer identifies, which SDGs are associated with an `InfoObject` in the database. For the identification it relies on indexing keywords that are provided from GitHub. Whenever the indexing keywords are changed, the SDG-Indexer should re-index the associated SDGs with *all* `InfoObjects`. 

The indexing terms live on GitHub and are retrieved on demand via the GitHub API. Because the keyword repo is *public*, the SDG-Indexer can use the anonymous raw access using the following URL `https://raw.githubusercontent.com/sustainability-zhaw/keywords/main/data/sdgs/SDG${SDG_ID}.csv` for retrieving the indexing terms when needed.

The SDG-Indexer will listen to [GitHub-Webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks/about-webhooks) for identifying changes of the indexing terms. The webhook will listen need to [push](https://docs.github.com/de/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#push) and [merge events](https://docs.github.com/de/developers/webhooks-and-events/webhooks/webhook-events-and-payloads?actionType=closed#pull_request) on the main branch of the [keyword repository](https://github.com/sustainability-zhaw/keywords). **Note:** The webhook might get registered by a separate service. 

The indexer handles indexing requests from a message queue. This allows to run selective indexing tasks more efficiently. 

Three events trigger the indexing process:

- An update of the index term files (via webhook)
- A new index term that has been added through the UI (signaled via gql-subscription)
- New (unindexed) objects were added by one of the importers.

## Deployment

The SDG-Indexer is designed for horizontal scaling. The service should run with at least three replications, because the each indexing run is slow compared to any of the other processes.

More indexing replicas only provide more performance, if sufficient CPU is available in the cluster.

## Development

A development environment with dgraph, sample data, and dgraph ratel is provided via `docker-compose-local.yaml`.

To start the environment run the following command: 

```bash
docker compose -f docker-compose-local.yaml up --build --force-recreate --remove-orphans
```

The launch takes approx. 30 seconds. After that period an initialised dgraph database is exposed via `localhost:8080`.

## Building 

docker build -t testing .