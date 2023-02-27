# SDG-Indexer

Scalable SDG Indexing for the SDG Dashboard

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
