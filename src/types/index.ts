export type EventType = 'wedding' | 'corporate' | 'funeral' | 'cultural' | 'private'

export type Stage =
  | 'new'
  | 'contacted'
  | 'visit-booked'
  | 'post-visit'
  | 'confirmed'
  | 'lost'

export type Room = 'pohutukawa' | 'manukau' | 'somerset' | null

export type ContactMethod = 'email' | 'phone' | 'social' | 'referral' | 'walk-in'

export interface Lead {
  id: string
  name: string
  eventType: EventType
  eventDate: string | null
  guestCount: number | null
  contactMethod: ContactMethod
  stage: Stage
  estimatedValue: number | null
  enquiryDate: string
  lastContact: string
  visitDate: string | null
  followUpDue: string | null
  depositReceived: boolean
  depositAmount: number | null
  room: Room
  notes: string
  competingVenues: string[]
  source: string
}

export interface RoomBlock {
  id: string
  room: Room
  date: string
  reason: string
}

export interface Settings {
  operatorName: string
  venueName: string
  apiKey: string
  monthlyTargets: Record<string, number>
  roomBlocks: RoomBlock[]
}

export type MessageType =
  | 'first-wedding'
  | 'first-corporate'
  | 'first-funeral'
  | 'first-private'
  | 'first-vague'
  | 'visit-invite'
  | 'post-visit-24h'
  | 'post-visit-48h'
  | 'reengage-3-7'
  | 'reengage-7plus'
  | 'final-close'
  | 'deposit-request'
  | 'date-hold'
  | 'stale-30d'

export const STAGE_ORDER: Stage[] = [
  'new',
  'contacted',
  'visit-booked',
  'post-visit',
  'confirmed',
  'lost',
]

export const STAGE_LABEL: Record<Stage, string> = {
  new: 'New',
  contacted: 'Contacted',
  'visit-booked': 'Visit Booked',
  'post-visit': 'Post-Visit',
  confirmed: 'Confirmed',
  lost: 'Lost',
}

export const STAGE_WEIGHT: Record<Stage, number> = {
  new: 0.1,
  contacted: 0.2,
  'visit-booked': 0.4,
  'post-visit': 0.65,
  confirmed: 1,
  lost: 0,
}

export const EVENT_LABEL: Record<EventType, string> = {
  wedding: 'Wedding',
  corporate: 'Corporate',
  funeral: 'Funeral',
  cultural: 'Cultural',
  private: 'Private',
}

export const ROOM_LABEL: Record<NonNullable<Room>, string> = {
  pohutukawa: 'Pohutukawa',
  manukau: 'Manukau',
  somerset: 'Somerset',
}

export const ROOM_CAPACITY: Record<NonNullable<Room>, number> = {
  pohutukawa: 80,
  manukau: 220,
  somerset: 60,
}
