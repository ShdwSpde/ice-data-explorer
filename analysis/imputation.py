"""
Project Watchtower - Obfuscated Data Imputation
FR 1.5: When agencies cease reporting unfavorable data series,
use probabilistic time-series modeling to visualize predicted values.

Marks imputed values clearly as "Inferred due to government obfuscation."
"""

import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
import plotly.graph_objects as go
from dash import html, dcc
from database import query_data


class DataImputationEngine:
    """
    Handles imputation of missing/obfuscated government data series.

    When agencies stop reporting certain metrics (often when the numbers
    become politically inconvenient), this engine uses historical trends
    and leading indicators to estimate what the values likely are.
    """

    def __init__(self):
        self.models = {}

    def fit_trend(self, years, values, model_type='linear'):
        """
        Fit a trend model to historical data.

        Args:
            years: Array of years
            values: Array of corresponding values
            model_type: 'linear', 'exponential', or 'logistic'

        Returns:
            Dict with model parameters and prediction function
        """
        years = np.array(years, dtype=float)
        values = np.array(values, dtype=float)

        # Remove NaN values
        mask = ~np.isnan(values)
        years = years[mask]
        values = values[mask]

        if len(years) < 3:
            return None

        if model_type == 'linear':
            slope, intercept, r_value, p_value, std_err = stats.linregress(years, values)

            def predict(year):
                return slope * year + intercept

            return {
                'type': 'linear',
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value ** 2,
                'std_err': std_err,
                'predict': predict,
                'residual_std': np.std(values - predict(years))
            }

        elif model_type == 'exponential':
            try:
                def exp_func(x, a, b, c):
                    return a * np.exp(b * (x - years[0])) + c

                popt, pcov = curve_fit(exp_func, years, values, maxfev=5000,
                                       p0=[values[0], 0.05, 0])

                def predict(year):
                    return exp_func(year, *popt)

                residuals = values - predict(years)
                return {
                    'type': 'exponential',
                    'params': popt,
                    'r_squared': 1 - np.var(residuals) / np.var(values),
                    'predict': predict,
                    'residual_std': np.std(residuals)
                }
            except (RuntimeError, ValueError):
                # Fall back to linear if exponential doesn't converge
                return self.fit_trend(years, values, 'linear')

        elif model_type == 'logistic':
            try:
                def logistic_func(x, L, k, x0, b):
                    return L / (1 + np.exp(-k * (x - x0))) + b

                p0 = [max(values) * 1.5, 0.1, np.median(years), min(values)]
                popt, pcov = curve_fit(logistic_func, years, values,
                                       p0=p0, maxfev=5000)

                def predict(year):
                    return logistic_func(year, *popt)

                residuals = values - predict(years)
                return {
                    'type': 'logistic',
                    'params': popt,
                    'r_squared': 1 - np.var(residuals) / np.var(values),
                    'predict': predict,
                    'residual_std': np.std(residuals)
                }
            except (RuntimeError, ValueError):
                return self.fit_trend(years, values, 'linear')

    def impute_missing_years(self, known_years, known_values, missing_years,
                             model_type='auto', confidence_level=0.95):
        """
        Impute values for years where data is missing/obfuscated.

        Args:
            known_years: Years with data
            known_values: Known values
            missing_years: Years to predict
            model_type: Model type or 'auto' to select best fit
            confidence_level: Confidence level for intervals

        Returns:
            Dict with predictions and confidence intervals
        """
        if model_type == 'auto':
            # Try multiple models, pick best fit
            best_model = None
            best_r2 = -1

            for mtype in ['linear', 'exponential']:
                model = self.fit_trend(known_years, known_values, mtype)
                if model and model['r_squared'] > best_r2:
                    best_model = model
                    best_r2 = model['r_squared']

            model = best_model
        else:
            model = self.fit_trend(known_years, known_values, model_type)

        if model is None:
            return None

        # Generate predictions with confidence intervals
        predictions = []
        z_score = stats.norm.ppf((1 + confidence_level) / 2)

        for year in missing_years:
            predicted = model['predict'](year)
            margin = z_score * model['residual_std']

            # Increase uncertainty for further out predictions
            max_known = max(known_years)
            years_out = max(0, year - max_known)
            uncertainty_factor = 1 + (years_out * 0.15)  # 15% more uncertain per year
            margin *= uncertainty_factor

            predictions.append({
                'year': int(year),
                'predicted': float(predicted),
                'lower': float(predicted - margin),
                'upper': float(predicted + margin),
                'uncertainty_factor': uncertainty_factor,
                'is_imputed': True
            })

        return {
            'model': model,
            'predictions': predictions,
            'confidence_level': confidence_level,
            'model_type': model['type'],
            'r_squared': model['r_squared']
        }


def create_imputation_chart(metric_name, known_years, known_values,
                            imputed_result, unit='', obfuscation_note=''):
    """
    Create a Plotly chart showing known data and imputed values.

    Args:
        metric_name: Name of the metric
        known_years: Years with actual data
        known_values: Actual values
        imputed_result: Output from impute_missing_years()
        unit: Unit label (e.g., 'deaths', '$M')
        obfuscation_note: Explanation of why data is missing

    Returns:
        Dash component with the visualization
    """
    fig = go.Figure()

    # Known data points
    fig.add_trace(go.Scatter(
        x=known_years,
        y=known_values,
        mode='lines+markers',
        name='Reported Data',
        line=dict(color='#3d5a80', width=2),
        marker=dict(size=8, color='#3d5a80'),
        hovertemplate='%{x}: %{y:,.0f} ' + unit + '<extra>Reported</extra>'
    ))

    if imputed_result and imputed_result['predictions']:
        pred_years = [p['year'] for p in imputed_result['predictions']]
        pred_values = [p['predicted'] for p in imputed_result['predictions']]
        pred_lower = [p['lower'] for p in imputed_result['predictions']]
        pred_upper = [p['upper'] for p in imputed_result['predictions']]

        # Confidence interval fill
        fig.add_trace(go.Scatter(
            x=pred_years + pred_years[::-1],
            y=pred_upper + pred_lower[::-1],
            fill='toself',
            fillcolor='rgba(229, 62, 62, 0.15)',
            line=dict(color='rgba(229, 62, 62, 0)'),
            name=f'{int(imputed_result["confidence_level"]*100)}% Confidence Interval',
            hoverinfo='skip'
        ))

        # Imputed prediction line
        fig.add_trace(go.Scatter(
            x=pred_years,
            y=pred_values,
            mode='lines+markers',
            name='Inferred (Obfuscated)',
            line=dict(color='#e53e3e', width=2, dash='dash'),
            marker=dict(size=8, symbol='diamond', color='#e53e3e'),
            hovertemplate='%{x}: %{y:,.0f} ' + unit + '<extra>Inferred</extra>'
        ))

        # Add "OBFUSCATED" annotation
        if pred_years:
            fig.add_annotation(
                x=pred_years[0],
                y=max(pred_values) * 1.1,
                text="⚠️ DATA OBFUSCATED<br>Values inferred from historical trends",
                showarrow=True,
                arrowhead=2,
                arrowcolor='#e53e3e',
                font=dict(color='#e53e3e', size=11),
                bgcolor='rgba(229, 62, 62, 0.1)',
                bordercolor='#e53e3e',
                borderwidth=1,
            )

    fig.update_layout(
        title=dict(
            text=metric_name,
            font=dict(size=16, color='white', family='Libre Baskerville')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            color='white',
            title='Year'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            color='white',
            title=unit
        ),
        legend=dict(
            font=dict(color='white'),
            bgcolor='rgba(0,0,0,0.3)',
            bordercolor='rgba(255,255,255,0.1)',
        ),
        margin=dict(l=60, r=30, t=60, b=60),
        height=400,
    )

    return html.Div([
        dcc.Graph(
            figure=fig,
            config={'displayModeBar': False},
            className='imputation-chart'
        ),
        html.Div([
            html.Span("⚠️ ", className='imputation-warning-icon'),
            html.Span(
                obfuscation_note or "Values marked with dashed lines are inferred due to government data obfuscation.",
                className='imputation-warning-text'
            ),
            html.Span(
                f" Model: {imputed_result['model_type']} (R² = {imputed_result['r_squared']:.3f})" if imputed_result else "",
                className='imputation-model-info'
            )
        ], className='imputation-warning'),
    ], className='imputation-container')


def get_obfuscated_metrics():
    """
    Identify and return metrics where government reporting has been
    curtailed or obfuscated, with imputed estimates.
    """
    engine = DataImputationEngine()
    imputed_metrics = []

    # Example: Deaths in custody - gaps in reporting
    deaths_data = query_data('''
        SELECT year, deaths FROM deaths_in_custody
        ORDER BY year ASC
    ''')

    if deaths_data:
        years = [d['year'] for d in deaths_data]
        values = [d['deaths'] for d in deaths_data]

        # Find gaps
        all_years = list(range(min(years), max(years) + 2))
        missing = [y for y in all_years if y not in years]

        if missing:
            result = engine.impute_missing_years(years, values, missing)
            if result:
                imputed_metrics.append({
                    'metric': 'Deaths in Custody',
                    'known_years': years,
                    'known_values': values,
                    'result': result,
                    'unit': 'deaths',
                    'note': 'ICE has periods of delayed or incomplete death reporting. Independent sources suggest higher actual counts.'
                })

    # Budget data - check for gaps
    budget_data = query_data('''
        SELECT year, budget_millions FROM agency_budgets
        WHERE agency = 'ICE'
        ORDER BY year ASC
    ''')

    if budget_data:
        years = [d['year'] for d in budget_data]
        values = [d['budget_millions'] for d in budget_data]
        all_years = list(range(min(years), max(years) + 2))
        missing = [y for y in all_years if y not in years]

        if missing:
            result = engine.impute_missing_years(years, values, missing)
            if result:
                imputed_metrics.append({
                    'metric': 'ICE Budget',
                    'known_years': years,
                    'known_values': values,
                    'result': result,
                    'unit': '$M',
                    'note': 'Budget figures may be incomplete for certain years.'
                })

    return imputed_metrics
