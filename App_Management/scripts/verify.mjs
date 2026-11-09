import { access, readFile } from 'node:fs/promises'
import vm from 'node:vm'
import { resolve } from 'node:path'

const root = resolve(import.meta.dirname, '..')
const source = await readFile(resolve(root, 'src/App.tsx'), 'utf8')
const css = await readFile(resolve(root, 'src/styles.css'), 'utf8')

for (const path of ['index.html', 'app.js', 'styles.css', 'vendor/react.production.min.js', 'vendor/react-dom.production.min.js', 'assets/manus-health-facility-islands-map.png', 'assets/manus-health-facility-islands.json', 'dist/index.html', 'dist/app.js', 'dist/styles.css', 'dist/assets/manus-health-facility-islands-map.png', 'dist/assets/manus-health-facility-islands.json']) {
  await access(resolve(root, path))
}

for (const label of ['선박 관리', '운행 위치', '재고 관리', '재고 요청']) {
  if (!source.includes(label)) throw new Error(`홈 기능 누락: ${label}`)
}
for (const island of ['Manus', 'Los Negros', 'Lou', 'Rambutyo', 'Luf', 'Mal', 'Aua', 'Wuvulu']) {
  if (!source.includes(island)) throw new Error(`섬 누락: ${island}`)
}
if (!source.includes("number: '111'") || !source.includes("type: '중형'")) throw new Error('초기 선박 111 정보 누락')
if (!source.includes("['미운행','항로A','항로B']")) throw new Error('확정 항로 선택지 누락')
if (!source.includes('medicineKey(candidate.name, candidate.expiry)')) throw new Error('동일 약품 합산 키 누락')
if (!source.includes("containerKey('island', island)")) throw new Error('선박에서 섬으로 재고 이전 누락')
if (!source.includes('item.quantity - quantity') || !source.includes(".filter((item) => item.quantity > 0)")) throw new Error('부분 수량 삭제 규칙 누락')
if (!source.includes('현재 수량 전부를 입력한 품목만 목록에서 삭제됩니다.')) throw new Error('수량 삭제 안내 누락')
if (source.includes('GPS가 아닌 시뮬레이션')) throw new Error('삭제 요청된 운행 위치 문구가 남아 있음')
if (!source.includes("status: '운행중'") || !source.includes("status: '미운행'")) throw new Error('선박 운행 상태 전이 누락')
if (!source.includes("location: 'Manus'") || !source.includes('frame.location')) throw new Error('시뮬레이션 위치 갱신 누락')
if (!source.includes("movement: '정박'") || !source.includes("frame.phase === '정박'")) throw new Error('정박 상태 또는 이벤트 표시 누락')
if (!source.includes('formatEventTimestamp(event.at)') || !source.includes('`${event.island} ${event.movement}`')) throw new Error('타임스탬프 또는 섬 이름 표시 누락')
if (!source.includes("useState('')") || !source.includes('전체 항구 타임라인') || !source.includes('정박 시작 · 10초')) throw new Error('전체 항구 정박 타임라인 표시 누락')
if (!source.includes('addRequestState') || !source.includes("name: 'request-history'") || !source.includes("type: 'number', min: 1, step: 1")) throw new Error('재고 요청 저장·내역·수량 입력 기능 누락')
if (source.includes("title: '재고 요청', eyebrow: '준비 중'")) throw new Error('재고 요청 준비 중 화면이 남아 있음')
const requestActionsSource = source.slice(source.indexOf("className: 'request-actions'"), source.indexOf("function RequestHistory"))
if (requestActionsSource.indexOf("'요청하기'") > requestActionsSource.indexOf("'요청 내역'")) throw new Error('재고 요청 하단 버튼 좌우 순서 오류')
if (!css.includes('@media (max-width: 650px)')) throw new Error('모바일 반응형 규칙 누락')
if (!css.includes('.event-row .docking')) throw new Error('정박 타임라인 스타일 누락')
if (!css.includes('transform: translate(-15px, -15px)') || !css.includes('.vessel-marker.docking .vessel-dot')) throw new Error('선박 마커 중심 좌표 또는 정박 상태 스타일 누락')
if (!css.includes('.request-actions') || !css.includes('justify-content: space-between') || !css.includes('.request-fields')) throw new Error('재고 요청 하단 버튼 배치 또는 입력 레이아웃 누락')

const stripped = source.replace(/ReactDOM\.createRoot[\s\S]*$/, '')
const context = {
  console,
  localStorage: { getItem() { return null }, setItem() {} },
  crypto: { randomUUID() { return 'test-id' } },
  React: {
    createElement(type, props, ...children) { return { type, props: { ...(props || {}), children: children.length <= 1 ? children[0] : children } } },
    useEffect() {},
    useMemo(value) { return value() },
    useState(value) { return [typeof value === 'function' ? value() : value, () => {}] },
  },
  ReactDOM: {},
  confirm() { return true },
}
vm.createContext(context)
vm.runInContext(stripped, context, { filename: 'src/App.tsx' })

function expand(node) {
  if (node == null || typeof node === 'string' || typeof node === 'number') return node
  if (Array.isArray(node)) return node.map(expand)
  if (typeof node.type === 'function') return expand(node.type(node.props || {}))
  return { ...node, props: { ...node.props, children: expand(node.props?.children) } }
}
function text(node) {
  if (node == null) return ''
  if (typeof node === 'string' || typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(text).join('')
  return text(node.props?.children)
}

const tree = expand(vm.runInContext('App()', context))
const renderedText = text(tree)
for (const label of ['선박 관리', '운행 위치', '재고 관리', '재고 요청']) {
  if (!renderedText.includes(label)) throw new Error(`React 렌더 트리 홈 기능 누락: ${label}`)
}
const sameKey = vm.runInContext("medicineKey('사바나', '2028-11-05') === medicineKey('사바나', '2028-11-05')", context)
const differentKey = vm.runInContext("medicineKey('사바나', '2028-11-05') !== medicineKey('사바나', '2028-11-06')", context)
if (!sameKey || !differentKey) throw new Error('약품명+유통기한 식별 규칙 오류')
const partialDelete = vm.runInContext("reduceInventory([{ id: 'tylenol', name: '타이레놀', expiry: '2028-11-05', quantity: 10 }], { tylenol: 3 })", context)
if (partialDelete.length !== 1 || partialDelete[0].quantity !== 7) throw new Error('부분 수량 삭제 계산 오류')
const fullDelete = vm.runInContext("reduceInventory([{ id: 'tylenol', name: '타이레놀', expiry: '2028-11-05', quantity: 3 }], { tylenol: 3 })", context)
if (fullDelete.length !== 0) throw new Error('전량 삭제 시 품목 제거 오류')
const savedRequestState = vm.runInContext("addRequestState({ requests: [] }, { medicineName: '  타이레놀  ', quantity: 3 }, new Date(2026, 10, 9, 20, 10, 5).getTime())", context)
if (savedRequestState.requests.length !== 1 || savedRequestState.requests[0].medicineName !== '타이레놀' || savedRequestState.requests[0].quantity !== 3 || !savedRequestState.requests[0].requestedAt) throw new Error('재고 요청 저장 계산 오류')
context.savedRequestState = savedRequestState
const secondRequestState = vm.runInContext("addRequestState(savedRequestState, { medicineName: '아목시실린', quantity: 8 }, new Date(2026, 10, 9, 20, 11, 5).getTime())", context)
if (secondRequestState.requests[0].medicineName !== '아목시실린' || secondRequestState.requests[1].medicineName !== '타이레놀') throw new Error('재고 요청 최신순 저장 오류')
const invalidRequestState = vm.runInContext("addRequestState({ requests: [] }, { medicineName: '', quantity: 0 }, 1000)", context)
if (invalidRequestState.requests.length !== 0) throw new Error('잘못된 재고 요청 차단 오류')
const requestPageTree = expand(vm.runInContext("RequestPage({ store: { addRequest() {} }, navigate() {} })", context))
const requestPageText = text(requestPageTree)
if (!requestPageText.includes('약품 이름') || !requestPageText.includes('수량') || !requestPageText.includes('요청하기') || !requestPageText.includes('요청 내역')) throw new Error('재고 요청 입력 화면 오류')
context.requestFixtures = secondRequestState.requests
const requestHistoryTree = expand(vm.runInContext("RequestHistory({ requests: requestFixtures, navigate() {} })", context))
const requestHistoryText = text(requestHistoryTree)
if (!requestHistoryText.includes('아목시실린') || !requestHistoryText.includes('8개') || requestHistoryText.indexOf('아목시실린') > requestHistoryText.indexOf('타이레놀')) throw new Error('재고 요청 내역 렌더 또는 최신순 오류')
const startFrame = vm.runInContext("getJourneyFrame({ route: '항로B', location: '', journeyStartedAt: 1000 }, 1000)", context)
if (startFrame.location !== 'Manus' || startFrame.done) throw new Error('운행 시작 위치 오류')
const routeADuration = vm.runInContext("getJourneyDuration('항로A')", context)
const routeBDuration = vm.runInContext("getJourneyDuration('항로B')", context)
if (routeADuration !== 100000 || routeBDuration !== 90000) throw new Error('항로별 운항·정박 총시간 오류')
const mapPoints = vm.runInContext('ISLAND_POINTS', context)
const expectedMapPoints = { Manus: [78.188, 70.368], 'Los Negros': [86.942, 68.165], Lou: [91.257, 69.965], Rambutyo: [94.577, 81.537], Luf: [44.273, 42.095], Mal: [28.040, 35.612], Aua: [7.464, 38.719], Wuvulu: [3.638, 52.585] }
for (const [island, [x, y]] of Object.entries(expectedMapPoints)) {
  if (mapPoints[island].x !== x || mapPoints[island].y !== y) throw new Error(`${island} 지도 표식 중심 좌표 오류`)
}
const routeAMilestones = vm.runInContext("getJourneyMilestones('항로A')", context)
const routeBMilestones = vm.runInContext("getJourneyMilestones('항로B')", context)
if (routeAMilestones.filter((item) => item.movement === '정박').length !== 4) throw new Error('항로A 정박 이벤트 수 오류')
if (routeBMilestones.filter((item) => item.movement === '정박').length !== 3) throw new Error('항로B 정박 이벤트 수 오류')
if (routeAMilestones.at(-1).offset !== routeADuration || routeBMilestones.at(-1).offset !== routeBDuration) throw new Error('최종 도착 타임스탬프 경계값 오류')
const firstArrivalOffset = routeAMilestones[0].offset
const dockingFrame = vm.runInContext(`getJourneyFrame({ route: '항로A', location: 'Manus', journeyStartedAt: 1000 }, ${1000 + firstArrivalOffset + 5000})`, context)
if (dockingFrame.phase !== '정박' || dockingFrame.location !== 'Luf' || dockingFrame.x !== context.ISLAND_POINTS?.Luf?.x) {
  const lufPoint = vm.runInContext('ISLAND_POINTS.Luf', context)
  if (dockingFrame.phase !== '정박' || dockingFrame.location !== 'Luf' || dockingFrame.x !== lufPoint.x || dockingFrame.y !== lufPoint.y) throw new Error('섬 정박 프레임 오류')
}
const finishFrame = vm.runInContext("getJourneyFrame({ route: '항로B', location: 'Rambutyo', journeyStartedAt: 1000 }, 91000)", context)
if (finishFrame.location !== 'Manus' || !finishFrame.done || finishFrame.progress !== 1) throw new Error('항로B 90초 1회 운항 종료 오류')
const timelineKey = vm.runInContext("formatTimelineKey(new Date(2026, 10, 9, 19, 44), 'B_111')", context)
if (timelineKey !== '202611091944_B_111') throw new Error('항구 이벤트 키 형식 오류')
const eventTimestamp = vm.runInContext("formatEventTimestamp(new Date(2026, 10, 9, 19, 44, 37).toISOString())", context)
if (eventTimestamp !== '2026.11.09 19:44:37') throw new Error('초 단위 이벤트 타임스탬프 표시 오류')
context.timelineFixture = { id: 'arrival-1', key: '202611091944_B_111', S_L: 'B_111', movement: '도착', island: 'Manus', at: new Date(2026, 10, 9, 19, 44, 37).toISOString() }
const trackingTree = expand(vm.runInContext("Tracking({ vessels: [], portEvents: { Manus: [timelineFixture] } })", context))
const trackingText = text(trackingTree)
if (!trackingText.includes('2026.11.09 19:44:37') || !trackingText.includes('Manus 도착')) throw new Error('타임라인 화면의 타임스탬프 또는 섬별 동작 표시 오류')
const startedJourney = vm.runInContext("startJourneyState({ vessels: [{ id: 'v', number: '111', route: '항로B', location: '', status: '', journeyStartedAt: null, journeyEventCursor: 0 }], portEvents: {} }, 'v', 1000)", context)
if (startedJourney.vessels[0].status !== '운행중' || startedJourney.vessels[0].location !== 'Manus' || startedJourney.portEvents.Manus[0].movement !== '출발' || startedJourney.portEvents.Manus[0].S_L !== 'B_111') throw new Error('운행 시작 상태 또는 출발 이벤트 오류')
context.startedJourney = startedJourney
const finishedJourney = vm.runInContext('advanceJourneyState(startedJourney, 91000)', context)
if (finishedJourney.vessels[0].status !== '미운행' || finishedJourney.vessels[0].location !== 'Manus' || finishedJourney.vessels[0].journeyStartedAt !== null) throw new Error('운행 종료 상태 오류')
if (finishedJourney.portEvents.Manus.length !== 2 || finishedJourney.portEvents.Manus[1].movement !== '도착') throw new Error('Manus 복귀 이벤트 오류')
if (!finishedJourney.portEvents.Manus[1].at || finishedJourney.portEvents.Manus[1].island !== 'Manus') throw new Error('Manus 도착 타임스탬프 또는 섬 이름 누락')
if (!finishedJourney.portEvents['Los Negros'] || !finishedJourney.portEvents.Lou || !finishedJourney.portEvents.Rambutyo) throw new Error('항로B 섬 이벤트 누락')
for (const island of ['Los Negros', 'Lou', 'Rambutyo']) {
  const islandEvents = finishedJourney.portEvents[island]
  const movements = islandEvents.map((event) => event.movement).join(',')
  if (movements !== '도착,정박,출발') throw new Error(`${island} 도착·정박·출발 순서 오류: ${movements}`)
  if (new Date(islandEvents[2].at) - new Date(islandEvents[1].at) !== 10000) throw new Error(`${island} 10초 정박 타임스탬프 간격 오류`)
  if (islandEvents[0].at !== islandEvents[1].at) throw new Error(`${island} 도착·정박 시작 시각 불일치`)
}
context.fullPortEvents = finishedJourney.portEvents
const fullTimelineTree = expand(vm.runInContext('Tracking({ vessels: [], portEvents: fullPortEvents })', context))
const fullTimelineText = text(fullTimelineTree)
for (const island of ['Los Negros', 'Lou', 'Rambutyo']) {
  if (!fullTimelineText.includes(`${island} 도착`) || !fullTimelineText.includes(`${island} 정박 시작 · 10초`) || !fullTimelineText.includes(`${island} 출발`)) throw new Error(`${island} 전체 항구 타임라인 표시 누락`)
}
if (!fullTimelineText.includes('전체 항구 타임라인') || !fullTimelineText.includes('11건')) throw new Error('전체 항구 타임라인 범위 또는 건수 오류')
if (fullTimelineText.indexOf('Manus 도착') > fullTimelineText.indexOf('Rambutyo 출발') || fullTimelineText.indexOf('Rambutyo 출발') > fullTimelineText.indexOf('Los Negros 도착')) throw new Error('전체 항구 타임라인 최신순 정렬 오류')
const startedRouteA = vm.runInContext("startJourneyState({ vessels: [{ id: 'a', number: '112', route: '항로A', location: '', status: '', journeyStartedAt: null, journeyEventCursor: 0 }], portEvents: {} }, 'a', 2000)", context)
context.startedRouteA = startedRouteA
const finishedRouteA = vm.runInContext('advanceJourneyState(startedRouteA, 102000)', context)
for (const island of ['Luf', 'Mal', 'Aua', 'Wuvulu']) {
  const islandEvents = finishedRouteA.portEvents[island]
  const movements = islandEvents?.map((event) => event.movement).join(',')
  if (movements !== '도착,정박,출발') throw new Error(`항로A ${island} 정박 타임라인 누락`)
  if (new Date(islandEvents[2].at) - new Date(islandEvents[1].at) !== 10000) throw new Error(`항로A ${island} 10초 정박 타임스탬프 간격 오류`)
}

console.log('Verified: offline request form/history persistence, bottom action layout, existing inventory rules, newest-first all-port timeline, A 100s/B 90s one-trip frames, 10s docking timestamps, port-centered markers, status/location rules, responsive CSS')
