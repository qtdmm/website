#!/usr/bin/env bash
# Upload public/ to the web host with lftp.
#
# Credentials are never stored here. Either:
#   * put a "machine <host> login <user> password <pw>" line in ~/.netrc
#     (chmod 600) and set FTP_HOST, or
#   * export FTP_HOST, FTP_USER and FTP_PASS.
# FTP_DIR is the remote directory (default: /), FTP_PROTO ftp|ftps|sftp
# (default: ftps — plain ftp only if the host really has nothing better).
#
#   ./deploy.sh           # build, then mirror
#   ./deploy.sh --dry-run # show what would change
#   ./deploy.sh --no-build
set -euo pipefail
cd "$(dirname "$0")"

: "${FTP_HOST:?set FTP_HOST}"
FTP_DIR=${FTP_DIR:-/}
FTP_PROTO=${FTP_PROTO:-ftps}
dry=""; build=1
for a in "$@"; do
  case $a in
    --dry-run) dry="--dry-run" ;;
    --no-build) build=0 ;;
    *) echo "unknown option $a" >&2; exit 2 ;;
  esac
done

command -v lftp >/dev/null || { echo "lftp not installed" >&2; exit 1; }
[ $build = 1 ] && ./build.sh

login=""
if [ -n "${FTP_USER:-}" ]; then
  login="-u $FTP_USER,${FTP_PASS:-}"
fi

lftp $login "$FTP_PROTO://$FTP_HOST" <<LFTP
set ftp:ssl-force true
set ftp:ssl-protect-data true
set ssl:verify-certificate true
mirror --reverse --delete --verbose --parallel=4 $dry \
  --exclude-glob .DS_Store --exclude-glob '*.swp' \
  public/ $FTP_DIR
bye
LFTP
echo "deployed to $FTP_HOST:$FTP_DIR"
