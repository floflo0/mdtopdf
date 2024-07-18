# Maintainer: Floris Bartra <floris.bartra@gmail.com>
pkgname="mdtopdf"
pkgver=1.0.1
pkgrel=1
pkgdesc="Convert markdown file to pdf."
arch=("x86_64")
license=("MIT")
depends=("python" "python-markdown" "python-pygments" "chromium")
provides=("${pkgname}")
replaces=("${pkgname}")
source=("${pkgname}.py" "${pkgname}.fish")
noextract=()
md5sums=("SKIP" "SKIP")

pkgver () {
    cd "${srcdir}"
    ./mdtopdf.py --version | cut -d " " -f 2
}

package () {
    cd "${srcdir}"

    install -Dm755 "${pkgname}.py" "${pkgdir}/usr/bin/${pkgname}"
    install -Dm644 "${pkgname}.fish" "${pkgdir}/usr/share/fish/completions/${pkgname}.fish"
}
