# Load helpers and technology
source "helpers.tcl"
source "flow_helpers.tcl"
source "sky130hd/sky130hd.vars"

# Set design variables (like the regression scripts do)
set synth_verilog "gcd_sky130hd.v"
set design "gcd"
set top_module "gcd"
set sdc_file "gcd_sky130hd.sdc"
set die_area {0 0 299.96 300.128}
set core_area {9.996 10.08 289.964 290.048}

# Include flow.tcl to initialize the tech and STA
include -echo "flow.tcl"

# At this point, OpenROAD knows the technology and STA is ready

# Generate setup paths (max delay)
report_checks -path_delay max \
              -format full_clock_expanded \
              -group_count 50 \
              -digits 4

# Generate hold paths (min delay)
report_checks -path_delay min \
              -format full_clock_expanded \
              -group_count 50 \
              -digits 4

exit

