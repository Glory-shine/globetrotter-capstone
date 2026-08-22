# GlobeTrotter Data Source Design

## Overview

The GlobeTrotter system uses a **polyglot data storage approach** with multiple independent databases, each owned by a single microservice. This document defines the data schema, relationships, and access patterns for all data sources.

---

## 1. Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                         Frontend (Vue 3)                        │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │    API Gateway        │
         │      Port 8000        │
         └───────┬───────┬───┬───┘
                 │       │   │
        ┌────────┘       │   └──────────┐
        │                │             │
        ▼                ▼             ▼
   ┌─────────┐    ┌──────────┐   ┌──────────────┐
   │ User    │    │Itinerary │   │Recommendation
   │Service  │    │Service   │   │Service
   │ :8001   │    │  :8002   │   │ :8003
   └────┬────┘    └────┬─────┘   └──────┬───────┘
        │              │                │
        ▼              ▼                ▼
   ┌────────┐    ┌──────────┐    ┌────────────────┐
   │ user   │    │itinerary │    │recommendation  │
   │ _db    │    │_db       │    │_db             │
   │        │    │          │    │                │
   │PgSQL   │    │PgSQL     │    │PgSQL           │
   │5432    │    │5432      │    │5432            │
   └────────┘    └──────────┘    └────────────────┘
        │              │                │
        └──────┬───────┴────────┬───────┘
               │                │
        ┌──────▼────┐    ┌──────▼──────┐
        │  RabbitMQ │    │ File Storage│
        │  Messaging│    │(Wikimedia)  │
        │  :5672    │    │             │
        └───────────┘    └─────────────┘
```

**Data Flow:**
- All services read/write their own database
- Inter-service communication via REST APIs (synchronous) and RabbitMQ (asynchronous)
- External data sources: Wikimedia Commons (images), OpenStreetMap (map tiles)

---

## 2. Database Schemas

### 2.1 User Service Database (`user_db`)

**Purpose:** User authentication, profiles, preferences, and accounts.

#### Table: `users`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `username` | VARCHAR(100) | | ✓ | UNIQUE |
| `email` | VARCHAR(255) | | ✓ | UNIQUE |
| `password_hash` | VARCHAR(255) | | ✓ | bcrypt/Argon2 |
| `full_name` | VARCHAR(255) | | | Optional |
| `bio` | TEXT | | | Optional |
| `profile_picture_url` | VARCHAR(2048) | | | Optional URL to external image |
| `created_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |
| `deleted_at` | TIMESTAMP | | | Soft delete |

#### Table: `user_preferences`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `user_id` | UUID | | ✓ | FK → users.id |
| `preferred_budget_range` | VARCHAR(50) | | | LOW/MEDIUM/HIGH |
| `preferred_transport_mode` | VARCHAR(20) | | | moto/taxi/walking |
| `preferred_language` | VARCHAR(10) | | | ISO 639-1 code (en/fr) |
| `notification_enabled` | BOOLEAN | | ✓ | DEFAULT TRUE |
| `theme` | VARCHAR(20) | | | light/dark |
| `created_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |

#### Table: `user_interests`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `user_id` | UUID | | ✓ | FK → users.id |
| `tag` | VARCHAR(50) | | ✓ | (e.g., "history", "nature", "food") |
| `created_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |

**Indexes:**
```sql
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_interests_user_id ON user_interests(user_id);
```

**Relationships:**
- `users` ↔ `user_preferences` (1:1)
- `users` ↔ `user_interests` (1:N)

---

### 2.2 Itinerary Service Database (`itinerary_db`)

**Purpose:** User travel plans, itinerary management, visited locations history.

#### Table: `itineraries`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `user_id` | UUID | | ✓ | External FK (user_db) |
| `title` | VARCHAR(255) | | ✓ | e.g., "Weekend in Bafoussam" |
| `description` | TEXT | | | Optional |
| `status` | VARCHAR(20) | | ✓ | draft/planned/in_progress/completed |
| `start_date` | DATE | | | Optional |
| `end_date` | DATE | | | Optional |
| `budget_usd` | DECIMAL(10,2) | | | Estimated total budget |
| `created_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |

#### Table: `itinerary_items`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `itinerary_id` | UUID | | ✓ | FK → itineraries.id |
| `destination_id` | UUID | | ✓ | External FK (recommendation_db) |
| `position` | INTEGER | | ✓ | Order in itinerary (0-indexed) |
| `visit_date` | DATE | | | Optional |
| `duration_hours` | INTEGER | | | Estimated visit duration |
| `notes` | TEXT | | | User's notes for this stop |
| `created_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |

#### Table: `visit_history`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `user_id` | UUID | | ✓ | External FK (user_db) |
| `destination_id` | UUID | | ✓ | External FK (recommendation_db) |
| `visited_at` | TIMESTAMP | | ✓ | When user visited |
| `rating` | INTEGER | | | 1-5 stars (nullable = not rated yet) |
| `notes` | TEXT | | | User's personal notes |
| `created_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |

**Indexes:**
```sql
CREATE INDEX idx_itineraries_user_id ON itineraries(user_id);
CREATE INDEX idx_itinerary_items_itinerary_id ON itinerary_items(itinerary_id);
CREATE INDEX idx_itinerary_items_destination_id ON itinerary_items(destination_id);
CREATE INDEX idx_visit_history_user_id ON visit_history(user_id);
CREATE INDEX idx_visit_history_destination_id ON visit_history(destination_id);
CREATE INDEX idx_visit_history_visited_at ON visit_history(visited_at);
```

**Relationships:**
- `itineraries` ↔ `itinerary_items` (1:N)
- `users` (external) ↔ `itineraries` (1:N)
- `destinations` (external) ↔ `itinerary_items` (1:N)

---

### 2.3 Recommendation Service Database (`recommendation_db`)

**Purpose:** Destination catalog, pricing data, comments, and recommendations.

#### Table: `destinations`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `name` | VARCHAR(255) | | ✓ | e.g., "Chefferie Supérieure" |
| `description` | TEXT | | ✓ | Detailed description |
| `category` | VARCHAR(50) | | ✓ | cultural/nature/food/historical/modern |
| `latitude` | DECIMAL(10,8) | | ✓ | GPS coordinate |
| `longitude` | DECIMAL(11,8) | | ✓ | GPS coordinate |
| `address` | VARCHAR(255) | | | Street address |
| `phone` | VARCHAR(20) | | | Contact number |
| `opening_hours` | VARCHAR(255) | | | e.g., "09:00-17:00" |
| `entry_fee_fcfa` | DECIMAL(10,2) | | | Entry cost in FCFA |
| `image_url` | VARCHAR(2048) | | | URL to Wikimedia Commons |
| `image_credit` | VARCHAR(255) | | | Attribution string |
| `featured` | BOOLEAN | | ✓ | DEFAULT FALSE |
| `is_published` | BOOLEAN | | ✓ | DEFAULT TRUE |
| `created_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |

#### Table: `destination_tags`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `destination_id` | UUID | | ✓ | FK → destinations.id |
| `tag` | VARCHAR(50) | | ✓ | (e.g., "history", "nature", "food") |

#### Table: `activities`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `destination_id` | UUID | | ✓ | FK → destinations.id |
| `name` | VARCHAR(255) | | ✓ | Activity name |
| `description` | TEXT | | | |
| `price_fcfa` | DECIMAL(10,2) | | ✓ | Activity cost |
| `duration_minutes` | INTEGER | | | Optional |
| `difficulty` | VARCHAR(20) | | | easy/moderate/hard |
| `position` | INTEGER | | ✓ | Display order |
| `is_published` | BOOLEAN | | ✓ | DEFAULT TRUE |
| `created_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |

#### Table: `fare_cache`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `from_destination_id` | UUID | | ✓ | FK → destinations.id |
| `to_destination_id` | UUID | | ✓ | FK → destinations.id |
| `mode` | VARCHAR(20) | | ✓ | moto/taxi |
| `estimated_fare_fcfa` | DECIMAL(10,2) | | ✓ | Calculated fare |
| `distance_km` | DECIMAL(8,2) | | ✓ | Road distance estimate |
| `created_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |
| `expires_at` | TIMESTAMP | | ✓ | TTL (24 hours typical) |

#### Table: `comments`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `destination_id` | UUID | | ✓ | FK → destinations.id |
| `user_id` | UUID | | ✓ | External FK (user_db) |
| `parent_comment_id` | UUID | | | FK → comments.id (for replies) |
| `content` | TEXT | | ✓ | Comment text |
| `rating` | INTEGER | | | 1-5 stars |
| `likes_count` | INTEGER | | ✓ | DEFAULT 0 |
| `is_published` | BOOLEAN | | ✓ | DEFAULT TRUE |
| `created_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |

#### Table: `comment_likes`

| Column | Type | PK | NN | Constraints |
|--------|------|----|----|-------------|
| `id` | UUID | ✓ | ✓ | PK |
| `comment_id` | UUID | | ✓ | FK → comments.id |
| `user_id` | UUID | | ✓ | External FK (user_db) |
| `created_at` | TIMESTAMP | | ✓ | DEFAULT NOW() |
| **Unique Constraint** | | | | (comment_id, user_id) |

**Indexes:**
```sql
CREATE INDEX idx_destinations_category ON destinations(category);
CREATE INDEX idx_destinations_featured ON destinations(featured);
CREATE INDEX idx_destination_tags_tag ON destination_tags(tag);
CREATE INDEX idx_activities_destination_id ON activities(destination_id);
CREATE INDEX idx_fare_cache_from_to ON fare_cache(from_destination_id, to_destination_id);
CREATE INDEX idx_comments_destination_id ON comments(destination_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_comment_id);
CREATE INDEX idx_comment_likes_comment_id ON comment_likes(comment_id);
CREATE INDEX idx_comment_likes_user_id ON comment_likes(user_id);
```

**Relationships:**
- `destinations` ↔ `destination_tags` (1:N)
- `destinations` ↔ `activities` (1:N)
- `destinations` ↔ `comments` (1:N)
- `comments` ↔ `comment_likes` (1:N)
- `comments` ↔ `comments` (self-referential, 1:N for replies)
- `users` (external) ↔ `comments` (1:N)

---

## 3. Data Access Patterns

### 3.1 User Service

| Operation | Pattern | Performance Target |
|-----------|---------|-------------------|
| Register new user | INSERT INTO users + INSERT INTO user_preferences | ~50ms |
| Login (authenticate) | SELECT users WHERE username/email | ~20ms |
| Get user profile | SELECT users WHERE id + SELECT user_preferences + SELECT user_interests | ~30ms |
| Update preferences | UPDATE user_preferences WHERE user_id | ~20ms |
| List user interests | SELECT user_interests WHERE user_id | ~15ms |

**Caching Strategy:**
- Cache user preferences in application memory with 15-minute TTL
- Cache user interests list with 30-minute TTL
- Invalidate on update via event

---

### 3.2 Itinerary Service

| Operation | Pattern | Performance Target |
|-----------|---------|-------------------|
| Create itinerary | INSERT into itineraries | ~30ms |
| Get itinerary with items | SELECT itineraries + SELECT itinerary_items (join) | ~50ms |
| Add destination to itinerary | INSERT into itinerary_items | ~20ms |
| Reorder items | UPDATE itinerary_items (batch) | ~40ms |
| Record visit | INSERT into visit_history | ~25ms |
| Get user's itineraries | SELECT itineraries WHERE user_id ORDER BY created_at DESC (paginated) | ~40ms |

**Caching Strategy:**
- Cache individual itinerary details with 5-minute TTL
- Cache list of user itineraries with 5-minute TTL
- Invalidate on any write operation

---

### 3.3 Recommendation Service

| Operation | Pattern | Performance Target |
|-----------|---------|-------------------|
| Get all destinations (paginated) | SELECT destinations LIMIT/OFFSET | ~60ms |
| Filter by category/tags | SELECT destinations + destination_tags WHERE category/tag | ~80ms |
| Get destination details | SELECT destinations + activities + comments (joins) | ~100ms |
| Calculate fare | Compute from coordinates or hit fare_cache | ~30ms cache / ~100ms compute |
| Add comment | INSERT into comments | ~20ms |
| Get comments for destination | SELECT comments WHERE destination_id ORDER BY created_at DESC | ~60ms |
| Like comment | INSERT into comment_likes (with upsert) | ~25ms |

**Caching Strategy:**
- Cache full destination list with 10-minute TTL (rebuild on schema change)
- Cache individual destination details with 10-minute TTL
- Cache fare estimates with 24-hour TTL
- Cache comment list per destination with 2-minute TTL (high churn)
- Use Redis for cache layer to support concurrent access

---

## 4. Inter-Service Data Dependencies

### 4.1 Synchronous API Calls

**Recommendation Service → User Service**
- Endpoint: `GET /users/{user_id}`
- Purpose: Retrieve user preferences for personalized recommendations
- Fallback: Return generic recommendations if user service unavailable
- Timeout: 5 seconds

**Recommendation Service → Itinerary Service**
- Endpoint: `GET /itineraries/{user_id}`
- Purpose: Fetch user's visit history for filtering recommendations
- Fallback: Return all destinations if itinerary service unavailable
- Timeout: 5 seconds

**Itinerary Service → Recommendation Service**
- Endpoint: `GET /destinations/{destination_id}`
- Purpose: Validate that a destination exists before adding to itinerary
- Fallback: Log warning and allow; recommendation service verifies on read
- Timeout: 5 seconds

### 4.2 Asynchronous Events (RabbitMQ)

**Event: `itinerary.created`**
- **Producer:** Itinerary Service
- **Consumer:** Recommendation Service
- **Payload:**
  ```json
  {
    "event_type": "itinerary.created",
    "itinerary_id": "uuid",
    "user_id": "uuid",
    "timestamp": "2024-08-22T10:00:00Z"
  }
  ```
- **Purpose:** Trigger recommendation cache refresh for user
- **Retry Policy:** 3 attempts, 5-second backoff

**Event: `comment.created`**
- **Producer:** Recommendation Service
- **Consumer:** User Service (optional, for notifications)
- **Payload:**
  ```json
  {
    "event_type": "comment.created",
    "comment_id": "uuid",
    "destination_id": "uuid",
    "user_id": "uuid",
    "timestamp": "2024-08-22T10:00:00Z"
  }
  ```
- **Purpose:** Send notification to destination followers (future feature)

---

## 5. External Data Sources

### 5.1 Wikimedia Commons (Images)

**Source:** `https://commons.wikimedia.org/`

**Usage:**
- Store image URLs in `destinations.image_url`
- Images are hotlinked; no local download/storage
- Attribution via `destinations.image_credit`
- Categories: `Category:Bafoussam`, `Category:Chefferie_de_Bafoussam`

**Reliability:**
- Dependent on Wikimedia CDN availability
- Fallback: Display placeholder image with credit attribution
- No caching of image data; only URL stored

### 5.2 OpenStreetMap (Map Tiles & Geocoding)

**Source:** `https://www.openstreetmap.org/`

**Usage:**
- Map tile provider: Leaflet + OSM tiles (default)
- Geocoding: Used for GPS → address conversion (optional)

**Tile Layer URL:**
```
https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

**Attribution (required by license):**
```
© OpenStreetMap contributors
```

---

## 6. Data Consistency & Integrity

### 6.1 Consistency Model

- **Per-Service ACID:** Each service maintains ACID guarantees within its database
- **Cross-Service:** Eventual consistency via events
- **Conflict Resolution:** Last-write-wins for user preferences

### 6.2 Foreign Key Constraints

**Hard constraints (database-enforced):**
- Within service databases only
- `itinerary_items` → `itineraries` (ON DELETE CASCADE)
- `destination_tags` → `destinations` (ON DELETE CASCADE)
- `activities` → `destinations` (ON DELETE CASCADE)
- `comments` → `destinations` (ON DELETE CASCADE)

**Soft constraints (application-enforced):**
- `itineraries.user_id` → `users.id` (validates on write)
- `itinerary_items.destination_id` → `destinations.id` (async check)
- `comments.user_id` → `users.id` (async validation)
- `visit_history.user_id` → `users.id` (async validation)
- `visit_history.destination_id` → `destinations.id` (async validation)

### 6.3 Orphan Data Handling

**Itinerary Service:**
- If referenced `destination_id` (in recommendation_db) is deleted, `itinerary_items` rows become orphaned
- Resolution: Periodically run cleanup job to mark these as `is_deleted=TRUE`

**Comment Service:**
- If user (in user_db) is deleted, comments remain but user lookup fails
- Resolution: Mark user_id as anonymous in comments or cascade delete via event listener

---

## 7. Backup & Recovery Strategy

### 7.1 Backup Schedule

| Database | Frequency | Retention | Location |
|----------|-----------|-----------|----------|
| user_db | Daily (02:00 UTC) | 30 days | S3 bucket: `globetrotter-backups-prod` |
| itinerary_db | Daily (02:15 UTC) | 30 days | S3 bucket: `globetrotter-backups-prod` |
| recommendation_db | Daily (02:30 UTC) | 30 days | S3 bucket: `globetrotter-backups-prod` |

### 7.2 Recovery Procedure

```bash
# Example: Restore recommendation_db to point in time
pg_restore -d recommendation_db \
  s3://globetrotter-backups-prod/recommendation_db_2024-08-22.sql.gz
```

---

## 8. Monitoring & Alerting

### 8.1 Key Metrics

| Metric | Threshold | Action |
|--------|-----------|--------|
| Database connection pool utilization | > 80% | Scale up connections |
| Query latency (p95) | > 200ms | Review slow queries |
| Replication lag | > 5s | Investigate replication |
| Disk usage (per DB) | > 80% | Plan storage expansion |
| Open connections per DB | > 100 | Investigate connection leak |

### 8.2 Alerting

- **Email alerts** for database outages
- **Slack notifications** for performance degradation
- **PagerDuty** escalation for critical failures

---

## 9. Scaling & Performance Optimization

### 9.1 Current Approach

- **Single PostgreSQL instance** with 3 separate databases
- **Per-service connection pooling** via PgBouncer or SQLAlchemy

### 9.2 Future Scaling

**Phase 2 (Read Replicas):**
- Add read replicas for user_db and recommendation_db
- Route SELECT queries to replicas, writes to primary
- Replication lag monitoring

**Phase 3 (Sharding):**
- Shard itinerary_db by `user_id`
- Shard recommendation_db by geographic region
- Consistent hashing for shard selection

**Phase 4 (Cache Layer):**
- Introduce Redis for session caching
- Cache frequently accessed destinations
- Cache user preferences and interests

---

## 10. Data Retention & Privacy

### 10.1 Retention Policies

| Data Type | Retention | Notes |
|-----------|-----------|-------|
| User accounts | Indefinite | Or until user deletion request (GDPR) |
| Visit history | 2 years | Historical analytics |
| Comments | Indefinite | (unless user requests deletion) |
| Itineraries | 2 years (archived) | Deleted after 2 years inactivity |
| Fare cache | 24 hours | Automatic expiration |
| API logs | 30 days | For debugging & compliance |

### 10.2 GDPR Compliance

- **Right to deletion:** Hard delete from all tables except audit logs
- **Right to portability:** Export endpoint returns user data as JSON
- **Data anonymization:** Replace user_id with NULL in comments/ratings on deletion

---

## 11. Entity-Relationship Diagram (Summary)

```
┌─────────────────────────────────────────────────────────────┐
│                      USER_DB                                │
│  ┌──────────┐  ┌──────────────────┐  ┌────────────────┐    │
│  │  users   │  │ user_preferences │  │ user_interests │    │
│  ├──────────┤  ├──────────────────┤  ├────────────────┤    │
│  │ id (PK)  │  │ id (PK)          │  │ id (PK)        │    │
│  │ username │  │ user_id (FK)──┐  │  │ user_id (FK)─┐ │    │
│  │ email    │  │ ...          │  │  │ tag         │ │    │
│  └──────────┘  └──────────────┘  └────────────────┘ │    │
│       ▲              ▲                              │    │
│       └──────┬───────┘                              │    │
│            1:1,1:N                                  │    │
└─────────────────────────────────────────────────────────────┘
        │
        │ EXTERNAL REFERENCES (REST/Events)
        │
        ├─────────────────────────────────────────────────────┐
        │              ITINERARY_DB                           │
        │  ┌─────────────────────┐  ┌──────────────────────┐  │
        │  │   itineraries       │  │  itinerary_items     │  │
        │  ├─────────────────────┤  ├──────────────────────┤  │
        │  │ id (PK)             │  │ id (PK)              │  │
        │  │ user_id (EXT FK)    │  │ itinerary_id (FK)────┤  │
        │  │ ...                 │  │ destination_id (EXT) │  │
        │  └─────────────────────┘  └──────────────────────┘  │
        │           │                         │               │
        │           └──────────────────────────┘               │
        │                   1:N                                │
        │  ┌──────────────────────────────────────────────┐   │
        │  │         visit_history                        │   │
        │  ├──────────────────────────────────────────────┤   │
        │  │ id (PK)                                      │   │
        │  │ user_id (EXT FK) → users                     │   │
        │  │ destination_id (EXT FK) → destinations       │   │
        │  │ visited_at, rating, notes                    │   │
        │  └──────────────────────────────────────────────┘   │
        │                                                      │
        └──────────────────────────────────────────────────────┘
        │
        │
        ├─────────────────────────────────────────────────────┐
        │          RECOMMENDATION_DB                          │
        │  ┌──────────────────┐  ┌──────────────────────────┐ │
        │  │ destinations     │  │  destination_tags        │ │
        │  ├──────────────────┤  ├──────────────────────────┤ │
        │  │ id (PK)          │  │ id (PK)                  │ │
        │  │ name, category   │  │ destination_id (FK)──────┤ │
        │  │ lat, lon, ...    │  │ tag                      │ │
        │  └────────┬─────────┘  └──────────────────────────┘ │
        │           │                                          │
        │           ├──┬─────────────────────┬──────────────┐  │
        │           │  │                     │              │  │
        │  ┌────────▼────────┐  ┌──────────┴───┐  ┌────────┴────────┐ │
        │  │   activities    │  │   comments   │  │  fare_cache     │ │
        │  ├─────────────────┤  ├──────────────┤  ├─────────────────┤ │
        │  │ id (PK)         │  │ id (PK)      │  │ id (PK)         │ │
        │  │ destination_... │  │ destination..│  │ from/to_dest... │ │
        │  │ name, price     │  │ user_id (EXT)│  │ mode, fare, ... │ │
        │  └─────────────────┘  │ content      │  └─────────────────┘ │
        │                       │              │                       │
        │                       ├─────┬────────┤                       │
        │                       │     │        │                       │
        │                    ┌──▼─────▼──┐    │                       │
        │                    │ comments   │    │                       │
        │                    │(self-ref)  │    │                       │
        │                    └────────────┘    │                       │
        │                                      │                       │
        │                       ┌──────────────▼──────────────┐        │
        │                       │     comment_likes           │        │
        │                       ├─────────────────────────────┤        │
        │                       │ id (PK)                     │        │
        │                       │ comment_id (FK)             │        │
        │                       │ user_id (EXT FK) → users    │        │
        │                       └─────────────────────────────┘        │
        │                                                               │
        └───────────────────────────────────────────────────────────────┘

LEGEND:
PK  = Primary Key
FK  = Foreign Key (same database)
EXT = External Reference (cross-database)
1:1 = One-to-One
1:N = One-to-Many
```

---

## 12. Implementation Checklist

- [ ] Define PostgreSQL schemas (SQL scripts in `/services/*/migrations/`)
- [ ] Set up connection pooling per service
- [ ] Implement soft delete pattern (add `deleted_at` to applicable tables)
- [ ] Configure indexes for common queries
- [ ] Add database constraints (unique, foreign keys, checks)
- [ ] Create backup scripts + S3 integration
- [ ] Set up monitoring dashboards (Prometheus/Grafana)
- [ ] Document data flow in wiki
- [ ] Implement GDPR compliance layer
- [ ] Add data migration tests

---

## Appendix A: SQL Migration Template

```sql
-- Migration: 0001_initial_schema.sql
-- Service: user-service
-- Created: 2024-08-22

BEGIN TRANSACTION;

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(100) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  bio TEXT,
  profile_picture_url VARCHAR(2048),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Additional tables...

COMMIT;
```

---

**Document Version:** 1.0  
**Last Updated:** 2024-08-22  
**Next Review:** 2024-09-22
