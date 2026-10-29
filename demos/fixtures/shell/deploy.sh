#!/bin/bash
# Deploy the current build to the web server.
TARGET=/var/www/$APP_NAME
cd $BUILD_OUT
tar czf /tmp/release.tgz .
scp /tmp/release.tgz deploy@$HOST:/tmp/
ssh deploy@$HOST "rm -rf $TARGET/* && tar xzf /tmp/release.tgz -C $TARGET"
for f in $(find . -name "*.conf"); do
  cp $f /etc/app/
done
curl -k https://$HOST/health
echo "deployed"
