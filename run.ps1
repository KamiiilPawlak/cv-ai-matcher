function up { docker-compose up --build }
function down { docker-compose down }
function test { docker-compose exec api pytest }
function lint { python -m pre_commit run --all-files }
