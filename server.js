const http = require("node:http");
const fs = require("node:fs");
const fsp = require("node:fs/promises");
const path = require("node:path");
const { Readable } = require("node:stream");

const PORT = Number(process.env.PORT || 3000);
const HOST = process.env.HOST || "127.0.0.1";
const ROOT = __dirname;
const REMOTE_ORIGIN = "https://medi-mitra-sand.vercel.app";

const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".woff": "font/woff",
  ".woff2": "font/woff2"
};

function isProxyPath(urlPath) {
  return (
    urlPath.startsWith("/api/") ||
    urlPath === "/api" ||
    urlPath.startsWith("/socket.io/")
  );
}

function safeJoin(rootDir, requestPath) {
  const resolved = path.resolve(rootDir, "." + requestPath);
  if (!resolved.startsWith(rootDir)) {
    return null;
  }
  return resolved;
}

async function proxyRequest(req, res) {
  const targetUrl = new URL(req.url, REMOTE_ORIGIN);
  const headers = new Headers();

  for (const [name, value] of Object.entries(req.headers)) {
    if (!value) continue;
    if (["host", "connection", "content-length"].includes(name.toLowerCase())) {
      continue;
    }
    headers.set(name, Array.isArray(value) ? value.join(", ") : value);
  }

  headers.set("host", new URL(REMOTE_ORIGIN).host);
  headers.set("origin", REMOTE_ORIGIN);
  headers.set("referer", `${REMOTE_ORIGIN}/`);

  const method = req.method || "GET";
  const init = {
    method,
    headers,
    redirect: "manual"
  };

  if (!["GET", "HEAD"].includes(method)) {
    init.body = req;
    init.duplex = "half";
  }

  try {
    const upstream = await fetch(targetUrl, init);

    res.statusCode = upstream.status;
    res.statusMessage = upstream.statusText;

    upstream.headers.forEach((value, key) => {
      if (
        ["connection", "content-encoding", "content-length", "transfer-encoding"].includes(
          key.toLowerCase()
        )
      ) {
        return;
      }
      res.setHeader(key, value);
    });

    if (!upstream.body) {
      res.end();
      return;
    }

    Readable.fromWeb(upstream.body).pipe(res);
  } catch (error) {
    res.statusCode = 502;
    res.setHeader("content-type", "application/json; charset=utf-8");
    res.end(
      JSON.stringify({
        error: "proxy_error",
        message: error instanceof Error ? error.message : String(error)
      })
    );
  }
}

async function serveFile(filePath, res) {
  try {
    const stats = await fsp.stat(filePath);
    if (!stats.isFile()) {
      res.statusCode = 404;
      res.end("Not found");
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    res.statusCode = 200;
    res.setHeader(
      "content-type",
      contentTypes[ext] || "application/octet-stream"
    );
    fs.createReadStream(filePath).pipe(res);
  } catch {
    res.statusCode = 404;
    res.end("Not found");
  }
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url || "/", `http://${req.headers.host || HOST}`);
  const pathname = decodeURIComponent(url.pathname);

  if (isProxyPath(pathname)) {
    await proxyRequest(req, res);
    return;
  }

  if (pathname === "/" || pathname === "/index.html") {
    await serveFile(path.join(ROOT, "index.html"), res);
    return;
  }

  const requestedFile = safeJoin(ROOT, pathname);
  if (requestedFile && fs.existsSync(requestedFile)) {
    await serveFile(requestedFile, res);
    return;
  }

  await serveFile(path.join(ROOT, "index.html"), res);
});

if (require.main === module) {
  server.listen(PORT, HOST, () => {
    console.log(`Medi Mitra clone running at http://${HOST}:${PORT}`);
  });
}

module.exports = server;
