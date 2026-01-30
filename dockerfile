FROM cockroachdb/cockroach:v24.1.8

EXPOSE 26257 8080

CMD ["start-single-node", "--insecure"]