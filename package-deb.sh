#!/usr/bin/sh

set -e

PKGNAME="mdtopdf"
PKGVER=$(python -c "print(__import__('${PKGNAME}').__version__)")
PKGREL="1"
PKGDIR="pkg"
ARCH="amd64"

if [ -e "${PKGDIR}" ]; then
    rm --verbose --recursive "${PKGDIR}"
fi
mkdir --verbose "${PKGDIR}"

install --verbose -Dm 755 "${PKGNAME}.py" "${PKGDIR}/usr/bin/${PKGNAME}"

mkdir --parents --verbose "${PKGDIR}/DEBIAN"
cat << EOF > "${PKGDIR}/DEBIAN/control"
Package: ${PKGNAME}
Name: MdToPdf
Description: Convert markdown file to pdf file using chromium.
Maintainer: Floris Bartra <floris.bartra@gmail.com>
Version: ${PKGVER}
Architecture: ${ARCH}
Depends: python3, python3-markdown, python3-pygments, chromium-browser
Homepage: https://github.com/floflo0/mdtopdf
Provides: ${PKGNAME}
EOF

dpkg-deb --verbose --build "${PKGDIR}" "${PKGNAME}_${PKGVER}-${PKGREL}_${ARCH}.deb"

rm --verbose --recursive "${PKGDIR}"
