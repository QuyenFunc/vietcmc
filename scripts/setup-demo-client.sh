#!/bin/bash
# Setup Demo Client - Tự động đăng ký client và config demo website

set -e

echo "=========================================="
echo "🚀 Setup Demo Client for VietCMS"
echo "=========================================="

# Config
API_URL="${VIETCMS_API_URL:-http://localhost/api/v1}"
DEMO_EMAIL="${DEMO_EMAIL:-demo@example.com}"
DEMO_PASSWORD="${DEMO_PASSWORD:-demo123456}"
DEMO_ORG="${DEMO_ORG:-Demo Organization}"
WEBHOOK_URL="${WEBHOOK_URL:-http://demo-website:5001/webhooks/moderation}"

echo ""
echo "📋 Configuration:"
echo "   API URL: $API_URL"
echo "   Email: $DEMO_EMAIL"
echo "   Organization: $DEMO_ORG"
echo "   Webhook URL: $WEBHOOK_URL"
echo ""

# Step 1: Register client
echo "📝 Step 1: Registering demo client..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"organization_name\": \"$DEMO_ORG\",
    \"email\": \"$DEMO_EMAIL\",
    \"password\": \"$DEMO_PASSWORD\",
    \"webhook_url\": \"$WEBHOOK_URL\"
  }")

echo "$REGISTER_RESPONSE"

API_KEY=$(echo "$REGISTER_RESPONSE" | grep -oP '"api_key":\s*"\K[^"]+' || true)
HMAC_SECRET=$(echo "$REGISTER_RESPONSE" | grep -oP '"hmac_secret":\s*"\K[^"]+' || true)

if [ -z "$API_KEY" ]; then
  echo "❌ Failed to register client. Response:"
  echo "$REGISTER_RESPONSE"
  exit 1
fi

echo "✅ Client registered successfully!"
echo ""
echo "📋 Credentials:"
echo "   API Key: $API_KEY"
echo "   HMAC Secret: $HMAC_SECRET"
echo ""

# Step 2: Create/Update .env file
echo "📝 Step 2: Updating .env file..."

ENV_FILE=".env"

# Update or add env vars
if grep -q "DEMO_API_KEY=" "$ENV_FILE" 2>/dev/null; then
  sed -i "s/DEMO_API_KEY=.*/DEMO_API_KEY=$API_KEY/" "$ENV_FILE"
else
  echo "DEMO_API_KEY=$API_KEY" >> "$ENV_FILE"
fi

if grep -q "DEMO_HMAC_SECRET=" "$ENV_FILE" 2>/dev/null; then
  sed -i "s/DEMO_HMAC_SECRET=.*/DEMO_HMAC_SECRET=$HMAC_SECRET/" "$ENV_FILE"
else
  echo "DEMO_HMAC_SECRET=$HMAC_SECRET" >> "$ENV_FILE"
fi

echo "✅ .env file updated"
echo ""

# Step 3: Restart demo website
echo "📝 Step 3: Restarting demo website..."
docker-compose restart demo-website

echo ""
echo "=========================================="
echo "✅ Demo Client Setup Complete!"
echo "=========================================="
echo ""
echo "📍 Demo Website: http://localhost:5000"
echo "📍 Client Dashboard: http://localhost/client-login"
echo ""
echo "🔑 Login Credentials:"
echo "   Email: $DEMO_EMAIL"
echo "   Password: $DEMO_PASSWORD"
echo ""
echo "💡 Test the flow:"
echo "   1. Open demo website: http://localhost:5000"
echo "   2. Submit a comment"
echo "   3. Check client dashboard for results"
echo ""

