# ReggeStar 🎵⭐

_Product Vision Document_

---

## Product Overview

**Name**: ReggeStar  
**Tagline**: "Star-Rank Your Sound"  
**Type**: Music-Centric Mobile Application  
**Platform**: iOS, Android  
**Launch Target**: Q3 2026

---

## Core Concept

ReggeStar is a vibe-driven music app that lets users **star-rank** tracks based on mood, energy, and vibe. The app learns user taste and builds evolving playlists with optional AI-generated "ReggeStar Sessions."

---

## Problem Statement

Music discovery is either:
- **Too passive** (algorithm-driven playlists, no control)
- **Too manual** (creating playlists takes forever)
- **Too disconnected** (mood and vibe are hard to express)

Existing apps let you like/dislike. They don't let you express *how* a song makes you feel.

---

## Solution

ReggeStar introduces **Vibe-Based Rating**:
- Rate songs 1-5 stars *per mood dimension*
- Build playlists by vibe, not just genre
- Let AI recommend based on your unique vibe profile

---

## Target Audience

| Segment | Demographics | Pain Point |
|---------|--------------|------------|
| Music Explorers | 18-35, streaming users | Want discovery, not algorithm recycling |
| Mood Listeners | 25-45, varied | Want music that matches their mood |
| Reggae/Roots Fans | 18-55, genre loyal | Want genre-focused discovery |
| Vibe Curators | 20-40, playlist obsessives | Want precise control over mood |

---

## Key Features

### 1. Star-Rank System

| Feature | Description |
|---------|-------------|
| **Mood Rating** | Rate each song on 5 vibes: Chill, Energetic, Melancholy, Uplifting, Intense |
| **Star Ranking** | Classic 1-5 star rating |
| **Vibe Tags** | Add custom tags: "rainy day," "gym pump," "Sunday morning" |
| **Quick Rate** | Swipe right to save, left to skip, with vibe quick-select |

### 2. Smart Playlists

| Feature | Description |
|---------|-------------|
| **Mood Match** | "Create playlist: I'm feeling [Chill + Melancholy]" |
| **Energy Curve** | Build a playlist with intentional energy flow |
| **Vibe Mix** | Blend multiple moods into one playlist |
| **Time-Based** | "Morning wind-down," "Afternoon focus," "Night drive" |

### 3. ReggeStar Sessions (AI)

| Feature | Description |
|---------|-------------|
| **AI Recommendations** | "Play me something like [song] but more [Uplifting]" |
| **Session Generator** | AI generates a themed listening session |
| **Vibe Analysis** | App analyzes your ratings to find patterns |
| **Surprise Me** | Random vibe exploration mode |

### 4. Social Features

| Feature | Description |
|---------|-------------|
| **Profile** | Display your vibe profile (top moods, genres) |
| **Share Vibe** | Share playlists with vibe tags |
| **Follow** | Follow friends' vibe profiles |
| **Discover** | See what similar vibes are listening to |

### 5. Music Integration

| Feature | Description |
|---------|-------------|
| **Streaming APIs** | Spotify, Apple Music integration (where available) |
| **Local Files** | Import from device library |
| **Mock Mode** | Demo mode with sample library |
| **YouTube Music** | Optional integration |

---

## User Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      ONBOARDING                             │
├─────────────────────────────────────────────────────────────┤
│  1. Select mood preferences                                │
│  2. Connect music service OR use demo                       │
│  3. Rate 5 seed songs to calibrate AI                     │
│  4. Choose vibe profile name                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      MAIN APP                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   DISCOVER │  │  PLAYLISTS  │  │   PROFILE   │       │
│  │            │  │             │  │             │       │
│  │ - For You  │  │ - My Mixes  │  │ - Vibe Stats│       │
│  │ - By Vibe  │  │ - By Mood   │  │ - History   │       │
│  │ - New      │  │ - By Energy │  │ - Followers │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                             │
│                     ┌─────────────┐                         │
│                     │ NOW PLAYING │                         │
│                     │ ★★★★☆       │                         │
│                     │ Chill       │                         │
│                     └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Monetization

### Free Tier
- Basic star-ranking
- 3 custom playlists
- Limited AI sessions
- Ads (optional)

### Premium Tier ($4.99/month)
- Unlimited playlists
- Unlimited AI sessions
- No ads
- Priority AI matching
- Export playlists

### Future Revenue
- Artist partnerships
- Sponsored vibe campaigns
- Merchandise integration

---

## Technical Architecture

### Stack
| Component | Technology |
|-----------|------------|
| Mobile | React Native |
| Backend | Node.js + PostgreSQL |
| AI/ML | Python (recommendation engine) |
| Music API | Spotify SDK, Apple Music API |
| Storage | S3, Redis |

### Key Services
```
┌─────────────────────────────────────────────────────┐
│                   MOBILE APP                        │
│  (TAPTAP)                                          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                   API GATEWAY                        │
│  (PIPELINE)                                        │
└──────┬──────────────┬──────────────┬───────────────┘
       │              │              │
┌──────▼──────┐ ┌─────▼─────┐ ┌────▼────────┐
│ User Service│ │Playlist   │ │AI Engine    │
│             │ │Service    │ │(MILL)       │
└──────┬──────┘ └─────┬─────┘ └──────┬──────┘
       │              │              │
┌──────▼──────────────▼──────────────▼──────────────┐
│              DATA LAYER                            │
│  PostgreSQL + Redis + S3                          │
└───────────────────────────────────────────────────┘
```

---

## Design Direction

### Visual Identity

| Element | Specification |
|---------|---------------|
| **Primary Color** | Warm Gold (#FFD700) |
| **Secondary Color** | Deep Green (#1B4D3E) |
| **Accent** | Sunset Orange (#FF6B35) |
| **Background** | Off-White / Warm Gray |
| **Dark Mode** | Deep Green + Gold accents |

### Typography
- **Headlines**: Bold, rounded sans-serif
- **Body**: Clean, readable sans-serif
- **Vibe Tags**: Handwritten-style for personality

### Iconography
- Star motifs throughout
- Music notes with personality
- Warm, inviting illustrations

### Animations
- Smooth transitions between screens
- Star-filling animations on rating
- Pulsing vibes on active playback

---

## Team Ownership

| Agent | Role |
|-------|------|
| **STACKTRACE** | System architecture |
| **TAPTAP** | Mobile app development |
| **PIPELINE** | Backend, API, integrations |
| **BUGCATCHER** | Testing, QA |
| **SENTINEL** | Security, data privacy |
| **VELUM** | Brand identity, visual design |
| **SCRIBBLE** | Copy, in-app content |
| **MILL** | AI/ML recommendation engine |

---

## Milestones

| Milestone | Target | Description |
|-----------|--------|-------------|
| M1 | Week 4 | Prototype with mock data |
| M2 | Week 8 | Basic app with star-ranking |
| M3 | Week 12 | Playlists + basic AI |
| M4 | Week 16 | Full app, ready for beta |
| M5 | Week 20 | Beta launch |
| M6 | Week 24 | Public launch |

---

## Competitive Landscape

| Competitor | Strength | ReggeStar Differentiation |
|------------|----------|---------------------------|
| Spotify | Discovery algorithms | Vibe-based, not algorithm-based |
| Apple Music | Integration | More expressive rating |
| Pandora | Mood | Modern, social, AI-powered |
| Last.fm | Scrobbling | Mobile-first, simpler |

---

## Success Metrics

| Metric | Target (Year 1) |
|--------|-----------------|
| Downloads | 100,000 |
| Monthly Active Users | 25,000 |
| Premium Subscribers | 2,500 |
| Average Session Length | 18 minutes |
| Rating Completion Rate | 65% |

---

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Music API limitations | Build mock mode, partner early |
| AI recommendation quality | Start simple, iterate based on feedback |
| Discovery against giants | Focus on niche: vibe-first users |
| Monetization | Freemium, prove value before scaling |

---

## Next Steps

1. **Week 1-2**: Finalize feature prioritization
2. **Week 3-4**: Build prototype with TAPTAP
3. **Week 5-8**: Backend development with PIPELINE
4. **Week 9-12**: AI engine with MILL
5. **Week 13-16**: Testing with BUGCATCHER
6. **Week 17-20**: Beta with select users
7. **Week 21-24**: Launch

---

_"Music is feeling. ReggeStar captures it."_
