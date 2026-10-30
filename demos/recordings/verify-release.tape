# Verify the signed v0.3.0 release: Sigstore signature, checksums, SLSA provenance. Needs cosign and gh (GH_TOKEN).
Output demos/recordings/out/verify-release.mp4
Output demos/recordings/out/verify-release.gif
Source demos/recordings/settings.tape
Set FontSize 24

Hide
Type "cd $(mktemp -d) && export PS1='$ ' VERSION=v0.3.0 && clear" Enter
Show
Type "gh release download $VERSION --repo XData-si/xdata-agenthub && ls" Enter
Sleep 4s
Type "cosign verify-blob --bundle SHA256SUMS.sigstore.json --certificate-oidc-issuer https://token.actions.githubusercontent.com --certificate-identity https://github.com/XData-si/xdata-agenthub/.github/workflows/release.yml@refs/tags/$VERSION SHA256SUMS" Enter
Sleep 5s
Type "sha256sum -c SHA256SUMS" Enter
Sleep 2s
Type "gh attestation verify xdata-agenthub-$VERSION.tar.gz --repo XData-si/xdata-agenthub" Enter
Sleep 7s
