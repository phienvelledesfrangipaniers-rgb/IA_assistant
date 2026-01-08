FROM pgvector/pgvector:pg16

COPY sql /docker-entrypoint-initdb.d
RUN chown -R postgres:postgres /docker-entrypoint-initdb.d
