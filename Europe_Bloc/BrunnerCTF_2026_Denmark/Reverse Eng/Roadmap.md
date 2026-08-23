  Solver : SideChiks
  ### Challenge Analysis
  The Roadmap challenge implements an Nginx-based state machine that checks whether the requested URL matches a specific approved 41-character route.

  #### Key Mechanics in default.conf & roadmap-badges.conf:
  1. Length Check: map $route $route_len_ok enforces that the route path (stripped of the leading /) must be exactly 41 characters long (~^.{41}$).
  2. Character Extraction & Badges:
      • Variables $wp_<hash> extract individual characters at specific offsets (e.g., ~^.{8}(?<c>.) captures index 8).
      • Variables $badge_<hash> translate characters into 2-character hex tokens using the mapping in roadmap-badges.conf.
  3. Checkpoint State Transitions:
      • An initial state cp_8a32 is activated when badge_a8e4 equals "0a" (character 'r' at index 18).
      • Subsequent checkpoints ($cp_<hash>) transition step-by-step when combined with the expected badge at each waypoint, until finally reaching
      "CLEARED" at cp_199f.
  ──────
  ### Solution Script

  We can trace the transition graph from the starting checkpoint to the CLEARED state:
    import re
    
    # 1. Load badge to character mappings
    badges = {}
    with open("roadmap-badges.conf") as f:
        for line in f:
            m = re.search(r'"([^"]+)"\s+"([^"]+)"', line)
            if m:
                char, badge = m.groups()
                badges[badge] = char
    
    # 2. Parse default.conf
    with open("default.conf") as f:
        conf = f.read()
    
   # Map waypoint variable -> route string index
    wp_to_idx = {}
    for m in re.finditer(r'map \$route \$(\w+)\s+\{\s*default ""; "~^\.\{(\d+)\}\(\?<c>\.\)" \$c; \}', conf):
        wp, idx = m.group(1), int(m.group(2))
        wp_to_idx[wp] = idx
    
    # Map waypoint -> badge variable
    badge_to_wp = {}
    for m in re.finditer(r'map \$(\w+)\s+\$(\w+)\s+\{\s*include roadmap-badges\.conf; \}', conf):
        wp, badge = m.group(1), m.group(2)
        badge_to_wp[badge] = wp
    
    # Parse start state and chained checkpoint transitions
    start_badge = None
    start_val = None
    start_cp_out = None
    transitions = {}

    for line in conf.splitlines():
        line = line.strip()
        m_start = re.match(r'map \$(\w+)\s+\$(\w+)\s+\{\s*default "DETOUR";\s*"([^"]+)"\s+"([^"]+)";\s*\}', line)
        if m_start:
            badge_var, _, req_val, cp_out_val = m_start.groups()
            start_badge, start_val, start_cp_out = badge_var, req_val, cp_out_val
            continue
        
        m_chain = re.match(r'map "\$\{(\w+)\}:\$\{(\w+)\}"\s+\$(\w+)\s+\{\s*default "DETOUR";\s*"([^:]+):([^"]+)"\s+"([^"]+)";\s*\}', line)
        if m_chain:
            _, badge_var, _, cp_in_val, req_badge_val, cp_out_val = m_chain.groups()
            transitions[cp_in_val] = (badge_var, req_badge_val, cp_out_val)

    # 3. Follow the state chain
    flag_chars = {}
    flag_chars[wp_to_idx[badge_to_wp[start_badge]]] = badges[start_val]

    curr_cp = start_cp_out
    while curr_cp != "CLEARED":
        badge_var, req_badge_val, next_cp = transitions[curr_cp]
        idx = wp_to_idx[badge_to_wp[badge_var]]
        flag_chars[idx] = badges[req_badge_val]
        curr_cp = next_cp

    flag = "".join(flag_chars[i] for i in range(41))
    print("Cleared Route / Flag:", flag)
  ──────
  ### Result / Flag

    brunner{c0rp0r4t3_r04dm4p_t0_ng1nx_h34rt}

