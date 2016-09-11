from distutils.core import setup

pkg = 'Extensions.HetWeer'
setup (name = 'enigma2-plugin-extensions-hetweer',
	version = '2.3',
	description = '=--Weer App--=\nMade by Caught @http://forums.openpli.org',
	packages = [pkg],
	package_dir = {pkg: 'plugin'}
)
