import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 1. Build a monthly date index covering the last 5 years (2021-2026)
end_date = datetime.today()
start_date = end_date - timedelta(days=5*365)
date_index = pd.date_range(start=start_date, end=end_date, freq='MS')

# 2. Generate synthetic popularity scores (0-100)
np.random.seed(42)

# VM technologies: steady decline then stabilization (floor at ~40%)
vm_trend = np.linspace(80, 40, len(date_index)) 
vm_trend = vm_trend + 5 * np.sin(np.linspace(0, np.pi, len(date_index)))
vm_noise = np.random.normal(loc=0, scale=3, size=len(date_index))
vm_popularity = np.clip(vm_trend + vm_noise, 0, 100)

# Container technologies: rapid growth then plateau (ceiling at ~85%)
container_trend = 20 + 65/(1 + np.exp(-0.4*(np.arange(len(date_index))-20)))
container_noise = np.random.normal(loc=0, scale=4, size=len(date_index))
container_popularity = np.clip(container_trend + container_noise, 0, 100)

# Assemble into a DataFrame
df = pd.DataFrame({
    'Date': date_index,
    'VM_Technologies': vm_popularity,
    'Container_Technologies': container_popularity
}).set_index('Date')

# 3. Plot the two series
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['VM_Technologies'],
         label='Virtual-Machine Technologies',
         linewidth=2, color='steelblue')
plt.plot(df.index, df['Container_Technologies'],
         label='Container Technologies',
         linewidth=2, color='darkorange')
plt.title('Popularity Trend: Virtual-Machine vs. Container Technologies (2021-2026)',
          fontsize=14, pad=15)
plt.xlabel('Year')
plt.ylabel('Popularity Index (0-100)')
plt.legend(loc='upper left')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('vm_vs_container_popularity-2026.png', dpi=300)
plt.show()