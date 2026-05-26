# DANGER: wipes the Postgres volume. Dev only.
docker compose down -v
docker compose up -d db
