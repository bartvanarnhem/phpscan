<?php

if (isset($_GET['page'], $_GET['num']))
{
  if ($_GET['page'] === 'home')
  {
    phpscan_flag('reached_home');
  }
  
  if (intval($_GET['num'] > 10))
  {
    phpscan_flag('reached_greater_than');
  }
}

?>
