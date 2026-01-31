# Setup Demo Client - Auto register and configure

Write-Host "==========================================`n🚀 Setup Demo Client`n==========================================" -ForegroundColor Cyan

$API_URL = "http://localhost/api/v1"
$DEMO_EMAIL = "demo@example.com"
$DEMO_PASSWORD = "demo123456"
$DEMO_ORG = "Demo Organization"
$WEBHOOK_URL = "http://demo-website:5000/webhooks/moderation"

Write-Host "`n📋 Registering client: $DEMO_EMAIL" -ForegroundColor Yellow

$body = @{
    organization_name = $DEMO_ORG
    email = $DEMO_EMAIL
    password = $DEMO_PASSWORD
    webhook_url = $WEBHOOK_URL
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_URL/register" -Method Post -Body $body -ContentType "application/json"
    
    $API_KEY = $response.api_key
    $HMAC_SECRET = $response.hmac_secret
    
    Write-Host "✅ Registered! API Key: $API_KEY" -ForegroundColor Green
    
    # Update .env
    Write-Host "`n📝 Updating .env file..." -ForegroundColor Yellow
    
    $ENV_FILE = ".env"
    if (Test-Path $ENV_FILE) {
        $envContent = Get-Content $ENV_FILE
    } else {
        $envContent = @()
    }
    
    # Remove old entries
    $envContent = $envContent | Where-Object { $_ -notmatch "DEMO_API_KEY=" -and $_ -notmatch "DEMO_HMAC_SECRET=" }
    
    # Add new entries
    $envContent += "DEMO_API_KEY=$API_KEY"
    $envContent += "DEMO_HMAC_SECRET=$HMAC_SECRET"
    
    $envContent | Set-Content $ENV_FILE
    
    Write-Host "✅ .env updated" -ForegroundColor Green
    
    # Restart container
    Write-Host "`n📝 Restarting demo-website..." -ForegroundColor Yellow
    docker-compose restart demo-website | Out-Null
    
    Write-Host "`n==========================================" -ForegroundColor Green
    Write-Host "✅ Setup Complete!" -ForegroundColor Green
    Write-Host "==========================================`n" -ForegroundColor Green
    Write-Host "📍 Demo: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "📍 Dashboard: http://localhost/client-login`n" -ForegroundColor Cyan
    Write-Host "🔑 Login: $DEMO_EMAIL / $DEMO_PASSWORD`n" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n💡 Make sure services are running: docker-compose ps" -ForegroundColor Yellow
    exit 1
}
