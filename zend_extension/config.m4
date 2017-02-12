PHP_ARG_ENABLE(phpscan, whether to enable PHPScan support,
[ --enable-phpscan   Enable PHPScan support])
if test "$PHP_PHPSCAN" = "yes"; then
  AC_DEFINE(HAVE_PHPSCAN, 1, [Whether you have PHPScan])
  PHP_NEW_EXTENSION(phpscan, phpscan.c, $ext_shared)
fi
