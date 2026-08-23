  ### Layer Pipeline by Dimensions

  2. self.quokka: 4 → 18
  1. Input: 4
  3. self.zephyr: 18 → 13
  4. self.vortex: 13 → 15
  5. self.thistle: 15 → 14
  6. self.ember: 14 → 10
  7. self.nimbus: 10 → 50 (Output characters)
  ──────
  ### Updated forward implementation in half_baked.py:29-37:

        def forward(self, x):
            # Help combine all recipe steps and activate the ingredients with yeast
            x = F.relu(self.quokka(x))
            x = F.relu(self.zephyr(x))
            x = F.relu(self.vortex(x))
            x = F.relu(self.thistle(x))
            x = F.relu(self.ember(x))
            x = self.nimbus(x)
            return x
  ──────
  ### Flag / Extracted Recipe:

    brunner{d0ugh_butt3r_sug4r_c1nn4mon_cr34m_c4r4m3l}
