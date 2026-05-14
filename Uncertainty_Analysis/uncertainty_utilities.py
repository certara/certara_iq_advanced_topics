import numpy as np
from abm._helper.covariance_matrix import AnnotatedFisherRow, confidence_intervals, covariance_matrix as covariance_matrix_helper

def covariance_matrix(
    self,
    uncertainty_ceiling: float = float("inf"),
) -> np.ndarray:
    """Compute the covariance matrix of the fitted parameters.

    The covariance matrix is the inverse of the Fisher information matrix
    evaluated at the MAP estimate.

    Parameters
    ----------
    uncertainty_ceiling : float, default = inf
        Cap on parameter uncertainties (sqrt of diagonal entries). Useful
        when parameters are near-non-identifiable, where inverting the FIM
        is numerically unstable. A value like 1e8 is a reasonable choice.

    Returns
    -------
    np.ndarray of shape (n_params, n_params)
        Covariance matrix in the optimizer's transformed parameter space.
        For parameters with ``loguniform`` priors the optimizer works in
        log-space, so the returned matrix is a log-space covariance; callers
        must exponentiate samples drawn from this distribution to recover
        natural-scale values.  Row/column order matches the keys of
        ``_fit_global_parameters``.
    """
    raw_fim = self._fim().output_or_raise()
    fit_global_parameters = self._fit_global_parameters
    fit_global_parameter_values = self._fit_global_parameters_dict

    annotated_fim: dict[str, AnnotatedFisherRow] = {
        name: AnnotatedFisherRow(
            parameter_value=fit_global_parameter_values[name],
            parameter_prior=fit_global_parameters[name].prior,
            values=values,
        )
        for name, values in raw_fim.items()
    }

    return covariance_matrix_helper(annotated_fim, uncertainty_ceiling)