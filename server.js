const http = require('http');
const fs   = require('fs');
const path = require('path');
const PORT = 3002;
const ROOT = __dirname;
const mime = { '.html':'text/html','.css':'text/css','.js':'text/javascript','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.ico':'image/x-icon','.webp':'image/webp' };
http.createServer((req, res) => {
  let u = req.url.split('?')[0];
  if (u === '/') u = '/index.html';
  const fp = path.join(ROOT, u);
  const ext = path.extname(fp);
  fs.readFile(fp, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not found'); return; }
    res.writeHead(200, { 'Content-Type': mime[ext] || 'text/plain' });
    res.end(data);
  });
}).listen(PORT, () => console.log(`Arizona Chimney Pros running on http://localhost:${PORT}`));
