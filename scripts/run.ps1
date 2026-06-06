param (
    [string]$Action
)


function up { docker-compose up --build }
function down { docker-compose down }
function test { docker-compose exec api pytest }

function lint { python -m pre_commit run --all-files }


function Clear-Project {
    Write-Host "We start clean the project..." -ForegroundColor Cyan
    Write-Host "-> We search and delete __pycache__ folders in subfolders" -ForegroundColor Gray
    Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "-> Delete *.egg-info" -ForegroundColor Gray
    Get-ChildItem -Path . -Filter "*.egg-info" -Recurse -Directory | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "-> Delete .\.pytest_cache... mypy... ruff.. " -ForegroundColor Gray
    Remove-Item -Path .\.pytest_cache, .\.mypy_cache, .\.ruff_cache, .\.tox -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "Done :D" -ForegroundColor Green
}


if ($Action -eq "cleanup") {
    Clear-Project
}



