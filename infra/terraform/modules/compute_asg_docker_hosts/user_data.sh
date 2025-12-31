#!/bin/bash
set -euxo pipefail

# Logs
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

# Update + install docker
dnf -y update
dnf -y install docker

systemctl enable docker
systemctl start docker

# Run a simple HTTP responder on port 80 (low-cost demo)
# This guarantees ALB health checks pass.
docker rm -f campusuce-hello || true
docker run -d --name campusuce-hello --restart unless-stopped -p 80:80 nginx:alpine

# Put a friendly page
docker exec campusuce-hello sh -c 'cat > /usr/share/nginx/html/index.html <<EOF
<!doctype html>
<html>
<head><meta charset="utf-8"><title>CampusUCETrade</title></head>
<body style="font-family: Arial, sans-serif;">
  <h1>CampusUCETrade - QA</h1>
  <p>ALB -> ASG -> EC2 is working ✅</p>
</body>
</html>
EOF'
