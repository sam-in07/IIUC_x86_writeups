### Challenge Breakdown & Analysis

  The kpiman binary is a 64-bit non-stripped ELF executable. It takes an employee ID (44 characters long) and evaluates it across three validation
  functions to reach a 100% productivity score:

  #### 1. calculateSynergy (Indices 0–14)

  • Logic: For each index i from 0 to 14, input[i] ^ (((i * 7) + 0x2a) & 0xff) == kpi_alpha[i].
  • Result: brunner{y0ur_kp

  #### 2. measureVelocity (Indices 15–29)

  • Logic: For each index i from 15 to 29, input[i] + input[i - 1] == kpi_beta[i - 15].
  • Using input[14] from the previous step, input[i] is computed iteratively as kpi_beta[i - 15] - input[i - 1].
  • Result: 1s_ar3_n0t_l00k

  #### 3. assessAlignment (Indices 30–43)

  • Logic: For each index i from 30 to 43, synergy_table[input[i]] == kpi_gamma[i - 30].
  • Reversing the byte lookup in synergy_table gives the remaining characters.
  • Result: ing_gr8_buddy}
  ──────
  ### Execution Verification

  Running kpiman with the derived ID:

    $ ./kpiman
    BrunnerCorp KPIman v3.1
    Enter employee ID: brunner{y0ur_kp1s_ar3_n0t_l00king_gr8_buddy}
    Analyzing synergy...
    Productivity: 100%. Finally, someone who gets it.
    Promotion code: brunner{y0ur_kp1s_ar3_n0t_l00king_gr8_buddy}


