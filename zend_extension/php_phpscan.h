#ifndef PHP_PHPSCAN
#define PHP_PHPSCAN 1
#define PHP_PHPSCAN_VERSION "1.0"
#define PHP_PHPSCAN_EXTNAME "phpscan"

PHP_FUNCTION(phpscan_enabled);
PHP_FUNCTION(phpscan_ext_get_zval_id);
PHP_FUNCTION(phpscan_ext_ignore_op);
PHP_FUNCTION(phpscan_ext_ignore_op_off);

extern zend_module_entry phpscan_module_entry;
#define phpext_phpscan_ptr &phpscan_module_entry

#endif
