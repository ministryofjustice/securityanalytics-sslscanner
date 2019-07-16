[![CircleCI](https://circleci.com/gh/ministryofjustice/securityanalytics-sslscanner.svg?style=svg)](https://circleci.com/gh/ministryofjustice/securityanalytics-sslscanner)

# SSL Scan

This Lambda based secondary (port) level scan, uses the openssl cli to determine features pertaining to SSL security e.g. certificate chain & expiry info.

## OpenSSL stuff

Windows: Install the MSI, not the 'Light' version, and ensure that the binary directory is in your path (`openssl` should work within your shell)

