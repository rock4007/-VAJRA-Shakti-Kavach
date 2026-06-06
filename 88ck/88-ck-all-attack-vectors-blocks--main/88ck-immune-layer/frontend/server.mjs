import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { dirname } from "node:path";
import { extname, isAbsolute, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = process.env.STATIC_ROOT || join(dirname(fileURLToPath(import.meta.url)), "dist");
const rootPath = resolve(root);
const port = Number.parseInt(process.env.PORT || "4173", 10);
const mime = new Map([
  [".html", "text/html; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".svg", "image/svg+xml"],
  [".json", "application/json; charset=utf-8"]
]);

function resolveAssetPath(reqUrl = "/") {
  let pathname;
  try {
    const url = new URL(reqUrl, "http://localhost");
    pathname = decodeURIComponent(url.pathname);
  } catch {
    return null;
  }

  const assetPath = pathname === "/" ? "/index.html" : pathname;
  const resolved = resolve(join(rootPath, `.${assetPath}`));
  const rel = relative(rootPath, resolved);

  if (rel === "" || (!rel.startsWith("..") && !isAbsolute(rel))) {
    return resolved;
  }
  return null;
}

createServer(async (req, res) => {
  const filePath = resolveAssetPath(req.url);
  if (!filePath) {
    res.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("bad request");
    return;
  }

  try {
    const file = await readFile(filePath);
    res.writeHead(200, { "Content-Type": mime.get(extname(filePath)) || "application/octet-stream" });
    res.end(file);
  } catch {
    try {
      const file = await readFile(join(rootPath, "index.html"));
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(file);
    } catch {
      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("not found");
    }
  }
}).listen(port, "0.0.0.0");
