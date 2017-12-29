#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include "php.h"
#include "php_phpscan.h"

#define OP_PHP_CALLBACK_FUNCTION "phpscan_ext_opcode_handler"

long zval_to_id(zval* val)
{
    long id = -1;
    if (Z_TYPE_P(val) == IS_REFERENCE)
    {
        id = val->value.zv;
    }

    return id;
}

int ignore_op = 0;
int in_callback = 0;
static void trigger_op_php_callback(zend_uchar opcode, 
                                    zval* op1, zend_uchar op1type, 
                                    zval* op2, zend_uchar op2type,
                                    zval* result, zend_uchar resulttype,
                                    int use_result)
{
    if (!in_callback && !ignore_op)
    {
        zval* params = NULL;
        uint param_count = 10;

        params = safe_emalloc(sizeof(zval), param_count, 0);

        zval function_name;
        ZVAL_STRING(&function_name, OP_PHP_CALLBACK_FUNCTION);

        zval opcode_zval;
        ZVAL_LONG(&opcode_zval, opcode);

        zval op1type_zval;
        ZVAL_LONG(&op1type_zval, op1type);

        zval op1id_zval;
        ZVAL_LONG(&op1id_zval, zval_to_id(op1));
        
        zval op2type_zval;
        ZVAL_LONG(&op2type_zval, op2type);

        zval op2id_zval;
        ZVAL_LONG(&op2id_zval, zval_to_id(op2));

        zval resulttype_zval;
        ZVAL_LONG(&resulttype_zval, resulttype);

        params[0] = opcode_zval;
        params[1] = *op1;
        params[2] = op1id_zval;
        params[3] = op1type_zval;
        params[4] = *op2;
        params[5] = op2id_zval;
        params[6] = op2type_zval;
            
        // TODO: looks like result can be unitialized even though type != IS_UNUSED... use NULL for now
        zval resultid_zval;
        if (use_result && (result->u1.v.type != IS_UNDEF) && (&result->value != 0))
        {
            params[7] = *result;
            ZVAL_LONG(&resultid_zval, zval_to_id(result));
        }
        else
        {
            ZVAL_NULL(&params[7]);
            ZVAL_LONG(&resultid_zval, -1);
        }


        params[8] = resultid_zval;
        params[9] = resulttype_zval;

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
        // printf("Warning: ignoring opcode %d while already in callback to prevent infinite recursion.\n", opcode);
    }
}

PHP_FUNCTION(phpscan_enabled)
{
  RETURN_BOOL(1);
}

PHP_FUNCTION(phpscan_ext_ignore_op)
{
    ignore_op = 1;
}

PHP_FUNCTION(phpscan_ext_ignore_op_off)
{
    ignore_op = 0;
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

struct OplineLag {
    zend_op *opline;
    zend_uchar opcode;
    zval* op1;
    zend_uchar op1_type;
    zval* op2;
    zend_uchar op2_type;
    zval* result;
    zend_uchar result_type;
    int pending;
};

void force_ref(zval *val) {
    if (!Z_ISREF_P(val) && 
        (Z_TYPE_P(val) != IS_INDIRECT) && 
        (Z_TYPE_P(val) != IS_CONSTANT) && 
        (Z_TYPE_P(val) != IS_CONSTANT_AST))
    {
        if (Z_TYPE_P(val) == IS_UNDEF) {
			ZVAL_NEW_EMPTY_REF(val);
			Z_SET_REFCOUNT_P(val, 2);
			ZVAL_NULL(Z_REFVAL_P(val));
        }
        else {
            ZVAL_MAKE_REF(val);
        }
    }
}

static int common_override_handler(zend_execute_data *execute_data)
{
    const zend_op *opline = execute_data->opline;
    static struct OplineLag lag = {0, 0, 0, 0, 0, 0, 0, 0, 0};

    int is_var;

    if (lag.pending != 0)
    {
        lag.pending = 0;

        trigger_op_php_callback(lag.opcode,
                                lag.op1, lag.op1_type,
                                lag.op2, lag.op2_type,
                                lag.result, lag.result_type,
                                1
                                );
    }


    if (opline->opcode == ZEND_ASSIGN)
    {
        if (Z_TYPE_P(EX_VAR(opline->op1.var)) == IS_UNDEF)
        {
            force_ref(EX_VAR(opline->op1.var));
        }
    }

    zval* op1 = get_zval(execute_data, opline->op1_type, &opline->op1, &is_var);
    zval* op2 = get_zval(execute_data, opline->op2_type, &opline->op2, &is_var);
    zval* result = get_zval(execute_data, opline->result_type, &opline->result, &is_var);

    trigger_op_php_callback(opline->opcode,
                            op1, opline->op1_type,
                            op2, opline->op2_type,
                            result, opline->result_type,
                            0
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
    register_handler(ZEND_IS_NOT_EQUAL);
    register_handler(ZEND_IS_IDENTICAL);
    register_handler(ZEND_CASE);

    register_handler(ZEND_ISSET_ISEMPTY_DIM_OBJ);
    register_handler(ZEND_FETCH_DIM_R);
    register_handler(ZEND_FETCH_DIM_FUNC_ARG);

    register_handler(ZEND_IS_SMALLER);
    register_handler(ZEND_IS_SMALLER_OR_EQUAL);

    register_handler(ZEND_ASSIGN);

    register_handler(ZEND_ADD);
    register_handler(ZEND_CONCAT);

    return SUCCESS;
}


ZEND_BEGIN_ARG_INFO_EX(arginfo_phpscan_ext_get_zval_id, 0, 0, 3)
    ZEND_ARG_INFO(1, var)
ZEND_END_ARG_INFO();


zend_function_entry phpscan_functions[] = {
    PHP_FE(phpscan_enabled, NULL)
    PHP_FE(phpscan_ext_get_zval_id, arginfo_phpscan_ext_get_zval_id)
    PHP_FE(phpscan_ext_ignore_op, NULL)
    PHP_FE(phpscan_ext_ignore_op_off, NULL)
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


