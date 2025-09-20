param(
  [string]$Repo = "Preetham0420/smartops-demo"
)

$ErrorActionPreference = "Stop"

# Output file
$outDir = "C:\Users\preet\Projects\nani\smartops\data\raw"
$outLog = Join-Path $outDir "gha_latest.log"
New-Item -ItemType Directory -Force $outDir | Out-Null

# 1) Get newest run id
$json = gh run list --repo $Repo --limit 1 --json databaseId
$arr  = $json | ConvertFrom-Json
if (-not $arr -or $arr.Count -lt 1) { throw "No runs found for $Repo" }
$runId = $arr[0].databaseId
Write-Host "Using run: $runId"

# 2) Wait until jobs exist AND status is completed
do {
  Start-Sleep -Seconds 5
  $runInfo = gh api "repos/$Repo/actions/runs/$runId" | ConvertFrom-Json
  $jobsObj = gh api "repos/$Repo/actions/runs/$runId/jobs?per_page=100" | ConvertFrom-Json
} while (-not $jobsObj.jobs -or $runInfo.status -ne "completed")

# 3) Combine each job's plain-text log into a single file
Remove-Item $outLog -ErrorAction SilentlyContinue
foreach ($j in $jobsObj.jobs) {
  "===== JOB $($j.id) • $($j.name) =====" | Add-Content -Encoding UTF8 $outLog
  gh api "repos/$Repo/actions/jobs/$($j.id)/logs" | Add-Content -Encoding UTF8 $outLog
}

Write-Host "Wrote: $outLog"
