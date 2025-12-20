# Events and Alerts Management System

## Phase 1: Database Models & Mock Generator ✅
- [x] Create SQLModel database models (AlertRule, AlertEvent) with proper relationships
- [x] Implement JSON-aware mock generator function that parses parameters
- [x] Set up basic State class with database initialization
- [x] Create app shell with sidebar + content layout

## Phase 2: Alert Rules Management UI ✅
- [x] Build Alert Rules list view with data table showing all rules
- [x] Create Add/Edit Alert Rule form with JSON parameters input
- [x] Implement Period UI with Value + Unit fields and conversion to seconds
- [x] Implement rule activation toggle and delete functionality
- [x] Add importance filtering and sorting capabilities

## Phase 3: Alert Events Dashboard & Actions ✅
- [x] Build Alert Events dashboard with real-time event list
- [x] Implement acknowledge event functionality with timestamp
- [x] Add event filtering by importance and text search
- [x] Create statistics cards showing event counts and trends
- [x] Add manual trigger button for mock alert generation
- [x] Historical Blotter with all columns (Time, Ticker, Message, Importance, Ack Status, Comment)