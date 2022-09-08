#!/usr/bin/sh

set -e

PKGNAME="mdtopdf"
PKGDESC="Convert markdown file to pdf file using chromium."
PKGVER=$(python -c "print(__import__('${PKGNAME}').__version__)")

PKGDIR="pkg"

mkdir --verbose "${PKGDIR}"
if [ -d "${PKGDIR}" ]; then
    rm --verbose --recursive "${PKGDIR}"
fi
mkdir --verbose "${PKGDIR}"

mkdir --parents --verbose "${PKGDIR}/usr/bin"
cp --verbose mdtopdf.py "${PKGDIR}/usr/bin/${PKGNAME}"
chmod --verbose +x "${PKGDIR}/usr/bin/${PKGNAME}"

mkdir --parents --verbose "${PKGDIR}/DEBIAN"
cat << EOF > "${PKGDIR}/DEBIAN/control"
Package: ${PKGNAME}
Name: MdToPdf
Description: ${PKGDESC}
Maintainer: Floris Bartra <floris.bartra@gmail.com>
Version: ${PKGVER}
Architecture: all
Depends: python3, python3-markdown, python3-pygments, chromium-browser
EOF

dpkg-deb --verbose --build "${PKGDIR}" "${PKGNAME}-${PKGVER}.deb"

rm --verbose --recursive "${PKGDIR}"
