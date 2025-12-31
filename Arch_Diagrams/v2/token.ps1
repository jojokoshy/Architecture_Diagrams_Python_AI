<#
Decode JWT Token Locally (PowerShell)

Usage:
- Run with token as argument: .\token.ps1 <token>
- Or copy token to clipboard and run: .\token.ps1

This script decodes the JWT header and payload locally (no external calls)
and prints key claims including human-readable iat/exp timestamps.
#>

param(
    [string]$Token
)

function Add-Padding {
    param([string]$s)
    $s = $s -replace '-','+' -replace '_','/'
    switch ($s.Length % 4) {
        0 { }
        2 { $s += '==' }
        3 { $s += '=' }
        1 { $s += '===' }
    }
    return $s
}

function Decode-Base64Url([string]$part) {
    $padded = Add-Padding $part
    try {
        $bytes = [System.Convert]::FromBase64String($padded)
        return [System.Text.Encoding]::UTF8.GetString($bytes)
    } catch {
        throw "Failed to decode base64 url part: $_"
    }
}

if (-not $Token) {
    try {
        $clip = Get-Clipboard -Raw -ErrorAction Stop
        if ($clip -and $clip.Contains('.')) { $Token = $clip.Trim() }
    } catch {
        # clipboard not available or empty
    }
}

if (-not $Token) {
    Write-Host "Usage: .\token.ps1 <token>    or copy token to clipboard and run .\token.ps1" -ForegroundColor Yellow
    exit 1
}

$parts = $Token.Split('.')
if ($parts.Count -lt 2) { Write-Error "Invalid JWT token format."; exit 1 }

$headerJson = Decode-Base64Url $parts[0]
$payloadJson = Decode-Base64Url $parts[1]

try { $header = $headerJson | ConvertFrom-Json } catch { $header = $headerJson }
try { $payload = $payloadJson | ConvertFrom-Json } catch { $payload = $payloadJson }

Write-Host "\n=== JWT Header ===" -ForegroundColor Cyan
if ($header -is [string]) { Write-Host $header } else { $header | ConvertTo-Json -Depth 10 }

Write-Host "\n=== JWT Claims (Payload) ===" -ForegroundColor Cyan
if ($payload -is [string]) { Write-Host $payload } else { $payload | ConvertTo-Json -Depth 10 }

Write-Host "\n--- Key Properties ---" -ForegroundColor Green
$keys = @('aud','iss','iat','exp','nbf','sub','appid','appidacr','azp','tid','roles','scp','upn','preferred_username')
foreach ($k in $keys) {
    if ($payload -isnot [string] -and $payload.PSObject.Properties.Name -contains $k) {
        Write-Host ("{0}: {1}" -f $k, ($payload.$k))
    }
}

if ($payload -isnot [string]) {
    if ($payload.iat) {
        try { $iat = [DateTimeOffset]::FromUnixTimeSeconds([int64]$payload.iat).ToLocalTime(); Write-Host ("Issued At (iat): {0}" -f $iat) } catch {}
    }
    if ($payload.exp) {
        try {
            $exp = [DateTimeOffset]::FromUnixTimeSeconds([int64]$payload.exp).ToLocalTime();
            $minutesLeft = [math]::Round(($exp - (Get-Date)).TotalMinutes,2)
            Write-Host ("Expires At (exp): {0} (in {1} minutes)" -f $exp, $minutesLeft)
        } catch {}
    }
}

Write-Host "\nDone."
### Decode JWT Token Locally (PowerShell)
# Copy the access_token value and run this PowerShell command in the terminal:
#
# $token = "PASTE_YOUR_TOKEN_HERE"
# $parts = $token.Split('.')
# $payload = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($parts[1].PadRight(($parts[1].Length + (4 - $parts[1].Length % 4) % 4), '=')))
# $payload | ConvertFrom-Json | ConvertTo-Json -Depth 10
#
# This will decode and display all JWT claims locally without calling any external service.
#
# Common JWT claims in Azure Entra tokens:
# - aud (Audience): The intended recipient of the token
# - iss (Issuer): Token issuer (e.g., https://sts.windows.net/{tenant-id}/)
# - iat (Issued At): Unix timestamp when token was issued
# - exp (Expiration): Unix timestamp when token expires
# - nbf (Not Before): Unix timestamp - token is not valid before this time
# - sub (Subject): Subject identifier
# - appid: Application ID that requested the token
# - tid (Tenant ID): Azure tenant identifier
# - roles/scp: Permissions and scopes granted
# - ver: Token version (1.0 or 2.0)

###