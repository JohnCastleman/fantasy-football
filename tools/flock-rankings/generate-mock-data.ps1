# Generate mock data for all Flock Fantasy ranking modes
# Usage: .\generate-mock-data.ps1 [num_players]

param(
    [int]$NumPlayers = 10
)

Write-Host "WARNING: This script will RESET and OVERWRITE data in the following tabs:"
Write-Host "  - 'Flock ROS raw data' (will be reset once)"
Write-Host "  - 'Flock weekly raw data' (will be reset once, then populated with QB, RB, WR, TE data)"
Write-Host ""
Write-Host "Number of players per mode: $NumPlayers"
Write-Host ""
$confirmation = Read-Host "Are you sure you want to continue? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "Aborted."
    exit 0
}

Write-Host ""
Write-Host "Generating mock data for Flock Fantasy rankings..."
Write-Host ""

# Reset ROS tab before generating
Write-Host "Resetting ROS tab..."
python tools/flock-rankings/flock-rankings-tsv-to-google-sheets.py `
  --reset `
  --type ROS

Write-Host ""

# ROS (Overall)
Write-Host "1/5: Generating ROS (Overall) mock data..."
python tools/flock-rankings/flock-rankings-tsv-to-google-sheets.py `
  --type ROS `
  --mock `
  --mock-players $NumPlayers

Write-Host ""

# Reset weekly tab once before all weekly positions
Write-Host "Resetting weekly tab..."
python tools/flock-rankings/flock-rankings-tsv-to-google-sheets.py `
  --reset `
  --type WEEKLY

Write-Host ""

# WEEKLY QB
Write-Host "2/5: Generating WEEKLY QB mock data..."
python tools/flock-rankings/flock-rankings-tsv-to-google-sheets.py `
  --type WEEKLY `
  --position QB `
  --mock `
  --mock-players $NumPlayers

Write-Host ""

# WEEKLY RB
Write-Host "3/5: Generating WEEKLY RB mock data..."
python tools/flock-rankings/flock-rankings-tsv-to-google-sheets.py `
  --type WEEKLY `
  --position RB `
  --mock `
  --mock-players $NumPlayers

Write-Host ""

# WEEKLY WR
Write-Host "4/5: Generating WEEKLY WR mock data..."
python tools/flock-rankings/flock-rankings-tsv-to-google-sheets.py `
  --type WEEKLY `
  --position WR `
  --mock `
  --mock-players $NumPlayers

Write-Host ""

# WEEKLY TE
Write-Host "5/5: Generating WEEKLY TE mock data..."
python tools/flock-rankings/flock-rankings-tsv-to-google-sheets.py `
  --type WEEKLY `
  --position TE `
  --mock `
  --mock-players $NumPlayers

Write-Host ""
Write-Host "Done! All mock data has been written to the Google Sheet."
Write-Host "Check the 'Flock ROS raw data' and 'Flock weekly raw data' tabs."
