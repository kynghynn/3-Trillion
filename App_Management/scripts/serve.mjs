import { createReadStream, existsSync, statSync } from 'node:fs'
import { createServer } from 'node:http'
import { extname, join, normalize, resolve } from 'node:path'

const root = resolve(import.meta.dirname, '../dist')
const port = Number(process.env.PORT || 4173)
const types = { '.css': 'text/css', '.html': 'text/html', '.js': 'text/javascript' }

createServer((request, response) => {
  const pathname = decodeURIComponent((request.url || '/').split('?')[0])
  const requested = normalize(join(root, pathname))
  const file = requested.startsWith(root) && existsSync(requested) && statSync(requested).isFile()
    ? requested
    : join(root, 'index.html')
  response.setHeader('Content-Type', `${types[extname(file)] || 'application/octet-stream'}; charset=utf-8`)
  createReadStream(file).pipe(response)
}).listen(port, '0.0.0.0', () => console.log(`Preview: http://localhost:${port}`))
