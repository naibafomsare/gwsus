"""
===========
Suspensions
===========

.. container:: construction-notice

    **🛠️⛏️ Documentation under construction**   
    This section is incomplete and subject to change.

This is the main title and introduction of your tutorial. 
You can use reStructuredText or Markdown formatting here.
"""

# %%
# Step 1: Setting up variables
# ----------------------------
# This comment block acts as normal tutorial prose. You can explain *why*
# you are writing the code below.

import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

# %%
# Step 2: Executing and Visualizing
# ---------------------------------
# Sphinx-Gallery will run the following block, capture the console output, 
# and automatically embed the generated plot directly into the HTML page!

print(f"Generated {len(x)} data points.")

import matplotlib.pyplot as plt
plt.plot(x, y)
plt.show()
