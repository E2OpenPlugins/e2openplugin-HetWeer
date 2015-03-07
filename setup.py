commit af0119f15f41c201e583fd53f73a90afb3fd502c
Author: Erik Slagter <erik@openpli.org>
Date:   Fri Mar 6 15:03:03 2015 +0100

    Added stub setup.py, please change accordingly.

diff --git a/setup.py b/setup.py
new file mode 100644
index 0000000..422ba4a
--- /dev/null
+++ b/setup.py
@@ -0,0 +1,9 @@
+from distutils.core import setup
+
+pkg = 'Exensions.HetWeer'
+setup (name = 'enigma2-plugin-extensions-hetweer',
+   version = '1.0',
+   description = '=--Weer App--=\nMade by DEG 2012~2015!'
+   packages = [pkg],
+   package_dir = {pkg: 'plugin'}
+)
