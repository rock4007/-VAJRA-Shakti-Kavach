// Healthcheck for the frontend container (distroless/nodejs20).
// Loaded by '/nodejs/bin/node /app/healthcheck.mjs' inside the container.
import http from 'node:http';

const port = process.env.PORT || '4173';

http.get(`http://127.0.0.1:${port}/`, (res) => {
  process.exit(res.statusCode === 200 ? 0 : 1);
}).on('error', () => process.exit(1));
