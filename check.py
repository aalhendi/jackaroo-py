#!/usr/bin/env python3
import numpy as np
print(np.unique(np.array(open("./random_1000.log").read().splitlines()), return_counts=True))
