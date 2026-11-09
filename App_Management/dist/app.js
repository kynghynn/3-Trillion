/* global React, ReactDOM */

const h = React.createElement
const { useEffect, useMemo, useState } = React
const STORAGE_KEY = 'manus-medical-transport-v11'

const iconPaths = {
  Anchor: ['path|M12 22V8', 'path|M5 12H2a10 10 0 0 0 20 0h-3', 'circle|12|5|3'],
  ArrowLeft: ['path|m12 19-7-7 7-7', 'path|M19 12H5'],
  ArrowRight: ['path|M5 12h14', 'path|m12 5 7 7-7 7'],
  Boxes: ['path|M2.97 12.92 12 17.84l9.03-4.92', 'path|M12 17.84V22', 'path|M7 19.83V15.3', 'path|M17 19.83V15.3', 'path|M2.97 7.08 12 12l9.03-4.92', 'path|M12 12v5.84', 'path|M7 9.83 17 4.3', 'path|M17 9.83 7 4.3'],
  Check: ['path|m20 6-11 11-5-5'],
  ChevronRight: ['path|m9 18 6-6-6-6'],
  ClipboardPlus: ['rect|9|2|6|4|1', 'path|M9 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-3', 'path|M12 11v6', 'path|M9 14h6'],
  Clock: ['circle|12|12|10', 'polyline|12 6 12 12 16 14'],
  MapPinned: ['path|M18 8c0 4.5-6 9-6 9s-6-4.5-6-9a6 6 0 0 1 12 0Z', 'circle|12|8|2', 'path|m8.5 17-5.5 3', 'path|m15.5 17 5.5 3'],
  Menu: ['path|M4 6h16', 'path|M4 12h16', 'path|M4 18h16'],
  PackagePlus: ['path|m7.5 4.27 9 5.15', 'path|M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l3-1.72', 'path|M3.3 7 12 12l8.7-5', 'path|M12 22V12', 'path|M19 16v6', 'path|M16 19h6'],
  Plus: ['path|M5 12h14', 'path|M12 5v14'],
  Sailboat: ['path|M22 18H2a10 10 0 0 0 20 0Z', 'path|M12 2v16', 'path|m7 12 5-10 5 10Z'],
  Ship: ['path|M12 10.189V14', 'path|M12 2v3', 'path|M19.991 19.991A9.971 9.971 0 0 1 12 24a9.971 9.971 0 0 1-7.991-4.009', 'path|M4 12.5 12 8l8 4.5-2 7.5-6-3-6 3-2-7.5Z'],
  Trash: ['path|M3 6h18', 'path|M8 6V4h8v2', 'path|M19 6l-1 14H6L5 6', 'path|M10 11v5', 'path|M14 11v5'],
  Warehouse: ['path|M3 21V9l9-6 9 6v12', 'path|M3 13h18', 'path|M8 21v-4h8v4'],
  X: ['path|M18 6 6 18', 'path|m6 6 12 12'],
}

function Icon({ name, size = 24 }) {
  const nodes = (iconPaths[name] || iconPaths.Boxes).map((entry, index) => {
    const parts = entry.split('|')
    if (parts[0] === 'circle') return h('circle', { key: index, cx: parts[1], cy: parts[2], r: parts[3] })
    if (parts[0] === 'rect') return h('rect', { key: index, x: parts[1], y: parts[2], width: parts[3], height: parts[4], rx: parts[5] })
    if (parts[0] === 'polyline') return h('polyline', { key: index, points: parts[1] })
    return h('path', { key: index, d: parts[1] })
  })
  return h('svg', { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round', 'aria-hidden': true }, nodes)
}

const clone = (value) => JSON.parse(JSON.stringify(value))
const createId = () => globalThis.crypto?.randomUUID?.() || `item-${Date.now()}-${Math.random().toString(16).slice(2)}`
const containerKey = (kind, id) => `${kind}:${id}`
const medicineKey = (name, expiry) => `${name.trim().toLocaleLowerCase('ko-KR')}::${expiry}`
const formatExpiry = (value) => value.replaceAll('-', '.')
const SAILING_DURATION_MS = 60_000
const DOCK_DURATION_MS = 10_000
const ISLAND_POINTS = {
  Manus: { x: 78.188, y: 70.368, facilities: ['Manus Provincial Hospital', 'Lorengau East / West UC', 'Lessau HC', 'Bundralis HC', 'Tingou HC', 'Pelipowai HC', 'Patu HC'] },
  'Los Negros': { x: 86.942, y: 68.165, facilities: ['Lombrum HC'] },
  Lou: { x: 91.257, y: 69.965, facilities: ['Lako HC'] },
  Rambutyo: { x: 94.577, y: 81.537, facilities: ['Panuselu HC'] },
  Luf: { x: 44.273, y: 42.095, facilities: ['Luf AP'] },
  Mal: { x: 28.040, y: 35.612, facilities: ['Mal HC'] },
  Aua: { x: 7.464, y: 38.719, facilities: ['Aua Island AP'] },
  Wuvulu: { x: 3.638, y: 52.585, facilities: ['Wuvulu HC'] },
}
const ROUTES = {
  항로A: ['Manus', 'Luf', 'Mal', 'Aua', 'Wuvulu', 'Manus'],
  항로B: ['Manus', 'Los Negros', 'Lou', 'Rambutyo', 'Manus'],
}
const vesselLabel = (vessel) => `${vessel.route?.slice(-1) || ''}_${vessel.number}`
const formatTimelineKey = (date, S_L) => {
  const pad = (value) => String(value).padStart(2, '0')
  return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}${pad(date.getHours())}${pad(date.getMinutes())}_${S_L}`
}
const formatEventTimestamp = (value) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '시간 정보 없음'
  const pad = (part) => String(part).padStart(2, '0')
  return `${date.getFullYear()}.${pad(date.getMonth() + 1)}.${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}
const routeMetrics = (route) => {
  const stops = ROUTES[route] || []
  const lengths = stops.slice(0, -1).map((stop, index) => {
    const from = ISLAND_POINTS[stop]; const to = ISLAND_POINTS[stops[index + 1]]
    return Math.hypot(to.x - from.x, to.y - from.y)
  })
  const total = lengths.reduce((sum, value) => sum + value, 0)
  const travelDurations = lengths.map((length) => total ? SAILING_DURATION_MS * length / total : 0)
  const duration = SAILING_DURATION_MS + Math.max(0, stops.length - 2) * DOCK_DURATION_MS
  return { stops, lengths, total, travelDurations, duration }
}
const getJourneyDuration = (route) => routeMetrics(route).duration
const getJourneyMilestones = (route) => {
  const metrics = routeMetrics(route); const milestones = []; let sailingOffset = 0; let dockOffset = 0
  metrics.travelDurations.forEach((travelDuration, index) => {
    sailingOffset += travelDuration
    let offset = Math.round(sailingOffset) + dockOffset
    const island = metrics.stops[index + 1]
    milestones.push({ offset, island, movement: '도착' })
    if (index < metrics.travelDurations.length - 1) {
      milestones.push({ offset, island, movement: '정박' })
      dockOffset += DOCK_DURATION_MS
      offset = Math.round(sailingOffset) + dockOffset
      milestones.push({ offset, island, movement: '출발' })
    }
  })
  return milestones
}
const getJourneyFrame = (vessel, now = Date.now()) => {
  const metrics = routeMetrics(vessel.route)
  if (!metrics.stops.length || !vessel.journeyStartedAt) return { done: false, stopIndex: 0, location: vessel.location || '', x: ISLAND_POINTS.Manus.x, y: ISLAND_POINTS.Manus.y, progress: 0, phase: '대기' }
  const elapsed = Math.max(0, now - vessel.journeyStartedAt)
  if (elapsed >= metrics.duration) return { done: true, stopIndex: metrics.stops.length - 1, location: 'Manus', ...ISLAND_POINTS.Manus, progress: 1, phase: '완료' }
  let remaining = elapsed
  for (let segment = 0; segment < metrics.travelDurations.length; segment += 1) {
    const travelDuration = metrics.travelDurations[segment]
    const from = ISLAND_POINTS[metrics.stops[segment]]; const to = ISLAND_POINTS[metrics.stops[segment + 1]]
    if (remaining < travelDuration) {
      const segmentProgress = travelDuration ? remaining / travelDuration : 0
      return { done: false, stopIndex: segment, location: metrics.stops[segment], x: from.x + (to.x - from.x) * segmentProgress, y: from.y + (to.y - from.y) * segmentProgress, progress: elapsed / metrics.duration, phase: '운항' }
    }
    remaining -= travelDuration
    if (segment < metrics.travelDurations.length - 1) {
      if (remaining < DOCK_DURATION_MS) return { done: false, stopIndex: segment + 1, location: metrics.stops[segment + 1], x: to.x, y: to.y, progress: elapsed / metrics.duration, phase: '정박', dockRemaining: DOCK_DURATION_MS - remaining }
      remaining -= DOCK_DURATION_MS
    }
  }
  return { done: true, stopIndex: metrics.stops.length - 1, location: 'Manus', ...ISLAND_POINTS.Manus, progress: 1, phase: '완료' }
}
const initialState = {
  vessels: [{ id: 'vessel-111', number: '111', type: '중형', route: '', location: '', status: '', journeyStartedAt: null, journeyEventCursor: 0 }],
  islands: ['Manus', 'Los Negros', 'Lou', 'Rambutyo', 'Luf', 'Mal', 'Aua', 'Wuvulu'],
  inventories: {
    'vessel:vessel-111': [], 'island:Manus': [], 'island:Los Negros': [], 'island:Lou': [],
    'island:Rambutyo': [], 'island:Luf': [], 'island:Mal': [], 'island:Aua': [], 'island:Wuvulu': [],
  },
  portEvents: {},
  requests: [],
}

const hydrateState = (saved) => {
  if (!saved) return clone(initialState)
  return {
    ...clone(initialState),
    ...saved,
    vessels: (saved.vessels || initialState.vessels).map((vessel) => ({
      ...vessel,
      status: vessel.status === '운행중' && !vessel.journeyStartedAt ? '미운행' : vessel.status,
      journeyStartedAt: vessel.journeyStartedAt || null,
      journeyEventCursor: Number.isInteger(vessel.journeyEventCursor) ? vessel.journeyEventCursor : 0,
    })),
    inventories: { ...clone(initialState.inventories), ...(saved.inventories || {}) },
    portEvents: saved.portEvents || {},
    requests: Array.isArray(saved.requests) ? saved.requests : [],
  }
}

const addPortEvent = (portEvents, island, vessel, movement, at = new Date()) => {
  const S_L = vesselLabel(vessel)
  const event = { id: createId(), key: formatTimelineKey(at, S_L), S_L, movement, island, at: at.toISOString() }
  return { ...portEvents, [island]: [...(portEvents[island] || []), event] }
}

const reduceInventory = (list, quantities) => list
  .map((item) => {
    const quantity = Math.min(item.quantity, Math.max(0, quantities[item.id] || 0))
    return { ...item, quantity: item.quantity - quantity }
  })
  .filter((item) => item.quantity > 0)

const addRequestState = (current, request, now = Date.now()) => {
  const medicineName = request.medicineName.trim()
  const quantity = Number(request.quantity)
  if (!medicineName || !Number.isInteger(quantity) || quantity < 1) return current
  const entry = { id: createId(), medicineName, quantity, requestedAt: new Date(now).toISOString() }
  return { ...current, requests: [entry, ...(current.requests || [])] }
}

const startJourneyState = (current, id, now = Date.now()) => {
  const vessel = current.vessels.find((item) => item.id === id)
  if (!vessel || vessel.status === '운행중' || !ROUTES[vessel.route]) return current
  const started = { ...vessel, status: '운행중', location: 'Manus', journeyStartedAt: now, journeyEventCursor: 0 }
  return {
    ...current,
    vessels: current.vessels.map((item) => item.id === id ? started : item),
    portEvents: addPortEvent(current.portEvents || {}, 'Manus', started, '출발', new Date(now)),
  }
}

const advanceJourneyState = (current, now = Date.now()) => {
  let changed = false; let portEvents = current.portEvents || {}
  const vessels = current.vessels.map((vessel) => {
    if (vessel.status !== '운행중' || !vessel.journeyStartedAt || !ROUTES[vessel.route]) return vessel
    const frame = getJourneyFrame(vessel, now); const milestones = getJourneyMilestones(vessel.route)
    let cursor = vessel.journeyEventCursor || 0
    while (cursor < milestones.length && vessel.journeyStartedAt + milestones[cursor].offset <= now) {
      const milestone = milestones[cursor]
      portEvents = addPortEvent(portEvents, milestone.island, vessel, milestone.movement, new Date(vessel.journeyStartedAt + milestone.offset))
      cursor += 1; changed = true
    }
    const next = frame.done
      ? { ...vessel, status: '미운행', location: 'Manus', journeyStartedAt: null, journeyEventCursor: 0 }
      : { ...vessel, location: frame.location, journeyEventCursor: cursor }
    if (next.status !== vessel.status || next.location !== vessel.location || next.journeyEventCursor !== vessel.journeyEventCursor) changed = true
    return next
  })
  return changed ? { ...current, vessels, portEvents } : current
}

function useStore() {
  const [state, setState] = useState(() => {
    try { return hydrateState(JSON.parse(localStorage.getItem(STORAGE_KEY))) } catch { return clone(initialState) }
  })
  useEffect(() => localStorage.setItem(STORAGE_KEY, JSON.stringify(state)), [state])
  useEffect(() => {
    const timer = setInterval(() => setState((current) => advanceJourneyState(current)), 200)
    return () => clearInterval(timer)
  }, [])
  const addVessel = ({ number, type }) => setState((current) => {
    if (current.vessels.some((item) => item.number === number)) return current
    const id = `vessel-${number}`
    return { ...current, vessels: [...current.vessels, { id, number, type, route: '', location: '', status: '', journeyStartedAt: null, journeyEventCursor: 0 }], inventories: { ...current.inventories, [containerKey('vessel', id)]: [] } }
  })
  const updateVessel = (id, changes) => setState((current) => ({ ...current, vessels: current.vessels.map((item) => item.id === id ? { ...item, ...changes } : item) }))
  const deleteVessel = (id) => setState((current) => {
    const inventories = { ...current.inventories }; delete inventories[containerKey('vessel', id)]
    return { ...current, vessels: current.vessels.filter((item) => item.id !== id), inventories }
  })
  const startJourney = (id) => setState((current) => startJourneyState(current, id))
  const addMedicine = (key, item) => setState((current) => {
    const list = current.inventories[key] || []
    const match = list.find((candidate) => medicineKey(candidate.name, candidate.expiry) === medicineKey(item.name, item.expiry))
    const next = match ? list.map((candidate) => candidate.id === match.id ? { ...candidate, quantity: candidate.quantity + item.quantity } : candidate) : [...list, { ...item, id: createId() }]
    return { ...current, inventories: { ...current.inventories, [key]: next } }
  })
  const reduceMedicines = (key, quantities) => setState((current) => ({
    ...current,
    inventories: {
      ...current.inventories,
      [key]: reduceInventory(current.inventories[key] || [], quantities),
    },
  }))
  const transfer = (sourceKey, destinationKey, quantities) => setState((current) => {
    const source = current.inventories[sourceKey] || []
    let destination = [...(current.inventories[destinationKey] || [])]
    const moved = {}
    source.forEach((item) => {
      const quantity = Math.min(item.quantity, Math.max(0, quantities[item.id] || 0)); moved[item.id] = quantity
      if (!quantity) return
      const match = destination.find((candidate) => medicineKey(candidate.name, candidate.expiry) === medicineKey(item.name, item.expiry))
      destination = match ? destination.map((candidate) => candidate.id === match.id ? { ...candidate, quantity: candidate.quantity + quantity } : candidate) : [...destination, { ...item, id: createId(), quantity }]
    })
    const remaining = source.map((item) => ({ ...item, quantity: item.quantity - moved[item.id] })).filter((item) => item.quantity > 0)
    return { ...current, inventories: { ...current.inventories, [sourceKey]: remaining, [destinationKey]: destination } }
  })
  const addRequest = (request) => setState((current) => addRequestState(current, request))
  return { state, addVessel, updateVessel, deleteVessel, startJourney, addMedicine, reduceMedicines, transfer, addRequest }
}

function Header({ goHome, isHome }) {
  return h('header', { className: 'topbar' },
    h('button', { className: 'brand', type: 'button', onClick: goHome, 'aria-label': '홈으로 이동' },
      h('span', { className: 'brand-mark' }, h(Icon, { name: 'Anchor', size: 34 })),
      h('span', null, h('strong', null, 'MANUS'), h('small', null, 'Medical Transportation Management'))),
    !isHome && h('button', { className: 'icon-button', type: 'button', onClick: goHome, 'aria-label': '메뉴' }, h(Icon, { name: 'Menu' })))
}

function Home({ navigate }) {
  const items = [
    ['선박 관리', '참여 선박과 적재 재고', 'Ship', { name: 'vessels' }],
    ['운행 위치', 'A·B 항로 시뮬레이션', 'MapPinned', { name: 'tracking' }],
    ['재고 관리', '선박·섬 재고 통합 조회', 'Boxes', { name: 'inventory' }],
    ['재고 요청', '필요 의약품 요청 및 내역', 'ClipboardPlus', { name: 'requests' }],
  ]
  return h('section', { className: 'home-screen page-enter' },
    h('div', { className: 'status-banner' }, h(Icon, { name: 'Clock' }), h('p', null, h('strong', null, '운행 알림'), h('span', null, '시뮬레이션 선박의 입·출항 알림이 이곳에 표시됩니다.'))),
    h('div', { className: 'home-grid' }, items.map(([label, description, icon, screen], index) => h('button', { className: 'home-action', style: { '--delay': `${index * 70}ms` }, type: 'button', onClick: () => navigate(screen), key: label }, h('span', { className: 'home-icon' }, h(Icon, { name: icon, size: 56 })), h('span', null, h('strong', null, label), h('small', null, description)), h('span', { className: 'action-arrow' }, h(Icon, { name: 'ChevronRight' })))))
  )
}

function PageHeading({ icon, title, eyebrow, actions }) {
  return h('div', { className: 'page-heading' }, h('div', { className: 'heading-title' }, h('span', { className: 'heading-icon' }, h(Icon, { name: icon })), h('div', null, eyebrow && h('small', null, eyebrow), h('h1', null, title))), actions && h('div', { className: 'heading-actions' }, actions))
}

function BackButton({ onClick, label = '목록' }) { return h('button', { className: 'text-button', type: 'button', onClick }, h(Icon, { name: 'ArrowLeft', size: 18 }), label) }
function EmptyState({ title, copy }) { return h('div', { className: 'empty-state' }, h(Icon, { name: 'Boxes', size: 48 }), h('strong', null, title), h('p', null, copy)) }

function Modal({ title, onClose, children, wide }) {
  return h('div', { className: 'modal-backdrop', onMouseDown: (event) => event.target === event.currentTarget && onClose() }, h('section', { className: `modal${wide ? ' wide' : ''}`, role: 'dialog', 'aria-modal': true }, h('div', { className: 'modal-title' }, h('h2', null, title), h('button', { className: 'icon-button', type: 'button', onClick: onClose, 'aria-label': '닫기' }, h(Icon, { name: 'X' }))), children))
}

function AddVesselModal({ vessels, onClose, onAdd }) {
  const [number, setNumber] = useState(''); const [type, setType] = useState('중형')
  const duplicate = vessels.some((item) => item.number === number)
  return h(Modal, { title: '선박 추가', onClose }, h('form', { className: 'modal-form', onSubmit: (event) => { event.preventDefault(); if (number && !duplicate) onAdd({ number, type }) } },
    h('label', null, '배번호', h('input', { inputMode: 'numeric', value: number, onChange: (event) => setNumber(event.target.value.replace(/\D/g, '')), placeholder: '예: 112', autoFocus: true, required: true })),
    duplicate && h('p', { className: 'field-error' }, '이미 등록된 배번호입니다.'),
    h('label', null, '선박 종류', h('select', { value: type, onChange: (event) => setType(event.target.value) }, ['소형', '중형', '대형'].map((value) => h('option', { key: value }, value)))),
    h('p', { className: 'form-note' }, '위치와 선박 상태는 등록 후 상세 화면에서 입력합니다.'),
    h('button', { className: 'primary-button full', type: 'submit', disabled: !number || duplicate }, h(Icon, { name: 'Plus', size: 18 }), '추가')))
}

function VesselList({ vessels, addVessel, navigate }) {
  const [open, setOpen] = useState(false)
  return h('section', { className: 'workspace page-enter' },
    h(PageHeading, { icon: 'Ship', title: '선박 관리', eyebrow: `${vessels.length}척 등록`, actions: h('button', { className: 'primary-button', type: 'button', onClick: () => setOpen(true) }, h(Icon, { name: 'Plus', size: 18 }), '선박 추가') }),
    h('div', { className: 'data-list' }, vessels.length === 0 && h(EmptyState, { title: '등록된 선박이 없습니다', copy: '선박 추가 버튼으로 첫 선박을 등록하세요.' }), vessels.map((vessel) => h('button', { className: 'data-row', type: 'button', key: vessel.id, onClick: () => navigate({ name: 'vessel', id: vessel.id }) }, h('span', { className: 'row-icon' }, h(Icon, { name: 'Sailboat' })), h('span', { className: 'row-main' }, h('strong', null, `No. ${vessel.number}`), h('small', null, `${vessel.type} · ${vessel.route || '항로 미지정'}`)), h('span', { className: `status-chip${vessel.status === '운행중' ? ' active' : ''}` }, vessel.status || '미운행'), h(Icon, { name: 'ChevronRight' })))),
    open && h(AddVesselModal, { vessels, onClose: () => setOpen(false), onAdd: (vessel) => { addVessel(vessel); setOpen(false) } }))
}

function InventoryTable({ medicines, selected, setSelected }) {
  const allSelected = medicines.length > 0 && selected.length === medicines.length
  return h('div', { className: 'inventory-panel' }, h('div', { className: 'inventory-title' }, h('div', null, h('h2', null, '보관 재고'), h('span', null, `${medicines.reduce((sum, item) => sum + item.quantity, 0)}개 · ${medicines.length}품목`))),
    h('div', { className: 'table-wrap' }, h('table', null,
      h('thead', null, h('tr', null, h('th', null, h('button', { className: `check-button${allSelected ? ' checked' : ''}`, type: 'button', onClick: () => setSelected(allSelected ? [] : medicines.map((item) => item.id)) }, allSelected && h(Icon, { name: 'Check', size: 15 }))), h('th', null, '약품명'), h('th', null, '유통기한'), h('th', { className: 'numeric' }, '수량'))),
      h('tbody', null, medicines.length === 0 ? h('tr', null, h('td', { className: 'empty-cell', colSpan: 4 }, '등록된 의약품이 없습니다.')) : medicines.map((medicine) => {
        const checked = selected.includes(medicine.id)
        return h('tr', { key: medicine.id, className: checked ? 'selected' : '' }, h('td', null, h('button', { className: `check-button${checked ? ' checked' : ''}`, type: 'button', onClick: () => setSelected(checked ? selected.filter((id) => id !== medicine.id) : [...selected, medicine.id]) }, checked && h(Icon, { name: 'Check', size: 15 }))), h('td', null, h('strong', null, medicine.name)), h('td', { className: new Date(`${medicine.expiry}T00:00:00`) < new Date() ? 'expired' : '' }, formatExpiry(medicine.expiry)), h('td', { className: 'numeric' }, medicine.quantity))
      })))))
}

function AddMedicineModal({ onClose, onAdd }) {
  const [name, setName] = useState(''); const [quantity, setQuantity] = useState(1); const [expiry, setExpiry] = useState('')
  return h(Modal, { title: '재고 추가', onClose }, h('form', { className: 'modal-form', onSubmit: (event) => { event.preventDefault(); if (name.trim() && expiry && quantity > 0) onAdd({ name: name.trim(), quantity, expiry }) } },
    h('label', null, '약품명', h('input', { value: name, onChange: (event) => setName(event.target.value), placeholder: '약품명 입력', autoFocus: true, required: true })),
    h('label', null, '수량', h('input', { type: 'number', min: 1, value: quantity, onChange: (event) => setQuantity(Math.max(1, Number(event.target.value))), required: true })),
    h('label', null, '유통기한', h('input', { type: 'date', value: expiry, onChange: (event) => setExpiry(event.target.value), required: true })),
    h('p', { className: 'form-note' }, '약품명과 유통기한이 모두 같으면 기존 항목의 수량에 합산됩니다.'),
    h('button', { className: 'primary-button full', type: 'submit' }, h(Icon, { name: 'Plus', size: 18 }), '추가')))
}

function DeleteQuantityModal({ medicines, onClose, onDelete }) {
  const [quantities, setQuantities] = useState(() => Object.fromEntries(medicines.map((item) => [item.id, 1])))
  const total = Object.values(quantities).reduce((sum, value) => sum + value, 0)
  return h(Modal, { title: '재고 수량 삭제', onClose, wide: true }, h('form', { className: 'modal-form', onSubmit: (event) => { event.preventDefault(); if (total > 0) onDelete(quantities) } },
    h('div', { className: 'transfer-list' },
      h('div', { className: 'transfer-head' }, h('span', null, '선택 품목'), h('span', null, '현재 / 삭제 수량')),
      medicines.map((medicine) => h('label', { className: 'transfer-row', key: medicine.id },
        h('span', null, h('span', null, h('strong', null, medicine.name), h('small', null, formatExpiry(medicine.expiry)))),
        h('span', null, h('b', null, medicine.quantity), h('input', {
          type: 'number', min: 1, max: medicine.quantity, value: quantities[medicine.id] || 1,
          onChange: (event) => setQuantities({ ...quantities, [medicine.id]: Math.min(medicine.quantity, Math.max(1, Number(event.target.value))) }),
          'aria-label': `${medicine.name} 삭제 수량`,
        }))))),
    h('p', { className: 'form-note' }, '입력한 수량만큼만 차감합니다. 현재 수량 전부를 입력한 품목만 목록에서 삭제됩니다.'),
    h('button', { className: 'danger-button full', type: 'submit', disabled: total < 1 }, h(Icon, { name: 'Trash', size: 18 }), '수량 삭제')))
}

function TransferModal({ medicines, islands, onClose, onTransfer }) {
  const [island, setIsland] = useState(''); const [quantities, setQuantities] = useState({})
  const selectedCount = Object.values(quantities).filter((value) => value > 0).length
  return h(Modal, { title: '재고 이전', onClose, wide: true }, h('form', { className: 'modal-form', onSubmit: (event) => { event.preventDefault(); if (island && selectedCount) onTransfer(island, quantities) } },
    h('label', null, '이전 대상', h('select', { value: island, onChange: (event) => setIsland(event.target.value), required: true }, h('option', { value: '' }, '섬을 선택하세요'), islands.map((value) => h('option', { key: value }, value)))),
    h('div', { className: 'transfer-list' }, h('div', { className: 'transfer-head' }, h('span', null, '이전 품목'), h('span', null, '현재 / 이전 수량')), medicines.map((medicine) => h('label', { className: 'transfer-row', key: medicine.id }, h('span', null, h('input', { type: 'checkbox', checked: (quantities[medicine.id] || 0) > 0, onChange: (event) => setQuantities({ ...quantities, [medicine.id]: event.target.checked ? 1 : 0 }) }), h('span', null, h('strong', null, medicine.name), h('small', null, formatExpiry(medicine.expiry)))), h('span', null, h('b', null, medicine.quantity), h('input', { type: 'number', min: 0, max: medicine.quantity, value: quantities[medicine.id] || 0, onChange: (event) => setQuantities({ ...quantities, [medicine.id]: Math.min(medicine.quantity, Math.max(0, Number(event.target.value))) }) }))))),
    h('p', { className: 'form-note' }, '이전한 수량은 선박 재고에서 차감되고 선택한 섬 재고에 합산됩니다.'),
    h('button', { className: 'primary-button full', type: 'submit', disabled: !island || !selectedCount }, h(Icon, { name: 'ArrowRight', size: 18 }), '이전')))
}

function VesselDetail({ vessel, medicines, islands, store, navigate }) {
  const [selected, setSelected] = useState([]); const [modal, setModal] = useState('')
  if (!vessel) return h('section', { className: 'workspace' }, h(EmptyState, { title: '선박을 찾을 수 없습니다', copy: '선박 목록으로 돌아가 다시 선택하세요.' }), h(BackButton, { onClick: () => navigate({ name: 'vessels' }) }))
  const key = containerKey('vessel', vessel.id)
  const running = vessel.status === '운행중'
  const canStart = Boolean(ROUTES[vessel.route]) && !running
  return h('section', { className: 'workspace page-enter' }, h(BackButton, { onClick: () => navigate({ name: 'vessels' }), label: '선박 목록' }),
    h(PageHeading, { icon: 'Sailboat', title: `No. ${vessel.number}`, eyebrow: '선박 상세', actions: h('button', { className: 'danger-button', type: 'button', onClick: () => { if (confirm(`No. ${vessel.number} 선박과 선박 재고를 모두 삭제할까요?`)) { store.deleteVessel(vessel.id); navigate({ name: 'vessels' }) } } }, h(Icon, { name: 'Trash', size: 18 }), '선박 정보 삭제') }),
    h('div', { className: 'detail-grid' },
      h('label', null, '선박 종류', h('select', { value: vessel.type, disabled: running, onChange: (event) => store.updateVessel(vessel.id, { type: event.target.value }) }, ['소형','중형','대형'].map((value) => h('option', { key: value }, value)))),
      h('label', null, '항로', h('select', { value: vessel.route, disabled: running, onChange: (event) => { const route = event.target.value; store.updateVessel(vessel.id, { route, status: route ? '미운행' : '', location: route === '미운행' || !route ? '' : vessel.location }) } }, h('option', { value: '' }, '선택'), ['미운행','항로A','항로B'].map((value) => h('option', { key: value }, value)))),
      h('label', null, '위치', h('input', { value: vessel.location || '', readOnly: true, placeholder: '운행 시작 전' })),
      h('div', { className: 'control-field' }, h('span', null, '선박 상태'), h('div', { className: 'status-control' }, h('strong', { className: running ? 'running' : '' }, vessel.status || '미운행'), h('button', { className: 'primary-button', type: 'button', disabled: !canStart, onClick: () => store.startJourney(vessel.id) }, h(Icon, { name: 'Sailboat', size: 18 }), running ? '운행 중' : ROUTES[vessel.route] ? '운행 시작' : '항로 선택 필요')))),
    h(InventoryTable, { medicines, selected, setSelected }),
    h('div', { className: 'inventory-actions' }, h('button', { className: 'secondary-button', type: 'button', disabled: !selected.length, onClick: () => setModal('reduce') }, h(Icon, { name: 'Trash', size: 18 }), '선택 수량 삭제'), h('div', null, h('button', { className: 'secondary-button', type: 'button', disabled: !medicines.length, onClick: () => setModal('transfer') }, h(Icon, { name: 'ArrowRight', size: 18 }), '재고 이전'), h('button', { className: 'primary-button', type: 'button', onClick: () => setModal('add') }, h(Icon, { name: 'PackagePlus', size: 18 }), '재고 추가'))),
    modal === 'add' && h(AddMedicineModal, { onClose: () => setModal(''), onAdd: (item) => { store.addMedicine(key, item); setModal('') } }),
    modal === 'transfer' && h(TransferModal, { medicines, islands, onClose: () => setModal(''), onTransfer: (island, quantities) => { store.transfer(key, containerKey('island', island), quantities); setModal('') } }),
    modal === 'reduce' && h(DeleteQuantityModal, { medicines: medicines.filter((item) => selected.includes(item.id)), onClose: () => setModal(''), onDelete: (quantities) => { store.reduceMedicines(key, quantities); setSelected([]); setModal('') } })
  )
}

function InventoryList({ vessels, islands, navigate }) {
  const containers = useMemo(() => [...vessels.map((vessel) => ({ kind: 'vessel', id: vessel.id, label: `No. ${vessel.number}`, meta: `선박 · ${vessel.type}` })), ...islands.map((island) => ({ kind: 'island', id: island, label: island, meta: '섬 보관소' }))], [vessels, islands])
  return h('section', { className: 'workspace page-enter' }, h(PageHeading, { icon: 'Boxes', title: '재고 관리', eyebrow: `${containers.length}개 보관처` }), h('p', { className: 'section-copy' }, '선박과 섬을 선택해 보관 중인 의약품을 확인합니다.'), h('div', { className: 'data-list' }, containers.map((item) => h('button', { className: 'data-row', type: 'button', key: `${item.kind}-${item.id}`, onClick: () => navigate(item.kind === 'vessel' ? { name: 'vessel', id: item.id } : { name: 'storage', kind: item.kind, id: item.id }) }, h('span', { className: 'row-icon' }, h(Icon, { name: item.kind === 'vessel' ? 'Sailboat' : 'Warehouse' })), h('span', { className: 'row-main' }, h('strong', null, item.label), h('small', null, item.meta)), h(Icon, { name: 'ChevronRight' })))))
}

function StorageDetail({ kind, id, medicines, store, navigate }) {
  const [selected, setSelected] = useState([]); const [modal, setModal] = useState(''); const key = containerKey(kind, id)
  return h('section', { className: 'workspace page-enter' }, h(BackButton, { onClick: () => navigate({ name: 'inventory' }), label: '재고 목록' }), h(PageHeading, { icon: kind === 'vessel' ? 'Sailboat' : 'Warehouse', title: `${id} 재고`, eyebrow: kind === 'vessel' ? '선박 보관처' : '섬 보관처' }), h(InventoryTable, { medicines, selected, setSelected }), h('div', { className: 'inventory-actions' }, h('button', { className: 'secondary-button', type: 'button', disabled: !selected.length, onClick: () => setModal('reduce') }, h(Icon, { name: 'Trash', size: 18 }), '선택 수량 삭제'), h('button', { className: 'primary-button', type: 'button', onClick: () => setModal('add') }, h(Icon, { name: 'PackagePlus', size: 18 }), '재고 추가')), modal === 'add' && h(AddMedicineModal, { onClose: () => setModal(''), onAdd: (item) => { store.addMedicine(key, item); setModal('') } }), modal === 'reduce' && h(DeleteQuantityModal, { medicines: medicines.filter((item) => selected.includes(item.id)), onClose: () => setModal(''), onDelete: (quantities) => { store.reduceMedicines(key, quantities); setSelected([]); setModal('') } }))
}

function RequestPage({ store, navigate }) {
  const [medicineName, setMedicineName] = useState(''); const [quantity, setQuantity] = useState(''); const [message, setMessage] = useState('')
  const submit = (event) => {
    event.preventDefault()
    const normalizedName = medicineName.trim(); const normalizedQuantity = Number(quantity)
    if (!normalizedName || !Number.isInteger(normalizedQuantity) || normalizedQuantity < 1) { setMessage('약품 이름과 1개 이상의 수량을 입력하세요.'); return }
    store.addRequest({ medicineName: normalizedName, quantity: normalizedQuantity })
    setMedicineName(''); setQuantity(''); setMessage('요청 내역에 저장되었습니다.')
  }
  return h('section', { className: 'workspace request-workspace page-enter' },
    h(PageHeading, { icon: 'ClipboardPlus', title: '재고 요청', eyebrow: '필요 의약품 등록' }),
    h('form', { className: 'request-form', onSubmit: submit },
      h('p', { className: 'section-copy' }, '필요한 약품 이름과 수량을 입력하세요. 요청은 요청 내역에 저장됩니다.'),
      h('div', { className: 'request-fields' },
        h('label', null, '약품 이름', h('input', { value: medicineName, onChange: (event) => { setMedicineName(event.target.value); setMessage('') }, placeholder: '예: 타이레놀', required: true })),
        h('label', null, '수량', h('input', { type: 'number', min: 1, step: 1, value: quantity, onChange: (event) => { setQuantity(event.target.value); setMessage('') }, placeholder: '필요 수량', required: true }))),
      message && h('p', { className: message.includes('저장') ? 'request-message success' : 'request-message error', role: 'status' }, message),
      h('div', { className: 'request-actions' },
        h('button', { className: 'primary-button', type: 'submit' }, h(Icon, { name: 'ClipboardPlus', size: 18 }), '요청하기'),
        h('button', { className: 'secondary-button', type: 'button', onClick: () => navigate({ name: 'request-history' }) }, h(Icon, { name: 'Clock', size: 18 }), '요청 내역'))))
}

function RequestHistory({ requests, navigate }) {
  const ordered = [...requests].sort((a, b) => b.requestedAt.localeCompare(a.requestedAt))
  return h('section', { className: 'workspace page-enter' },
    h(BackButton, { onClick: () => navigate({ name: 'requests' }), label: '재고 요청' }),
    h(PageHeading, { icon: 'Clock', title: '요청 내역', eyebrow: `${ordered.length}건` }),
    ordered.length
      ? h('div', { className: 'request-history' }, ordered.map((request) => h('div', { className: 'request-row', key: request.id },
          h('span', { className: 'row-icon' }, h(Icon, { name: 'ClipboardPlus' })),
          h('span', { className: 'request-main' }, h('strong', null, request.medicineName), h('time', { dateTime: request.requestedAt }, formatEventTimestamp(request.requestedAt))),
          h('strong', { className: 'request-quantity' }, `${request.quantity}개`))))
      : h(EmptyState, { title: '저장된 요청이 없습니다', copy: '재고 요청에서 필요한 약품과 수량을 등록하세요.' }))
}

function Tracking({ vessels, portEvents }) {
  const [now, setNow] = useState(Date.now()); const [selectedIsland, setSelectedIsland] = useState('')
  useEffect(() => { const timer = setInterval(() => setNow(Date.now()), 100); return () => clearInterval(timer) }, [])
  const active = vessels.filter((vessel) => vessel.status === '운행중' && vessel.journeyStartedAt && ROUTES[vessel.route])
  const allEvents = Object.values(portEvents).flat()
  const events = [...(selectedIsland ? portEvents[selectedIsland] || [] : allEvents)].sort((a, b) => b.at.localeCompare(a.at))
  const point = selectedIsland ? ISLAND_POINTS[selectedIsland] : null
  const summary = active.length
    ? active.map((vessel) => {
        const frame = getJourneyFrame(vessel, now)
        const remaining = Math.max(0, Math.ceil((getJourneyDuration(vessel.route) - (now - vessel.journeyStartedAt)) / 1000))
        return h('div', { className: `active-vessel${frame.phase === '정박' ? ' docking' : ''}`, key: vessel.id },
          h('span', null, h(Icon, { name: 'Sailboat', size: 18 }), vesselLabel(vessel)),
          h('strong', null, frame.phase === '정박' ? `${frame.location} 정박 중` : `${frame.location || 'Manus'} 출발 구간`),
          h('small', null, `${remaining}초 남음`))
      })
    : h('p', null, '현재 운행 중인 선박이 없습니다. 선박 상세에서 항로를 선택하고 운행을 시작하세요.')
  const routeLines = Object.entries(ROUTES).map(([route, stops]) => h('polyline', {
    key: route,
    className: route === '항로A' ? 'route-a' : 'route-b',
    points: stops.map((stop) => `${ISLAND_POINTS[stop].x},${ISLAND_POINTS[stop].y}`).join(' '),
    vectorEffect: 'non-scaling-stroke',
  }))
  const portButtons = Object.entries(ISLAND_POINTS).map(([island, islandPoint]) => h('button', {
    className: `port-hit${selectedIsland === island ? ' selected' : ''}`,
    style: { left: `${islandPoint.x}%`, top: `${islandPoint.y}%` },
    type: 'button', key: island,
    onClick: () => setSelectedIsland(island),
    'aria-label': `${island} 항구 타임라인`,
  }, h('span', null, island)))
  const markers = active.map((vessel, index) => {
    const frame = getJourneyFrame(vessel, now)
    return h('div', { className: `vessel-marker${frame.phase === '정박' ? ' docking' : ''}`, style: { left: `${frame.x}%`, top: `${frame.y}%`, '--marker-index': index }, key: vessel.id },
      h('span', { className: 'vessel-dot' }, h(Icon, { name: 'Sailboat', size: 17 })),
      h('strong', null, vesselLabel(vessel)))
  })
  const timeline = events.length
    ? h('div', { className: 'event-list' }, events.map((event) => h('div', { className: 'event-row', key: event.id },
        h('div', { className: 'event-stamp' },
          h('time', { dateTime: event.at }, formatEventTimestamp(event.at)),
          h('code', null, event.key)),
        h('strong', { className: event.movement === '도착' ? 'arrival' : event.movement === '정박' ? 'docking' : 'departure' }, event.movement === '정박' ? `${event.island} 정박 시작 · 10초` : `${event.island} ${event.movement}`))))
    : h('p', { className: 'empty-timeline' }, '기록된 운항 이벤트가 없습니다.')
  return h('section', { className: 'workspace page-enter' },
    h(PageHeading, { icon: 'MapPinned', title: '운행 위치', eyebrow: '항로별 1회 운항 시뮬레이션' }),
    h('div', { className: 'tracking-summary' }, summary),
    h('div', { className: 'route-duration-legend' },
      h('span', null, h('strong', null, '항로 A'), ' 100초'),
      h('span', null, h('strong', null, '항로 B'), ' 90초'),
      h('span', null, '중간 섬마다 10초 정박')),
    h('div', { className: 'map-scroll' },
      h('div', { className: 'map-frame' },
        h('img', { src: './assets/manus-health-facility-islands-map.png', alt: '마누스주 사업 대상 섬 지도' }),
        h('svg', { className: 'route-overlay', viewBox: '0 0 100 100', preserveAspectRatio: 'none', 'aria-hidden': true }, routeLines),
        portButtons,
        markers
      )
    ),
    h('div', { className: 'tracking-detail' },
      h('section', null,
        h('small', null, selectedIsland ? '선택 항구' : '타임라인 범위'),
        h('h2', null, selectedIsland || '전체 항구'),
        h('p', null, point ? `보건시설: ${point.facilities.join(', ')}` : '모든 항구의 출발·도착·정박 기록을 최신 기록부터 표시합니다. 지도에서 섬을 선택하면 해당 항구 기록만 확인할 수 있습니다.')),
      h('section', { className: 'timeline-panel' },
        h('div', { className: 'timeline-heading' },
          h('h2', null, selectedIsland ? `${selectedIsland} 타임라인` : '전체 항구 타임라인'),
          h('div', { className: 'timeline-actions' },
            selectedIsland && h('button', { className: 'timeline-filter', type: 'button', onClick: () => setSelectedIsland('') }, '전체 항구'),
            h('span', null, `${events.length}건`))),
        timeline)
    )
  )
}

function App() {
  const store = useStore(); const [screen, setScreen] = useState({ name: 'home' }); const goHome = () => setScreen({ name: 'home' })
  let page = h(Home, { navigate: setScreen })
  if (screen.name === 'vessels') page = h(VesselList, { vessels: store.state.vessels, addVessel: store.addVessel, navigate: setScreen })
  if (screen.name === 'vessel') { const vessel = store.state.vessels.find((item) => item.id === screen.id); page = h(VesselDetail, { vessel, medicines: store.state.inventories[containerKey('vessel', screen.id)] || [], islands: store.state.islands, store, navigate: setScreen }) }
  if (screen.name === 'inventory') page = h(InventoryList, { vessels: store.state.vessels, islands: store.state.islands, navigate: setScreen })
  if (screen.name === 'storage') page = h(StorageDetail, { kind: screen.kind, id: screen.id, medicines: store.state.inventories[containerKey(screen.kind, screen.id)] || [], store, navigate: setScreen })
  if (screen.name === 'tracking') page = h(Tracking, { vessels: store.state.vessels, portEvents: store.state.portEvents || {} })
  if (screen.name === 'requests') page = h(RequestPage, { store, navigate: setScreen })
  if (screen.name === 'request-history') page = h(RequestHistory, { requests: store.state.requests || [], navigate: setScreen })
  return h('div', { className: 'app-shell' }, h(Header, { goHome, isHome: screen.name === 'home' }), h('main', null, page), h('footer', null, 'MANUS Medical Transportation Management · Simulation'))
}

ReactDOM.createRoot(document.getElementById('root')).render(h(App))
