# Pinecone Vector Archival System

This system automatically archives old vectors (older than 6 months) from Pinecone to PostgreSQL to control costs while preserving historical data.

## Components

- **archival_config.json**: Configuration for the archival process
- **pinecone_archiver.py**: Core script that handles vector archival
- **scheduler.py**: Manages the scheduling of archival jobs

## How It Works

1. The system identifies vectors in Pinecone that are older than 6 months by checking the timestamp metadata.
2. These vectors are exported to PostgreSQL tables, preserving their IDs, vectors, and metadata.
3. After successful storage in PostgreSQL, the vectors are deleted from Pinecone.
4. The process runs on a scheduled basis (default: daily at 3 AM).

## Configuration Options

You can modify the following parameters in `archival_config.json`:

- `age_threshold_days`: Number of days after which vectors are archived (default: 180)
- `schedule`: Cron expression for the archival schedule (default: "0 3 * * *" - 3 AM daily)
- `batch_size`: Number of vectors to process in each batch (default: 1000)
- `dry_run`: If set to true, performs a trial run without deleting from Pinecone
- `namespaces_to_archive`: List of Pinecone namespaces to include in archival

## Setup Instructions

1. Ensure PostgreSQL tables are properly configured (handled automatically)
2. Review and adjust the configuration in `archival_config.json`
3. Run the scheduler:

```bash
python scheduler.py
```

For production deployment, you should set this up as a service using systemd or Docker.

## Database Schema

For each namespace, a corresponding PostgreSQL table is created with the following schema:

- `id`: Serial primary key
- `vector_id`: Original vector ID from Pinecone
- `namespace`: Source namespace
- `vector`: Array of float values representing the embedding
- `archived_at`: Timestamp when the vector was archived
- Additional columns for each metadata field defined in the namespace configuration

## Logging

Logs are stored in `/var/log/cherry/archival.log` and include details about:
- Number of vectors archived
- Any errors encountered during the process
- Timing information

## Monitoring

To monitor the archival process:
- Check log files for errors
- Query PostgreSQL to see archived vector counts
- Check Pinecone metrics to ensure vector counts are decreasing as expected
