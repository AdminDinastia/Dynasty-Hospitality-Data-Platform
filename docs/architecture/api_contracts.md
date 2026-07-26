# API Endpoints MVP

## Auth (Clerk Integration)
POST   /webhooks/clerk/user     # Clerk webhook: syncs user data to PostgreSQL
                                 # Called when user signs up or updates profile

# Authentication Flow:
# 1. Frontend uses Clerk UI components (<SignIn />, <SignUp />)
# 2. Clerk returns JWT token to frontend
# 3. Frontend includes token in requests: Authorization: Bearer {token}
# 4. Backend verifies Clerk JWT on all protected endpoints
# 5. Backend extracts user_id and org_id from verified token

## Accommodations (Provider)
POST   /accommodations          # Body: {name, type, location, ...}
GET    /accommodations          # List your hotels (org_id from token)
GET    /accommodations/{id}     # Hotel detail
PATCH  /accommodations/{id}     # Body: {name?, location?, category?, ...}
PATCH  /accommodations/{id}/data-sharing  # Body: {allow_aggregated, allow_raw_sharing, revenue_share_pct}

## Uploads (Provider)
POST   /uploads                 # Body: {accommodation_id, filename} → returns pre-signed S3 URL
POST   /uploads/{id}/confirm    # Confirm file uploaded to S3
GET    /uploads                 # Query params: ?status=pending&accommodation_id=123
GET    /uploads/{id}            # Upload detail

## Datasets (Provider)
GET    /datasets                # Query params: ?status=ready&accommodation_id=123
GET    /datasets/{id}           # Dataset detail
PATCH  /datasets/{id}           # Body: {is_active: true/false}

## Points & Payments
GET    /points/balance          # Your balance (org_id from token)
GET    /points/history          # Query params: ?type=earned or ?type=spent
POST   /points/purchase         # Body: {amount_usd} → returns Stripe checkout URL
POST   /webhooks/stripe/payment # Stripe calls this when payment completes

## Revenue (Provider)
GET    /revenue/summary         # Total earned
GET    /revenue/distributions   # Query params: ?status=paid&year=2025
GET    /revenue/distributions/{id}  # Sale detail

## Stripe Connect (Provider)
POST   /stripe/connect/onboard  # Returns Stripe URL to connect bank account
GET    /stripe/connect/status   # Status: connected/pending/not_connected
POST   /webhooks/stripe/connect # Stripe calls this when account connects

## Products (Consumer)
GET    /products/aggregated     # Query params: ?location=spain&stars=4&year=2025
GET    /products/raw            # Query params: ?accommodation_id=123&year=2025
GET    /products/{id}           # Product detail
POST   /products/{id}/purchase  # Purchase access → creates entitlement

## Entitlements (Consumer)
GET    /entitlements            # Products you have access to
GET    /entitlements/{id}       # Entitlement detail
GET    /purchases               # Purchase history (alias of entitlements)

## Reports (Consumer)
GET    /reports                      # List available reports (purchased products)
GET    /reports/{entitlement_id}     # Get report data as JSON
                                      # Frontend displays it
                                      # User clicks "Download" → browser saves as PDF (react-to-pdf)

## Organizations
GET    /organizations/me        # Your organization
PATCH  /organizations/me        # Body: {name?, description?, ...}
