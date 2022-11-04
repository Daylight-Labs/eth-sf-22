#!/usr/bin/env bash

set -eou pipefail

SSL_DIR=/etc/ssl/web
mkdir -p $SSL_DIR

WEB_KEY=$SSL_DIR/web.key
WEB_CERT=$SSL_DIR/web.crt
WEB_CSR=$SSL_DIR/web.csr

# Can only be read by root user
chmod 0600 $SSL_DIR

# Generate web ssl key and Certificate-Signing-Request (CSR)
openssl req \
    -new \
    -nodes \
    -newkey rsa:2048 \
    -subj "/C=US/O=bn/CN=api.background.network" \
    -keyout $WEB_KEY \
    -out $WEB_CSR

# Self-sign CSR and generate web ssl cert
openssl x509 \
    -req \
    -days 3650 \
    -in $WEB_CSR \
    -signkey $WEB_KEY \
    -out $WEB_CERT

# Start nginx
nginx -g "daemon off;"