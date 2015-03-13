from distutils.core import setup

pkg = 'Extensions.HetWeer'
setup (name = 'enigma2-plugin-extensions-hetweer',
	version = '1.0',
	description = '=--Weer App--=\nMade by DEG 2012~2015!',
	packages = [pkg],
	package_dir = {pkg: 'plugin'}
)
