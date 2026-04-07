#!/bin/sh
set -e
export PUBLIC_DOMAIN="${PUBLIC_DOMAIN:-localhost}"
export SSL_CERTIFICATE_PATH="${SSL_CERTIFICATE_PATH:-/etc/nginx/certs/fullchain.pem}"
export SSL_CERTIFICATE_KEY_PATH="${SSL_CERTIFICATE_KEY_PATH:-/etc/nginx/certs/privkey.pem}"
if [ "${ENABLE_NGINX_SSL:-0}" = "1" ]; then
  envsubst '${PUBLIC_DOMAIN} ${SSL_CERTIFICATE_PATH} ${SSL_CERTIFICATE_KEY_PATH}' \
    < /tmp/nginx-ssl.conf.template > /etc/nginx/conf.d/default.conf
else
  envsubst '${PUBLIC_DOMAIN}' < /tmp/nginx.conf.template > /etc/nginx/conf.d/default.conf
fi
exec "$@"
