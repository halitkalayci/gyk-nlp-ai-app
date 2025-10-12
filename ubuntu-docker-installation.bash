#!/usr/bin/env bash
# install-docker-ubuntu2204.sh
# Ubuntu 22.04 (Jammy) için resmi Docker deposundan kurulum
# Tüm adımlar root kullanıcıyla çalışacak şekilde yazılmıştır.

set -Eeuo pipefail

log() { echo -e "\033[1;32m[+] $*\033[0m"; }
warn() { echo -e "\033[1;33m[!] $*\033[0m"; }
err() { echo -e "\033[1;31m[✗] $*\033[0m" >&2; }

# 0) Root kontrolü
if [[ "${EUID}" -ne 0 ]]; then
  err "Lütfen scripti root olarak çalıştırın (sudo -i veya sudo bash ...)."
  exit 1
fi

# 1) Dağıtım kontrolü (Ubuntu 22.04.x)
source /etc/os-release
if [[ "${ID:-}" != "ubuntu" ]]; then
  err "Bu script yalnızca Ubuntu için hazırlandı. Bulunan: ${ID:-unknown}"
  exit 1
fi
if [[ ! "${VERSION_ID:-}" =~ ^22\.04 ]]; then
  warn "Tespit edilen sürüm: ${VERSION_ID:-unknown}. Script 22.04 için yazıldı (22.04.5 dahil). Devam ediliyor..."
fi
ARCH="$(dpkg --print-architecture)"             # amd64 / arm64 / ...
CODENAME="${VERSION_CODENAME:-jammy}"

log "Ubuntu ${VERSION_ID:-} (${CODENAME}), mimari: ${ARCH}"

# 2) Eski paketler varsa kaldır
log "Eski Docker bileşenlerini (varsa) kaldırıyor..."
apt-get remove -y docker docker-engine docker.io containerd runc || true
apt-get purge  -y docker docker-engine docker.io containerd runc || true
rm -rf /var/lib/docker /var/lib/containerd || true

# 3) Gerekli bağımlılıklar
log "Bağımlılıkları kuruyor (ca-certificates, curl, gnupg, apt-transport-https)..."
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ca-certificates curl gnupg apt-transport-https lsb-release

# 4) Docker GPG anahtarı ve depo ekleme (keyring ile)
log "Docker GPG anahtarını ve APT deposunu ekliyor..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${CODENAME} stable" \
  > /etc/apt/sources.list.d/docker.list

# 5) Kurulum
log "Paket önbelleği güncelleniyor ve Docker kuruluyor..."
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 6) Hizmeti başlat ve enable et
log "Docker servislerini başlatıyor ve enable ediyor..."
systemctl daemon-reload
systemctl enable --now docker
systemctl enable --now containerd

# 7) Basit doğrulamalar
log "Sürüm bilgileri:"
docker --version || { err "docker komutu bulunamadı."; exit 1; }
docker compose version || warn "docker compose plugin sürümü alınamadı."

# 8) (İsteğe bağlı) Hızlı test: Hello World
# Yorum satırını kaldırarak çalıştırabilirsiniz:
# log "Hello-World konteyneri çekilip çalıştırılıyor (opsiyonel)..."
# docker run --rm hello-world || warn "Hello-World testi başarısız oldu."

log "Kurulum tamamlandı. Kullanım: 'docker ps', 'docker run hello-world', 'docker compose version'"
