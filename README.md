![image](https://github.com/user-attachments/assets/9410d691-4627-4dbb-bb72-e3de4897ce6b)


# sysmonlog
System Monitor 

Edit the first few lines in script to customize what is shown. 

#HOW TO USE

`Commands to run are:`

  `'-nolog' for faster update and no write to log.json file.`
  
  `'-all' to override user config and toggle all metrics as true. `
  
 `Set the update intervals and path to save log.json below. `

` User-configurable settings`

NOLOG_TIMER = 1.25  # Timer when '-nolog' is used

SLEEP_TIMER = 1800  # Default time interval between logs (in seconds)

OUTPUT_PATH = 'log.json'  # Default path for the output log file

MAX_LOG_ENTRIES = 0  # 0 for unlimited, >0 to limit entries in log.json

 Metrics toggle settings
 
settings = {

    "show_uptime": True,
    "show_cpu_info": False,
    "show_cpu_frequency": False,
    "show_cpu_cores": False,
    "show_cpu_threads": False,
    "show_disk_io": True,
    "show_disk_usage": True,
    "show_total_processes": True,
    "show_active_connections": True,
    "show_cpu_usage": True,
    "show_ram_usage": True,
    "show_network_io": False,
    "show_data_downloaded": True,
    "show_data_uploaded": True,
    "show_cpu_temperature": False,
    "show_battery_status": False,
    "show_swap_memory": False,
    "show_top_processes": False`
`
