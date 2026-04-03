# DEPRECATED — replaced by seed_routing_table.py (Phase 1)
#
# The old hardcoded roles (municipal_officer, department_head, city_planner,
# system_admin) no longer match the admin hierarchy.
#
# Use this instead:
#   cd backend
#   python script/seed_routing_table.py
#
# That script creates 7 accounts with correct roles:
#   super_admin, city_admin (x2), dept_officer (x4)
# and populates the routing_table with city/department → officer mappings.
raise SystemExit("Deprecated. Run: python script/seed_routing_table.py")
