#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include "php.h"
#include "php_phpscan.h"

#define OP_PHP_CALLBACK_FUNCTION "phpscan_ext_opcode_handler"

long zval_to_id(zval* val)
{
  long id = (long)&val->value.zv->value;
  return id;
}

int in_callback = 0;
static void trigger_op_php_callback(zend_uchar opcode, 
                                    zval* op1, zend_uchar op1type, 
                                    zval* op2, zend_uchar op2type,
                                    zval* result, zend_uchar resulttype)
{
    if (!in_callback)
    {
        zval* params = NULL;
        uint param_count = 7;

        params = safe_emalloc(sizeof(zval), param_count, 0);

        zval function_name;
        ZVAL_STRING(&function_name, OP_PHP_CALLBACK_FUNCTION);

        zval opcode_zval;
        ZVAL_LONG(&opcode_zval, opcode);

        zval op1type_zval;
        ZVAL_LONG(&op1type_zval, op1type);

        zval op2type_zval;
        ZVAL_LONG(&op2type_zval, op2type);

        zval resulttype_zval;
        ZVAL_LONG(&resulttype_zval, resulttype);


        params[0] = opcode_zval;
        params[1] = *op1;
        params[2] = op1type_zval;
        params[3] = *op2;
        params[4] = op2type_zval;
        if (result)
            params[5] = *result;
        else
            ZVAL_NULL(&params[5]);
        params[6] = resulttype_zval;

        zval return_value;

        in_callback = 1;
        if (call_user_function(
                EG(function_table), NULL /* no object */, &function_name,
                &return_value, param_count,     params TSRMLS_CC
            ) == SUCCESS
        )
        {
            /* do something with retval_ptr here if you like */
        }
        in_callback = 0;

        efree(params);
        zval_ptr_dtor(&return_value);
    }
    else
    {
        printf("Warning: ignoring opcode %d while already in callback to prevent infinite recursion.\n", opcode);
    }
}

PHP_FUNCTION(phpscan_enabled)
{
  RETURN_BOOL(1);
}

PHP_FUNCTION(phpscan_ext_get_zval_id)
{
  zval* var;

  if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "z", &var) == FAILURE) {
      RETURN_NULL();
  }

  RETURN_LONG(zval_to_id(var));
}

zval *get_zval(zend_execute_data *zdata, int node_type, const znode_op *node, int *is_var)
{
    zend_free_op should_free;
    zval* r = zend_get_zval_ptr(node_type, node, zdata, &should_free, BP_VAR_IS);

    return r;
}

static int common_override_handler(zend_execute_data *execute_data)
{
    const zend_op *opline = execute_data->opline;
    zend_free_op should_free;

    int is_var;
    zval* op1 = get_zval(execute_data, opline->op1_type, &opline->op1, &is_var);
    zval* op2 = get_zval(execute_data, opline->op2_type, &opline->op2, &is_var);
    zval* result = get_zval(execute_data, opline->result_type, &opline->result, &is_var);

    trigger_op_php_callback(opline->opcode,
                            op1, opline->op1_type,
                            op2, opline->op2_type,
                            result, opline->result_type
                            );

    return ZEND_USER_OPCODE_DISPATCH;
}

void register_handler(zend_uchar opcode)
{
    zend_set_user_opcode_handler(opcode, common_override_handler);
}

PHP_MINIT_FUNCTION(phpscan)
{
    register_handler(ZEND_IS_EQUAL);
    register_handler(ZEND_IS_IDENTICAL);

    register_handler(ZEND_ISSET_ISEMPTY_DIM_OBJ);
    register_handler(ZEND_FETCH_DIM_R);

    register_handler(ZEND_IS_SMALLER);
    register_handler(ZEND_IS_SMALLER_OR_EQUAL);

    register_handler(ZEND_ASSIGN);

    return SUCCESS;
}


zend_function_entry phpscan_functions[] = {
    PHP_FE(phpscan_enabled, NULL)
    PHP_FE(phpscan_ext_get_zval_id, NULL)
    {NULL, NULL, NULL}
};
 

zend_module_entry phpscan_module_entry = {
    STANDARD_MODULE_HEADER,
    PHP_PHPSCAN_EXTNAME,
    phpscan_functions,
    PHP_MINIT(phpscan),
    NULL,
    NULL,
    NULL,
    NULL,
    PHP_PHPSCAN_VERSION,
    STANDARD_MODULE_PROPERTIES
};

#ifdef COMPILE_DL_PHPSCAN
ZEND_GET_MODULE(phpscan)
#endif


