// Healthcheck for the frontend container (distroless/nodejs20).
// Loaded by '/nodejs/bin/node /app/healthcheck.mjs' inside the container.
import http from 'node:http';

http.get('http://127.0.0.1:4173/', (res) => {
  process.exit(res.statusCode === 200 ? 0 : 1);
}).on('error', () => process.exit(1));
