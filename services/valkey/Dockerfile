FROM valkey/valkey:alpine3.23

WORKDIR /app

COPY valkey/entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

EXPOSE 6379

ENTRYPOINT ["/app/entrypoint.sh"]
