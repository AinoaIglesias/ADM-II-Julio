from abc import ABC, abstractmethod
import pandas as pd
from typing import Any, Dict

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import (mean_squared_error, r2_score,
                             accuracy_score, confusion_matrix,
                             silhouette_score)


class IModelStrategy(ABC):
    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        """
        entrena el modelo con características X y target y.
        """
        ...

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Predice sobre nuevas etiquetas a partir de X.
        """
        ...

    @abstractmethod
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        calcula métricas (por ejemplo, error cuadrático medio, R², accuracy, matriz de confusión, silhouette) comparando las predicciones con y
        """
        ...



class BasePipelineModel(IModelStrategy):
    """
    Base class for sklearn pipelines. Builds a pipeline with preprocessing,
    estimator, and optional grid search.
    Si indicas un diccionario de hiperparámetros (por ejemplo {'estimator__n_estimators': [50,100]}) y use_grid_search=True, entonces el pipeline usará GridSearchCV 
    para probar todas las combinaciones y quedará con la mejor
    """
    def __init__(self, estimator, param_grid: Dict[str, Any] = None,
                 preprocess_config: Dict[str, Any] = None,    # qué columnas numéricas / categóricas preprocesar
                 use_grid_search: bool = False, cv: int = 5, scoring: str = None):
        self.estimator = estimator     # cualquier objeto de scikit-learn (p.ej. RandomForestRegressor)
        self.param_grid = param_grid or {}    # rango de hiperparámetros para GridSearchCV
        self.use_grid_search = use_grid_search and bool(self.param_grid)
        self.cv = cv
        self.scoring = scoring

        # Build preprocessing transformer if config given
        if preprocess_config:
            numeric_cols = preprocess_config.get("numeric", [])
            categorical_cols = preprocess_config.get("categorical", [])
            transformers = []
            if numeric_cols:
                transformers.append(("num", StandardScaler(), numeric_cols))
            if categorical_cols:
                transformers.append(("cat", OneHotEncoder(handle_unknown='ignore'), categorical_cols))
            self.preprocessor = ColumnTransformer(transformers)
        else:
            self.preprocessor = None

        self.pipeline = self._build_pipeline()

    def _build_pipeline(self):
        steps = []
        if self.preprocessor:
            steps.append(("preproc", self.preprocessor))
        steps.append(("estimator", self.estimator))
        pipeline = Pipeline(steps)

        if self.use_grid_search:
            return GridSearchCV(pipeline, self.param_grid,
                                cv=self.cv, scoring=self.scoring,
                                n_jobs=-1)
        return pipeline

    def fit(self, X: pd.DataFrame, y: pd.Series = None):  #Cualquier modelo de scikit-learn: p.ej. RandomForestRegressor(), SVC(), LogisticRegression(), etc
        #Entrena todo el pipeline. Si hay GridSearchCV, buscará la mejor combinación de parámetros.
        self.pipeline.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> pd.Series:
        #Aplica transformaciones y produce una serie de predicciones alineada con el índice de X
        preds = self.pipeline.predict(X)
        return pd.Series(preds, index=X.index)

    def evaluate(self, X: pd.DataFrame, y: pd.Series = None) -> Dict[str, Any]:
        # detecta si la variable y es numérica (regresión) o no (clasificación) y devuelve las métricas adecuadas, junto a los best_params_ si hubo grid search.
        y_pred = self.predict(X)
        results = {}
        if hasattr(self.pipeline, 'best_params_'):
            results['best_params'] = self.pipeline.best_params_

        # Regression metrics
        if y is not None and y.dtype.kind in 'if':
            results['mse'] = mean_squared_error(y, y_pred)
            results['r2'] = r2_score(y, y_pred)

        # Classification metrics
        if y is not None and y.dtype.kind not in 'if':
            results['accuracy'] = accuracy_score(y, y_pred)
            results['confusion_matrix'] = confusion_matrix(y, y_pred).tolist()

        return results


