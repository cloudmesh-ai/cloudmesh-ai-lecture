# Data Visualization with Matplotlib

!!! info "Learning Objectives"

    By the end of this chapter, you will be able to:
    - Install and configure the `matplotlib` library for data visualization.
    - Generate line plots by integrating `NumPy` for data sampling and `matplotlib.pyplot` for rendering.
    - Enhance plot readability using axis labels, titles, legends, and predefined visual styles.
    - Implement bar charts to represent and compare categorical data.
    - Evaluate the differences between static plotting and interactive, browser-based visualization tools like `Bokeh`.

In the fields of AI and Cloud Engineering, the ability to visualize data is as critical as the ability to process it. Whether monitoring the loss curve of a training neural network, analyzing the latency of a microservice, or visualizing resource distribution across a cluster, graphical representations allow engineers to identify patterns and anomalies that remain hidden in raw logs or tables.

`matplotlib` is the foundational library for visualization in Python. It provides a low-level interface that allows for total control over every element of a figure. While higher-level libraries like `Seaborn` or `Plotly` are often used for complex statistical charts, they are almost all built upon the core engine of `matplotlib`.

## Installation and Setup

Before creating visualizations, the library must be installed in your environment. It is recommended to do this within a virtual environment to avoid conflicts with system-level packages.

```bash
$ pip install matplotlib
```

## Line Plots and Functional Data

Line plots are the most common way to visualize continuous data or functions. To create these, `matplotlib` is typically used in conjunction with `NumPy` to generate the numerical coordinates.

### Data Generation with NumPy

To plot a mathematical function, we first need a set of sample points. The `np.linspace` function is used to create an array of evenly spaced numbers over a specified interval.

```python
import numpy as np
import matplotlib.pyplot as plt

# Generate 16 evenly spaced samples between -pi and pi
x = np.linspace(-np.pi, np.pi, 16)
```

With the x-axis defined, we can generate the corresponding y-axis values using NumPy's trigonometric functions.

```python
cos = np.cos(x)
sin = np.sin(x)
```

### Rendering the Plot

The `plt.plot()` function maps the x and y arrays to a coordinate system. To display the resulting figure, `plt.show()` must be called.

```python
# Plot the cosine function
plt.plot(x, cos)
plt.show()
```

To visualize multiple datasets on the same graph, simply call `plt.plot()` multiple times before calling `plt.show()`.

```python
plt.plot(x, cos)
plt.plot(x, sin)
plt.show()
```

## Enhancing Plot Readability

A plot without context is technically accurate but practically useless. Professional visualizations require clear labeling to ensure they are interpretable by others.

### Labels, Titles, and Legends

To provide context, we use `xlabel`, `ylabel`, and `title`. To distinguish between multiple lines, we assign a `label` during the plot call and then invoke the `legend()` method.

```python
plt.plot(x, cos, label="cosine")
plt.plot(x, sin, label="sine")

plt.xlabel("X - label (units)")
plt.ylabel("Y - label (units)")
plt.title("A clever Title for your Figure")

# Position the legend in the upper right corner
plt.legend(loc='upper right')
plt.show()
```

### Complete Implementation Example

The following script combines data generation and visualization into a single, executable file.

```python
import numpy as np
import matplotlib.pyplot as plt

# 1. Data Preparation
x = np.linspace(-np.pi, np.pi, 16)
cos = np.cos(x)
sin = np.sin(x)

# 2. Plotting
plt.plot(x, cos, label="cosine")
plt.plot(x, sin, label="sine")

# 3. Customization
plt.xlabel("X - label (units)")
plt.ylabel("Y - label (units)")
plt.title("A clever Title for your Figure")
plt.legend(loc='upper right')

# 4. Rendering
plt.show()
```

## Categorical Data with Bar Charts

While line plots are for continuous data, bar charts are used for categorical data—where the x-axis represents distinct groups rather than a numerical range.

Example: Comparing the horsepower of various car models.

```python
import matplotlib.pyplot as plt

# Define categories and values
x = [' Toyota Prius',
     'Tesla Roadster ',
     ' Bugatti Veyron',
     ' Honda Civic ',
     ' Lamborghini Aventador ']
horse_power = [120, 288, 1200, 158, 695]

# Map categories to integer positions for the x-axis
x_pos = [i for i, _ in enumerate(x)]

# Create the bar chart
plt.bar(x_pos, horse_power, color='green')

# Customization
plt.xlabel("Car Model")
plt.ylabel("Horse Power (Hp)")
plt.title("Horse Power for Selected Cars")

# Replace integer positions with actual car model names
plt.xticks(x_pos, x)

plt.show()
```

## Visual Styling and Aesthetics

`matplotlib` includes a variety of predefined styles that can change the background color, grid lines, and color palettes of a plot with a single command.

### Discovering Available Styles

You can list all available styles installed in your environment using the following command:

```python
print(plt.style.available)
```

### Applying a Style

To apply a style, such as the popular `seaborn` theme, use `plt.style.use()`. This should be called at the beginning of the script to ensure all subsequent plots follow the theme.

```python
plt.style.use('seaborn')
```

## Beyond Static Plots: Interactive Visualization

While `matplotlib` generates static images, modern data science often requires interactive plots that allow users to zoom, pan, and hover over data points. `Bokeh` is a powerful library designed specifically for this purpose, outputting visualizations directly to a web browser.

Example of creating an interactive scatter plot with `Bokeh`:

```python
from bokeh.io import show
from bokeh.plotting import figure

# Define data
x_values = [1, 2, 3, 4, 5]
y_values = [6, 7, 2, 3, 6]

# Create a figure object
p = figure()

# Add circle markers to the plot
p.circle(x=x_values, y=y_values)

# Display the plot in a browser
show(p)
```

!!! tip "Summary Checklist"

    - [ ] Installed `matplotlib` via `pip`.
    - [ ] Used `np.linspace` to generate coordinate samples for functional plots.
    - [ ] Implemented `plt.plot()` to render line graphs.
    - [ ] Added `xlabel`, `ylabel`, and `title` to provide plot context.
    - [ ] Used `label` and `plt.legend()` to distinguish multiple datasets.
    - [ ] Created bar charts using `plt.bar()` and `plt.xticks()`.
    - [ ] Applied visual themes using `plt.style.use()`.
    - [ ] Identified the use case for interactive plotting via `Bokeh`.

!!! note "Exercise 1: Sampling and Resolution"

    **Task**: Recreate the sine and cosine plot, but vary the third parameter of `np.linspace`. Compare the results using 5, 50, and 500 samples.
    **Goal**: Understand how sampling resolution affects the visual smoothness of a curve.

!!! note "Exercise 2: Performance Comparison"

    **Task**: Create a bar chart that compares the response times (in milliseconds) of three different API endpoints (e.g., `/login`, `/search`, `/upload`). Use different colors for each bar.
    **Goal**: Practice representing categorical performance metrics.

!!! note "Exercise 3: Multi-Plot Dashboard"

    **Task**: Use `plt.subplot()` to create a single figure containing two plots: one showing a line graph of a function and another showing a bar chart of related categorical data.
    **Goal**: Master the layout of complex figures for comprehensive data reporting.
