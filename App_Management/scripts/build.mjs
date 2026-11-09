import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const root = resolve(import.meta.dirname, '..')
const dist = resolve(root, 'dist')
const source = await readFile(resolve(root, 'src/App.tsx'), 'utf8')
const required = ['선박 관리', '운행 위치', '재고 관리', '재고 요청', '요청하기', '요청 내역', 'addRequestState', 'requestedAt', 'Manus', 'Wuvulu', '항로A', '항로B', 'medicineKey', 'transfer', 'reduceMedicines', '재고 수량 삭제', 'SAILING_DURATION_MS', 'DOCK_DURATION_MS', 'getJourneyMilestones', '정박 시작 · 10초', '전체 항구 타임라인', '최신 기록부터', 'b.at.localeCompare(a.at)', 'formatEventTimestamp', 'event.island', 'startJourney', 'portEvents', 'manus-health-facility-islands-map.png']

for (const value of required) {
  if (!source.includes(value)) throw new Error(`필수 구현 누락: ${value}`)
}
if (/^\s*(import|export)\s/m.test(source)) throw new Error('오프라인 빌드 소스에 외부 모듈 참조가 있습니다.')

await rm(dist, { recursive: true, force: true })
await mkdir(resolve(dist, 'vendor'), { recursive: true })
await mkdir(resolve(dist, 'assets'), { recursive: true })
await Promise.all([
  cp(resolve(root, 'src/styles.css'), resolve(root, 'styles.css')),
  writeFile(resolve(root, 'app.js'), source),
  cp(resolve(root, 'index.html'), resolve(dist, 'index.html')),
  cp(resolve(root, 'src/styles.css'), resolve(dist, 'styles.css')),
  cp(resolve(root, 'vendor/react.production.min.js'), resolve(dist, 'vendor/react.production.min.js')),
  cp(resolve(root, 'vendor/react-dom.production.min.js'), resolve(dist, 'vendor/react-dom.production.min.js')),
  cp(resolve(root, 'assets'), resolve(dist, 'assets'), { recursive: true }),
  writeFile(resolve(dist, 'app.js'), source),
])

console.log('Build complete: root index.html and dist/index.html')
