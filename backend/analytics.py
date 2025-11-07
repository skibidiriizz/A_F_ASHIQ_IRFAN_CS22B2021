"""
Analytics Engine
Computes quantitative analytics: regression, spread, z-score, ADF test, correlations, etc.
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from pykalman import KalmanFilter
import logging
import warnings

# Suppress pandas RuntimeWarnings for NaN operations
warnings.filterwarnings('ignore', category=RuntimeWarning, module='pandas')

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Modular analytics engine for quantitative analysis.
    Each method is independent and can be extended easily.
    """
    
    @staticmethod
    def compute_price_stats(df: pd.DataFrame) -> Dict:
        """
        Compute basic price statistics.
        
        Args:
            df: DataFrame with 'price' or 'close' column
            
        Returns:
            Dictionary of statistics
        """
        if df.empty:
            return {}
        
        price_col = 'close' if 'close' in df.columns else 'price'
        prices = df[price_col]
        
        returns = prices.pct_change().dropna()
        
        return {
            'mean': float(prices.mean()),
            'std': float(prices.std()),
            'min': float(prices.min()),
            'max': float(prices.max()),
            'last': float(prices.iloc[-1]),
            'return_mean': float(returns.mean()) if len(returns) > 0 else 0,
            'return_std': float(returns.std()) if len(returns) > 0 else 0,
            'skew': float(returns.skew()) if len(returns) > 2 else 0,
            'kurtosis': float(returns.kurtosis()) if len(returns) > 3 else 0
        }
    
    @staticmethod
    def ols_regression(y: pd.Series, x: pd.Series) -> Dict:
        """
        Ordinary Least Squares regression.
        
        Args:
            y: Dependent variable (e.g., ETH price)
            x: Independent variable (e.g., BTC price)
            
        Returns:
            Dictionary with beta (hedge ratio), alpha, r_squared, residuals
        """
        if len(y) < 2 or len(x) < 2:
            return {'beta': 0, 'alpha': 0, 'r_squared': 0, 'residuals': None}
        
        # Align series
        df = pd.DataFrame({'y': y, 'x': x}).dropna()
        
        if len(df) < 2:
            return {'beta': 0, 'alpha': 0, 'r_squared': 0, 'residuals': None}
        
        y_vals = df['y'].values
        x_vals = df['x'].values
        
        # Compute regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
        
        # Residuals
        residuals = y_vals - (slope * x_vals + intercept)
        
        return {
            'beta': float(slope),
            'alpha': float(intercept),
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value),
            'std_err': float(std_err),
            'residuals': residuals
        }
    
    @staticmethod
    def robust_regression_huber(y: pd.Series, x: pd.Series) -> Dict:
        """
        Huber robust regression (less sensitive to outliers).
        
        Args:
            y: Dependent variable
            x: Independent variable
            
        Returns:
            Similar to OLS but with robust estimates
        """
        try:
            from sklearn.linear_model import HuberRegressor
            
            df = pd.DataFrame({'y': y, 'x': x}).dropna()
            
            if len(df) < 2:
                return {'beta': 0, 'alpha': 0, 'residuals': None}
            
            y_vals = df['y'].values.reshape(-1, 1)
            x_vals = df['x'].values.reshape(-1, 1)
            
            model = HuberRegressor()
            model.fit(x_vals, y_vals.ravel())
            
            predictions = model.predict(x_vals)
            residuals = y_vals.ravel() - predictions
            
            # R-squared
            ss_res = np.sum(residuals ** 2)
            ss_tot = np.sum((y_vals.ravel() - y_vals.mean()) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            return {
                'beta': float(model.coef_[0]),
                'alpha': float(model.intercept_),
                'r_squared': float(r_squared),
                'residuals': residuals
            }
        except Exception as e:
            logger.error(f"Huber regression error: {e}")
            return AnalyticsEngine.ols_regression(y, x)
    
    @staticmethod
    def compute_spread(price1: pd.Series, price2: pd.Series, hedge_ratio: float) -> pd.Series:
        """
        Compute spread between two series: spread = price1 - hedge_ratio * price2
        
        Args:
            price1: First price series
            price2: Second price series
            hedge_ratio: Hedge ratio (beta from regression)
            
        Returns:
            Spread series
        """
        df = pd.DataFrame({'p1': price1, 'p2': price2}).dropna()
        return df['p1'] - hedge_ratio * df['p2']
    
    @staticmethod
    def compute_zscore(series: pd.Series, window: int = 20) -> pd.Series:
        """
        Compute rolling z-score.
        
        Args:
            series: Input series (e.g., spread)
            window: Rolling window size
            
        Returns:
            Z-score series
        """
        import warnings
        
        if len(series) < window:
            return pd.Series(index=series.index, dtype=float)
        
        # Drop NaN values before calculation to avoid runtime warnings
        series_clean = series.dropna()
        if len(series_clean) < window:
            return pd.Series(index=series.index, dtype=float)
        
        # Suppress RuntimeWarning for invalid values in subtract
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            rolling_mean = series_clean.rolling(window=window).mean()
            rolling_std = series_clean.rolling(window=window).std()
            
            # Avoid division by zero
            rolling_std = rolling_std.replace(0, np.nan)
            
            zscore = (series_clean - rolling_mean) / rolling_std
            
        # Reindex to original series and fill NaN with 0
        return zscore.reindex(series.index).fillna(0)
    
    @staticmethod
    def adf_test(series: pd.Series) -> Dict:
        """
        Augmented Dickey-Fuller test for stationarity.
        
        Args:
            series: Time series to test
            
        Returns:
            Dictionary with test results
        """
        if len(series) < 10:
            return {'statistic': 0, 'pvalue': 1, 'is_stationary': False}
        
        try:
            series_clean = series.dropna()
            result = adfuller(series_clean, autolag='AIC')
            
            is_stationary = result[1] < 0.05  # p-value < 0.05
            
            return {
                'statistic': float(result[0]),
                'pvalue': float(result[1]),
                'usedlag': int(result[2]),
                'nobs': int(result[3]),
                'critical_values': {k: float(v) for k, v in result[4].items()},
                'is_stationary': bool(is_stationary)
            }
        except Exception as e:
            logger.error(f"ADF test error: {e}")
            return {'statistic': 0, 'pvalue': 1, 'is_stationary': False, 'error': str(e)}
    
    @staticmethod
    def rolling_correlation(series1: pd.Series, series2: pd.Series, window: int = 20) -> pd.Series:
        """
        Compute rolling correlation between two series.
        
        Args:
            series1: First series
            series2: Second series
            window: Rolling window
            
        Returns:
            Correlation series
        """
        df = pd.DataFrame({'s1': series1, 's2': series2})
        return df['s1'].rolling(window=window).corr(df['s2'])
    
    @staticmethod
    def kalman_hedge_ratio(price1: pd.Series, price2: pd.Series) -> Dict:
        """
        Dynamic hedge ratio estimation using Kalman Filter.
        More adaptive than static OLS for changing market conditions.
        
        Args:
            price1: First price series
            price2: Second price series
            
        Returns:
            Dictionary with hedge ratios and predictions
        """
        try:
            df = pd.DataFrame({'p1': price1, 'p2': price2}).dropna()
            
            if len(df) < 10:
                return {'hedge_ratios': None, 'observations': None}
            
            # State transition and observation matrices
            delta = 1e-5
            trans_cov = delta / (1 - delta) * np.eye(2)
            
            obs_mat = np.vstack([df['p2'].values, np.ones(len(df))]).T
            
            kf = KalmanFilter(
                n_dim_obs=1,
                n_dim_state=2,
                initial_state_mean=np.zeros(2),
                initial_state_covariance=np.ones((2, 2)),
                transition_matrices=np.eye(2),
                observation_matrices=obs_mat,
                observation_covariance=1.0,
                transition_covariance=trans_cov
            )
            
            state_means, state_covs = kf.filter(df['p1'].values)
            
            hedge_ratios = state_means[:, 0]
            intercepts = state_means[:, 1]
            
            return {
                'hedge_ratios': pd.Series(hedge_ratios, index=df.index),
                'intercepts': pd.Series(intercepts, index=df.index),
                'last_hedge_ratio': float(hedge_ratios[-1]),
                'last_intercept': float(intercepts[-1])
            }
        except Exception as e:
            logger.error(f"Kalman filter error: {e}")
            return {'hedge_ratios': None, 'observations': None}
    
    @staticmethod
    def half_life(series: pd.Series) -> float:
        """
        Compute mean reversion half-life using Ornstein-Uhlenbeck process.
        Useful for understanding how quickly spreads revert.
        
        Args:
            series: Spread or price series
            
        Returns:
            Half-life in time units (bars)
        """
        try:
            series_clean = series.dropna()
            
            if len(series_clean) < 10:
                return np.nan
            
            lagged = series_clean.shift(1).dropna()
            delta = series_clean.diff().dropna()
            
            # Align
            df = pd.DataFrame({'lagged': lagged, 'delta': delta}).dropna()
            
            if len(df) < 5:
                return np.nan
            
            # Regression: delta = lambda * lagged + noise
            regression = stats.linregress(df['lagged'].values, df['delta'].values)
            lambda_param = regression.slope
            
            if lambda_param >= 0:
                return np.nan
            
            half_life = -np.log(2) / lambda_param
            return float(half_life)
        except Exception as e:
            logger.error(f"Half-life computation error: {e}")
            return np.nan
    
    @staticmethod
    def liquidity_metrics(df: pd.DataFrame, window: int = 20) -> Dict:
        """
        Compute liquidity-related metrics.
        
        Args:
            df: DataFrame with volume/size data
            window: Rolling window
            
        Returns:
            Dictionary of liquidity metrics
        """
        if df.empty or 'volume' not in df.columns:
            return {}
        
        volume = df['volume']
        
        return {
            'avg_volume': float(volume.rolling(window).mean().iloc[-1]) if len(volume) >= window else 0,
            'volume_std': float(volume.rolling(window).std().iloc[-1]) if len(volume) >= window else 0,
            'last_volume': float(volume.iloc[-1]),
            'volume_trend': float(volume.rolling(window).mean().diff().iloc[-1]) if len(volume) >= window else 0
        }
    
    @staticmethod
    def vwap(df: pd.DataFrame) -> float:
        """
        Volume-Weighted Average Price.
        
        Args:
            df: DataFrame with 'price' and 'size' or 'volume' columns
            
        Returns:
            VWAP value
        """
        if df.empty:
            return 0
        
        price_col = 'close' if 'close' in df.columns else 'price'
        volume_col = 'volume' if 'volume' in df.columns else 'size'
        
        if price_col not in df.columns or volume_col not in df.columns:
            return 0
        
        total_volume = df[volume_col].sum()
        
        if total_volume == 0:
            return 0
        
        vwap = (df[price_col] * df[volume_col]).sum() / total_volume
        return float(vwap)
