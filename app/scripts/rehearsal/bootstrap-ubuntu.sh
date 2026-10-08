#!/bin/sh
# Disposable Ubuntu rehearsal host; run as root on an empty VM.
set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl git python3
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
cat > /etc/apt/sources.list.d/docker.sources <<SOURCES
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${UBUNTU_CODENAME:-$VERSION_CODENAME}
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
SOURCES
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
# SSH account is created by the GCE guest agent. The following login takes effect
# after bootstrap, without granting access to existing project service accounts.
while ! id learner >/dev/null 2>&1; do sleep 2; done
usermod -aG docker learner
docker run --rm hello-world
mkdir -p /var/lib/marketplace-rehearsal
{
  date -u
  uname -m
  cat /etc/os-release
  git --version
  python3 --version
  docker version --format '{{.Server.Version}}'
  docker compose version
} > /var/lib/marketplace-rehearsal/host.txt
touch /var/lib/marketplace-rehearsal/bootstrap-ready
