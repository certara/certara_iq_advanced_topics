# IQ Python Client – Troubleshooting Guide

This guide covers common warnings, errors, and performance issues encountered
when using the `abm` Python client, along with diagnostic strategies and
recommended fixes.

---

## Table of Contents

1. [`abm.simulate` — Warnings and Errors](#abmsimulate--warnings-and-errors)
   - [Duplicate parameters](#duplicate-parameters)
   - [Parameters ignored by the model](#parameters-ignored-by-the-model)
   - [NaN-valued outputs](#nan-valued-outputs)
   - [Integrator errors](#integrator-errors)
2. [Debugging Workflow](#debugging-workflow)
3. [`abm.optimize` — Issues and Diagnostics](#abmoptimize--issues-and-diagnostics)
   - [Fit errors out after some iterations](#fit-errors-out-after-some-iterations)
   - [Fit progresses very slowly](#fit-progresses-very-slowly)
   - [Inexplicably poor quality of fit](#inexplicably-poor-quality-of-fit)

---

## `abm.simulate` — Warnings and Errors

### Duplicate parameters

**Error message:**
```
ValueError: Duplicate found: {parameter names}
```

**Cause:** One or more of your label sets matches two or more rows in the
parameter table for the listed parameters. This means the client cannot
determine which parameter value to use for a given simulation.

**Resolution:** You have two options:

- Add more label columns to the rows in the parameter table to make them
  uniquely distinguishable, or
- Add the missing label columns to your simulations table so that the matching
  is more specific.

**Diagnostic helper:** Use the function below to identify which
simulation/parameter combinations produce duplicates:

```python
def find_duplicate_parameter_matches(
    simulations: pd.DataFrame,
    parameters: pd.DataFrame,
) -> pd.DataFrame:
    """
    For each row in `simulations`, find all rows in `parameters` that match via
    label column semantics: a parameter row matches a simulation row when, for
    every shared label column, the parameter's value is "*" (match-all) or equals
    the simulation's concrete value.  From those matches, keep only the rows whose
    `parameter` name appears more than once for that simulation — i.e., the
    parameter is ambiguously duplicated.

    Returns a DataFrame in which each row pairs the simulation's concrete label
    values with one matching (duplicate) parameter row.  Parameter label columns
    that share a name with a simulation label column are prefixed with "param_"
    to avoid collision.

    Parameters
    ----------
    simulations : pd.DataFrame
        Simulation table; every column is treated as a label column.
    parameters : pd.DataFrame
        Parameter table; must contain "parameter", "value", and "unit" columns.
        All other columns are treated as label columns.
    """
    PARAM_REQUIRED = {"parameter", "value", "unit"}

    sim_label_cols = list(simulations.columns)
    param_label_cols = [c for c in parameters.columns if c not in PARAM_REQUIRED]

    # Only columns present in *both* tables drive matching.
    shared_label_cols = [c for c in sim_label_cols if c in param_label_cols]

    records = []

    for _, sim_row in simulations.iterrows():
        # Build a boolean mask for parameter rows that match this simulation row.
        mask = pd.Series(True, index=parameters.index)
        for col in shared_label_cols:
            sim_val = sim_row[col]
            mask &= (parameters[col] == "*") | (parameters[col] == sim_val)

        matched_params = parameters[mask]

        # A parameter is "duplicate" if its name appears more than once among
        # the matched rows for this simulation.
        param_counts = matched_params["parameter"].value_counts()
        duplicate_names = param_counts[param_counts > 1].index
        duplicate_rows = matched_params[matched_params["parameter"].isin(duplicate_names)]

        for _, param_row in duplicate_rows.iterrows():
            record = {}

            # Concrete label values from the simulation row come first.
            for col in sim_label_cols:
                record[col] = sim_row[col]

            # All parameter columns follow; prefix any name that collides with a
            # simulation label column so both values are preserved.
            for col in parameters.columns:
                out_col = f"param_{col}" if col in sim_label_cols else col
                record[out_col] = param_row[col]

            records.append(record)

    if not records:
        out_cols = sim_label_cols + [
            (f"param_{c}" if c in sim_label_cols else c)
            for c in parameters.columns
        ]
        return pd.DataFrame(columns=out_cols)

    return pd.DataFrame(records).reset_index(drop=True)
```

---

### Parameters ignored by the model

**Warning message:**
```
UserWarning: Parameters not present in the model will be ignored: {parameters}
```

**Cause:** The listed parameters were present in the parameter table but do not
exist in the model, so their values are silently ignored.

**Resolution:** This is harmless if intentional. However, it often indicates a
typographical error in one or more parameter names. Verify the spelling of the
flagged parameter names against the model definition.

---

### NaN-valued outputs

**Cause:** NaN outputs are most commonly caused by NaN-valued parameters
propagating through the model's assignment expressions. This typically occurs
when a parameter is set to `nan` in the model file and no overriding value is
provided in the parameter table. The NaNs propagate downstream, so the
quantities that appear in the error output are often not themselves the root
cause.

**Resolution:**
1. Set the default values of suspicious parameters from `nan` to a recognizable
   indicator value such as `1234`.
2. Simulate to time 0.
3. Inspect the results for outputs carrying the indicator value — those
   parameters are missing from the parameter table.

A secondary cause is zero-valued denominators in assignment expressions such as
receptor occupancies. If the above steps do not resolve the issue, add a small
constant to any denominator that could evaluate to zero.

---

### Integrator errors

Integrator errors typically manifest as a "solver cannot progress" message and
usually stem from one of the following causes.

#### `abstol` set too large

`abstol` controls the threshold below which errors in state values are
considered negligible. The default value of `1e-9` is often too large,
particularly for models with states such as cell counts that have small `nmol`
values — for example, in vitro models.

**Symptom:** Some state time courses appear jagged or rough.

**Resolution:** Set `abstol=1e-15`, which corresponds to slightly less than one
molecule in `nmol`. This is the first thing to try for any integrator error.

#### States changing too fast

The integrator adapts its step size to keep error within the specified
tolerances. If states change over multiple orders of magnitude within seconds,
the required step size can become infeasibly small, triggering a "solver cannot
progress" error.

**Symptom:** The error message prints the state values and their time
derivatives.

**Diagnosis:** Look for time derivatives whose absolute values are far larger
than their corresponding state values, then identify the reactions that affect
those states. This issue is most commonly caused by parameters set to extreme
values, particularly for non-intuitive parameters with unusual units.

#### Negative states

If reactions drive a state to negative values, the integrator will repeatedly
reduce its step size to avoid the violation, eventually failing.

**Symptom:** "Solver cannot progress" error. Looking at the printed state values
and time derivatives, look for states with very small values but relatively
large negative time derivatives.

**Resolution:**
- Identify the reactions responsible for the negative values and review the
  driving parameters.
- Note that an `abstol` that is too large can also cause states to go negative
  by allowing the integrator to ignore small errors; try `abstol=1e-15` as well.

#### Negative exponents

If a quantity is raised to a negative power, the derivative becomes
unbounded as the quantity approaches zero. Because the solver uses the system Jacobian, 
NaN or infinite Jacobian entries from such terms force premature termination.

**Symptom:** "Solver cannot progress" error with no obvious large time
derivatives or negative states.

**Diagnosis:** Search the model file for exponents that could be negative —
either hard-coded or parameterized — and whose base expression could reach zero.

**Resolution:** Add a small constant inside the exponentiated term to prevent
the base from ever reaching zero:

```
(x + 1e-15)^n - 1e-15^n
```

The subtracted outer term ensures the expression evaluates to zero when `x = 0`.

---

## Debugging Workflow

When investigating unexpected simulation behavior, a useful pattern is to set
up a small plotting function that runs a representative subset of simulations
and renders arbitrary expressions of the model outputs:

```python
def plot_expressions(**exprs):
    """Timecourse plots for arbitrary expressions of model quantities.

    Parameters
    ----------
    **exprs
        Expressions to plot and labels to show on the plot provided as
        `plot_expressions(name_1=expr_1, name_2=expr_2, ...)`.
        Expressions should be provided as strings.

    Returns
    -------
    p9.ggplot
        Plot of the timecourses, with each expression shown on a different facet.
    """
    simulations = ...

    df = abm.simulate(
        models=...,
        parameters=...,
        doses=...,
        simulations=simulations,
        times=...
    ).to_pandas(tall_outputs=False)

    for name, expr in exprs.items():
        df[name] = df.eval(expr)

    df = df.melt(
        id_vars=list(simulations.columns) + ['t'],
        value_vars=list(exprs.keys()),
        var_name='output',
        value_name='value',
    )

    return (
        p9.ggplot(df, p9.aes('t', 'value'))
        + p9.geom_line()
        + p9.facet_wrap('~ output')
    )
```

**Tips for effective use:**

- Reaction rates can be plotted by copying their expressions directly from the
  model file.
- Work backward from the output you want to understand: plot the states that
  comprise it to see which contribute to the behavior, then plot the reaction
  rates acting on those states.
- Decompose complicated expressions into sub-terms before plotting to isolate
  which part drives the behavior.

---

## `abm.optimize` — Issues and Diagnostics

### Fit errors out after some iterations

**Cause:** During optimization, parameter values can drift into regimes that
trigger integrator failures as described in the [`abm.simulate` section](#integrator-errors)
above.

**Resolution:** Apply stricter bounds on the parameters being fitted and/or
apply the fixes recommended in the integrator errors section.

---

### Fit progresses very slowly

Slow fit progression has two common causes.

#### Poorly conditioned parameter space (nonidentifiability)

If the likelihood is very sensitive to some parameters and completely insensitive
to others, the optimizer is forced to take very small steps. This is often a
sign that some parameters are nonidentifiable.

**Resolution:**
1. Apply priors to the parameters being calibrated. Normal or lognormal priors
   with large standard deviations are a good starting point — even weak priors
   can improve conditioning.
2. If the fit completes with priors, calculate confidence intervals or profile
   likelihoods to identify which parameters are nonidentifiable.
3. Consider fixing nonidentifiable parameters or fitting fewer parameters overall.
4. Run a local sensitivity analysis to confirm that the parameters you are
   fitting actually affect the outputs you are fitting. If they do not, those
   parameters may be fixed. If they should but do not, the parameters may be at
   extreme values or there may be a structural issue with the model — use the
   [debugging workflow](#debugging-workflow) to investigate.

#### Optimization tolerance too tight

The calibration can stall near convergence because the default optimization
tolerance of `1e-8` is too strict, causing the optimizer to pursue improvements
beyond what is numerically meaningful.

**Resolution:** Set `opttol=1e-4` or `opttol=1e-5`.

---

### Inexplicably poor quality of fit

When the model consistently fails to fit the data well, the most common causes
are problematic data and a poor choice of error model.

#### Problematic data

If a subset of the data is structurally incompatible with the model, the
optimizer may sacrifice the quality of fit across the remaining data points in
an attempt to accommodate the difficult measurements. Common culprits include
outliers, non-zero subcutaneous PK measurements at times close to zero, and
post-dose concentration values that have a pre-dose timepoint.

**Note:** These problematic points are often not visually obvious in a time
course plot.

**Diagnosis:**
1. Call the `residuals()` method on the optimization result and sort the output
   by the absolute value of the normalized residual.
2. Replot the model-versus-data comparison, coloring each measurement by its
   absolute normalized residual to make large-residual points visible.
3. Use the `.query()` method on the measurements DataFrame to isolate subsets
   (by output, patient, timepoint, etc.) and determine whether the poor fit
   persists for specific subgroups.

#### Poor error model choice

The error model determines how the difference between simulation and data
translates into an objective function contribution:

- **Constant error:** Contribution scales with the natural-scale difference.
  Use for data plotted on a natural scale.
- **Exponential error:** Contribution scales with the log-scale difference.
  Use for data plotted on a log scale.
- **Proportional error:** Similar to exponential for small errors relative to
  the measurement value, but note that large proportional errors make the
  optimization insensitive to underestimates.

**Recommendation:** Match the error model to how the data are displayed — use
constant error for natural-scale data and exponential error for log-scale data.
This ensures that the visual distance between simulation and data is proportional
to the objective function contribution. If you observe consistent underestimates
of the data, consider switching from proportional to exponential error models.
