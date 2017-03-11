<?php

register_shutdown_function('phpscan_handle_shutdown');

$__phpscan_variable_map = array();
$__phpscan_init_complete = false;
$__phpscan_op_ignore = false;
$__phpscan_op = array();



function phpscan_ext_opcode_handler($opcode, 
                  $op1, $op1type,
                  $op2, $op2type,
                  $result, $resulttype)
{
  global $__phpscan_init_complete;
  global $__phpscan_op_ignore;

  if (!$__phpscan_op_ignore && $__phpscan_init_complete)
  {
    if ($opcode === 38)
    {
      print 'GOT ASSIGN' . "\n";
    }
    else
    {
      $op = array(
        'opcode' => $opcode,

        'op1_value' => $op1,
        'op1_id' => phpscan_lookup_zval($op1),
        'op1_type' => $op1type,
        'op1_data_type' => gettype($op1),

        'op2_value' => $op2,
        'op2_id' => phpscan_lookup_zval($op2),
        'op2_type' => $op2type,
        'op2_data_type' => gettype($op2)
      );
      phpscan_log_op($op);
    }
  }
}

function phpscan_log_op($op)
{
  global $__phpscan_op;
  $__phpscan_op[] = $op;
}

function phpscan_initialize($state)
{
  phpscan_replace_internals();
  phpscan_initialize_environment($state);
}

function phpscan_initialize_environment($state)
{
  global $__phpscan_init_complete;

  $state_decoded = json_decode($state);

  foreach ($state_decoded as $var_name => $var_info)
  {
    $var = phpscan_initialize_variable($var_name, $var_info);
    phpscan_set_toplevel_variable($var_name, $var);
  }

  $__phpscan_init_complete = true;
}

function phpscan_set_toplevel_variable($var_name, $var)
{
  global ${$var_name};
  ${$var_name} = $var;
}


function phpscan_register_zval($var, $var_info)
{
  global $__phpscan_variable_map;
  $var_zval_id = phpscan_ext_get_zval_id($var);
  $__phpscan_variable_map[$var_zval_id] = $var_info->id;
}

function phpscan_lookup_zval($var)
{
  global $__phpscan_variable_map;
  global $__phpscan_op_ignore;

  $var_zval_id = phpscan_ext_get_zval_id($var);

  $__phpscan_op_ignore = true;
  $var_id = 'untracked (zval_id=' . $var_zval_id .')';
  // TODO __phpscan_replace should not be necessary here
  if (__phpscan_replace_array_key_exists($var_zval_id, $__phpscan_variable_map))
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
    default:
  }

  $var = phpscan_separate_zval($var);

  phpscan_register_zval($var, $var_info);

  if (($var_info->type == 'array') and (array_key_exists('properties', $var_info)))
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
  else {
    $separated_var .= '';
  }

  return $separated_var;
}

function phpscan_handle_shutdown()
{
  phpscan_report_opcodes();
}

function phpscan_flag($flag)
{
  print '__PHPSCAN_FLAG__' . $flag . '__/PHPSCAN_FLAG__';
}

function phpscan_report_opcodes()
{
  global $__phpscan_op;
  $json = json_encode($__phpscan_op);
  
  print '__PHPSCAN_OPS__' . $json . '__/PHPSCAN_OPS__';

  global $__phpscan_variable_map;
  var_dump('MAP', $__phpscan_variable_map);
}











function __phpscan_taint_hook($func, $args)
{
  global $__phpscan_variable_map;
  global $__phpscan_op_ignore;

  $__phpscan_op_ignore = true;

  $var_zval_id = null;
  $taint = false;
  for ($i = 0; $i < __phpscan_replace_count($args); ++$i)
  {
    $var = $args[$i];
    $var_zval_id = phpscan_ext_get_zval_id($var);
    if (__phpscan_replace_array_key_exists($var_zval_id, $__phpscan_variable_map))
    {
      $taint = true;
      break;
    }
  }

  // TODO handle cases where multiple inputs are being tracked

  $res = __phpscan_replace_call_user_func_array($func, $args);

  if ($taint)
  {
    $res_zval_id = phpscan_ext_get_zval_id($res);
    $__phpscan_variable_map[$res_zval_id] = $__phpscan_variable_map[$var_zval_id];

  }

  $__phpscan_op_ignore = false;

  return $res;
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
    printf("Replacing %s ...\n", $f);
    runkit_function_rename($f, '__phpscan_replace_' . $f);
    runkit_function_add($f, '', 'return __phpscan_taint_hook("__phpscan_replace_' . $f . '", __phpscan_replace_func_get_args());');
  }
}






?>