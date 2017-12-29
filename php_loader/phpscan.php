<?php

require_once 'zend_opcodes.php';

register_shutdown_function('phpscan_handle_shutdown');

phpscan_ext_ignore_op();
$_rGET = array(); $_GET = &$_rGET;
$_rPOST = array(); $_POST = &$_rPOST;
$_rFILES = array(); $_FILES = &$_rFILES;
$_rCOOKIES = array(); $_COOKIES = &$_rCOOKIES;
$_rREQUEST = array(); $_REQUEST = &$_rREQUEST;

$__phpscan_variable_map = array();
$__phpscan_transform = array();
$__phpscan_init_complete = false;
$__phpscan_op_ignore = false;
$__phpscan_op = array();
$__phpscan_taint_hook = array();
$__phpscan_var_id_lookup = array();
phpscan_ext_ignore_op_off();

function phpscan_var_id(&$var) {
    return phpscan_ext_get_zval_id($var);
}

function phpscan_ext_opcode_handler($opcode, 
                  $op1, $op1_zval_id, $op1_type,
                  $op2, $op2_zval_id, $op2_type,
                  $result, $result_zval_id, $resulttype)
{
  global $__phpscan_init_complete;
  global $__phpscan_op_ignore;
  global $__phpscan_variable_map;

  if (!$__phpscan_op_ignore && $__phpscan_init_complete)
  {
    $op1_id = phpscan_lookup_zval_by_id($op1_zval_id);
    $op2_id = phpscan_lookup_zval_by_id($op2_zval_id);

    phpscan_ext_ignore_op();
    $__phpscan_op_ignore = true;

    if ($opcode === ZendOpcodes::ZEND_ASSIGN)
    {
      if (($op1_zval_id > 0) && phpscan_is_tracking($op2_zval_id) && ($op1_zval_id !== $op2_zval_id))
      {
        $__phpscan_variable_map[$op1_zval_id] = 'assign(' . $op2_id . ':' . __phpscan_replace_uniqid('', true) . ')';
        // TODO do we really need to reassign here?
        $op1_id = phpscan_lookup_zval_by_id($op1_zval_id);
        
        phpscan_register_transform($op1_id,
                                  'assign',
                                  array($op2_id),
                                  array(
                                    array('type' => 'symbolic', 'id' => $op2_id, 'value' => $op2)
                                  ));
      }
    }
    else if (($opcode === ZendOpcodes::ZEND_ADD) || ($opcode === ZendOpcodes::ZEND_CONCAT))
    {
      if (phpscan_is_tracking($op1_zval_id) || phpscan_is_tracking($op2_zval_id))
      {
        $result_zval_id = phpscan_ext_get_zval_id($result);

        $functions = array(1 => 'add', 8 => 'concat');

        $func_name = $functions[$opcode];

        $args = array();
        if (phpscan_is_tracking($op1_zval_id))
          $args[] = array('type' => 'symbolic', 'id' => $op1_id, 'value' => $op1);
        else
          $args[] = array('type' => 'raw_value', 'value' => $op1);

        if (phpscan_is_tracking($op2_zval_id))
          $args[] = array('type' => 'symbolic', 'id' => $op2_id, 'value' => $op2);
        else
          $args[] = array('type' => 'raw_value', 'value' => $op2);

        $symbolic_args = array();
        foreach ($args as $arg) {
          if ($arg['type'] === 'symbolic')
            $symbolic_args[] = $arg['id'];
        }

        $__phpscan_variable_map[$result_zval_id] = $func_name . '(' . implode(';', $symbolic_args) . ';' . __phpscan_replace_uniqid() . ')';
        print 'RESULT_ZVAL_ID = ' . $result_zval_id . "\n";
        $result_id = phpscan_lookup_zval_by_id($result_zval_id);


        phpscan_register_transform($result_id,
                                  $func_name,
                                  array($op1_id, $op2_id),
                                  $args);
      }

    }
    else
    {
      $result_zval_id = phpscan_ext_get_zval_id($result);

      $op = array(
        'opcode' => $opcode,

        'op1_value' => $op1,
        'op1_id' => $op1_id,
        'op1_type' => $op1_type,
        'op1_data_type' => __phpscan_replace_gettype($op1),

        'op2_value' => $op2,
        'op2_id' => $op2_id,
        'op2_type' => $op2_type,
        'op2_data_type' => __phpscan_replace_gettype($op2)
      );
      phpscan_log_op($op);

      if ($opcode == ZendOpcodes::ZEND_FETCH_DIM_R)
      {
        // if (!__phpscan_replace_array_key_exists($res_zval_id, $__phpscan_variable_map))
        if (phpscan_is_tracking($op1_zval_id))
        {
          if (!__phpscan_replace_array_key_exists($op2, $op1) || !__phpscan_replace_array_key_exists($result_zval_id, $__phpscan_variable_map))
            $__phpscan_variable_map[$result_zval_id] = 'fetch_dim_r(' . $op1_id . ':' . $op2 .  ')';

          $res_id = phpscan_lookup_zval_by_id($result_zval_id);

          phpscan_register_transform($res_id,
                                    'fetch_dim_r',
                                    array($op1_id),
                                    array(
                                      array('type' => 'symbolic', 'id' => $op1_id, 'value' => $op1),
                                      array('type' => 'raw_value', 'value' => $op2)
                                    ));

        }
      }
    }

    $__phpscan_op_ignore = false;
    phpscan_ext_ignore_op_off();
  }
}

function phpscan_log_op($op)
{
  global $__phpscan_op;
  $__phpscan_op[] = $op;
}

function phpscan_initialize($state)
{
  phpscan_ext_ignore_op();
  phpscan_replace_internals();
  phpscan_initialize_environment($state);
  phpscan_ext_ignore_op_off();
}

function phpscan_initialize_environment($state)
{
  global $__phpscan_init_complete;

  $state_decoded = json_decode($state);
  var_dump('SETTING STATE', $state_decoded);

  phpscan_initialize_variables($state_decoded);
  phpscan_initialize_register_zvals($state_decoded);

  $__phpscan_init_complete = true;
}

function phpscan_initialize_variables($state_decoded)
{
  foreach ($state_decoded as $var_name => $var_info)
  {
    $var = phpscan_initialize_variable($var_name, $var_info);
    phpscan_set_toplevel_variable($var_name, $var);
  }
}

function phpscan_initialize_register_zvals($state_decoded)
{
  foreach ($state_decoded as $var_name => $var_info)
  {
    global ${$var_name};
    phpscan_register_zval(${$var_name}, $var_info);
    phpscan_initialize_register_zvals_rec(${$var_name}, $var_info);
  }
}

function phpscan_initialize_register_zvals_rec(&$var, $var_info)
{
  if (($var_info->type == 'array') and (__phpscan_replace_array_key_exists('properties', $var_info)))
  {
    foreach ($var_info->properties as $prop_name => $prop_info)
    {
      phpscan_register_zval($var[$prop_name], $prop_info);
      phpscan_initialize_register_zvals_rec($var[$prop_name], $prop_info);
    }
  }
}

function phpscan_set_toplevel_variable($var_name, $var)
{
  global ${$var_name};
  ${$var_name} = $var;
}


function phpscan_register_zval(&$var, $var_info)
{
  global $__phpscan_variable_map;
  $var_zval_id = phpscan_var_id($var);
  $__phpscan_variable_map[$var_zval_id] = $var_info->id;
}

function phpscan_is_tracking($var_zval_id)
{
  global $__phpscan_variable_map;
  return __phpscan_replace_array_key_exists($var_zval_id, $__phpscan_variable_map);
}

function phpscan_lookup_zval($var)
{
  return phpscan_lookup_zval_by_id(phpscan_var_id($var));
}

function phpscan_lookup_zval_by_id($var_zval_id)
{
  global $__phpscan_variable_map;
  global $__phpscan_op_ignore;

  $__phpscan_op_ignore = true;
  $var_id = 'untracked (zval_id=' . $var_zval_id .')';
  if (phpscan_is_tracking($var_zval_id))
  {
    $var_id = $__phpscan_variable_map[$var_zval_id];
  }
  $__phpscan_op_ignore = false;

  return $var_id;
}

function phpscan_initialize_variable($var_name, $var_info)
{
  $var = null;

  switch ($var_info->type)
  {
    case 'array':
      $var = array();
      break;
    case 'string':
      $var = $var_info->value;
      break;
    case 'integer':
      $var = $var_info->value;
      break;
    case 'double':
      $var = $var_info->value;
      break;
    case 'unknown':
      // Type can be unknown if newly discovered and we did not get a typehint yet
      $var = $var_info->value;
      break;
    default:
  }

  $var = phpscan_separate_zval($var);

  if (($var_info->type == 'array') and (__phpscan_replace_array_key_exists('properties', $var_info)))
  {
    foreach ($var_info->properties as $prop_name => $prop_info)
    {
      $var[$prop_name] = phpscan_initialize_variable($prop_name, $prop_info);
    }
  }

  return $var;
}

function phpscan_separate_zval($var)
{
  $separated_var = $var;
  if (is_array($separated_var))
  {
    $separated_var['__aa__'] = rand();
    unset($separated_var['__aa__']);
  }
  else if (is_string($separated_var)) {
    $separated_var .= '';
  }
  else if (is_integer($separated_var) || is_double($separated_var)) {
    $separated_var *= 1;
  }
  else {
    throw new Exception('Unable to separate zval for unknown type ' . gettype($separated_var));
  }

  return $separated_var;
}

function phpscan_handle_shutdown()
{
  phpscan_ext_ignore_op();
  phpscan_report_opcodes();
  phpscan_report_transform();
  phpscan_ext_ignore_op_off();
}

function phpscan_flag($flag = 'default')
{
  print '__PHPSCAN_FLAG__' . $flag . '__/PHPSCAN_FLAG__';
}

function phpscan_report_opcodes()
{
  global $__phpscan_op;
  $json = __phpscan_replace_json_encode($__phpscan_op);
  
  print '__PHPSCAN_OPS__' . $json . '__/PHPSCAN_OPS__';

  global $__phpscan_variable_map;
  var_dump('MAP', $__phpscan_variable_map);

  global $__phpscan_var_id_lookup;
  var_dump('LOOKUP', $__phpscan_var_id_lookup);
}

function phpscan_report_transform()
{
  global $__phpscan_transform;
  $json = __phpscan_replace_json_encode($__phpscan_transform);
  print '__PHPSCAN_TRANSFORMS__' . $json . '__/PHPSCAN_TRANSFORMS__';
}









function __phpscan_taint_hook($func, $args)
{
  global $__phpscan_variable_map;
  global $__phpscan_op_ignore;
  global $__phpscan_transform;
  global $__phpscan_taint_hook;

  $__phpscan_op_ignore = true;

  $var_zval_id = null;
  $taint = array();
  $args_symbolic = array();
  for ($i = 0; $i < __phpscan_replace_count($args); ++$i)
  {
    $var = $args[$i];
    $var_zval_id = phpscan_var_id($var);
    if (__phpscan_replace_array_key_exists($var_zval_id, $__phpscan_variable_map))
    {
      $taint[] = $__phpscan_variable_map[$var_zval_id];
      $args_symbolic[] = array(
        'type' => 'symbolic',
        'id' => $__phpscan_variable_map[$var_zval_id],
        'value' => $var
      );
    }
    else
    {
      $args_symbolic[] = array(
        'type' => 'raw_value',
        'value' => $var
      );
    }
  }

  // TODO handle cases where multiple inputs are being tracked

  $res = __phpscan_replace_call_user_func_array($func, $args);

  $short_func = __phpscan_replace_str_replace('__phpscan_replace_', '', $func);
  if (__phpscan_replace_array_key_exists($short_func, $__phpscan_taint_hook))
  {
    $res = __phpscan_replace_call_user_func($__phpscan_taint_hook[$short_func], $res);
  }

  if (__phpscan_replace_count($taint) > 0)
  {
    $res_zval_id = phpscan_var_id($res);
    $__phpscan_variable_map[$res_zval_id] = $short_func . '(' . __phpscan_replace_implode(',', $taint) . ':' . __phpscan_replace_uniqid() . ')';

    phpscan_register_transform($__phpscan_variable_map[$res_zval_id],
                               $short_func,
                               $taint,
                               $args_symbolic);
  }

  $__phpscan_op_ignore = false;

  return $res;
}

function phpscan_register_transform($id, $func, $ids, $args)
{
  global $__phpscan_transform;
  $__phpscan_transform[$id] = array(
    'function' => $func,
    'ids' => $ids,
    'args' => $args
  );
}


function phpscan_replace_internals()
{
  $hook_functions = get_defined_functions()['internal'];
  $hook_functions = array_filter($hook_functions, function ($f)
  {
    $r = !preg_match('/^(.*runkit.*|dl|var_dump|printf|.*phpscan.*)$/', $f);

    return $r;
  });

  foreach ($hook_functions as $f)
  {
    // printf("Replacing %s ...\n", $f);
    runkit_function_rename($f, '__phpscan_replace_' . $f);
    runkit_function_add($f, '', 'return __phpscan_taint_hook("__phpscan_replace_' . $f . '", __phpscan_replace_func_get_args());');
  }
}



function phpscan_explode_taint_hook($res) // TODO should res be a reference?
{
  // Fixes testcase test_explode
  // If explode is called on a string that does not contain the split string $res[0] will point to the
  // same zval as the original string. Explictly separate them such that we can track $res[0] separately.
  if (__phpscan_replace_count($res) == 1)
  {
    $res[0] = phpscan_separate_zval($res[0]);
  }

  return $res;
}

$__phpscan_taint_hook['explode'] = 'phpscan_explode_taint_hook';

?>