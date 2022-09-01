pkgname="mdtopdf"
pkgver="1.0.0"
pkgrel="1"
pkgdesc="Convert markdown file to pdf file using chromium."
arch=("any")
license=("unknow")
depends=("python" "python-markdown" "chromium")
provides=("${pkgname}")
replaces=("${pkgname}")
source=("${pkgname}.py")
noextract=()
md5sums=("SKIP")

pkgver () {
    python -c "print(__import__('${pkgname}').__version__)"
}

package () {
    cd "${srcdir}"

    install -Dm755 "${pkgname}.py" "${pkgdir}/usr/bin/${pkgname}"
}
