import numpy as np, random, os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml, make_moons
from sklearn.model_selection import train_test_split, learning_curve, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression
from sklearn.svm import SVR, SVC
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import classification_report, confusion_matrix, RocCurveDisplay, mean_absolute_error, mean_squared_error, r2_score
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.inspection import PartialDependenceDisplay
from sklearn.base import BaseEstimator, TransformerMixin
from skopt import BayesSearchCV
import joblib

# Setup
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
random.seed(RANDOM_STATE)
os.environ['PYTHONHASHSEED'] = str(RANDOM_STATE)
IMAGE_DIR = '/Users/grey/work/cloudmesh-ai-lecture/docs/section/ai/skit-learn/images/scikit-learn-example/'

# The dataset uses 'class' as the target column name instead of 'quality'
TARGET_COL = 'class'

def save_fig(name):
    plt.savefig(f'{IMAGE_DIR}{name}')
    plt.close()

print("--- Data Loading ---")
wine = fetch_openml(name='wine-quality-red', version=1, as_frame=True)
df = wine.frame
# Ensure target is numeric
df[TARGET_COL] = pd.to_numeric(df[TARGET_COL])
print(df.head())

print("\n--- Figure 1: Distribution ---")
sns.histplot(df[TARGET_COL], kde=True, bins=10, color='steelblue')
plt.title('Distribution of Wine Quality Scores')
plt.xlabel('Quality (0-10)')
save_fig('figure_1_distribution.png')
print("Saved figure_1_distribution.png")

print("\n--- Figure 2: Correlation ---")
plt.figure(figsize=(10,8))
corr = df.corr()
sns.heatmap(corr, cmap='coolwarm', annot=True, fmt=".2f")
plt.title('Feature Correlation Matrix')
save_fig('figure_2_correlation.png')
print("Saved figure_2_correlation.png")

print("\n--- Preprocessing ---")
X = df.drop(TARGET_COL, axis=1)
y = df[TARGET_COL]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)

numeric_features = X.select_dtypes(include=['float64', 'int64']).columns
preprocess = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features)
    ], remainder='passthrough'
)

pipeline = Pipeline(steps=[
    ('preprocess', preprocess),
    ('regressor', LinearRegression())
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)

print("\n--- Figure 3: Residuals ---")
residuals = y_test - y_pred
sns.scatterplot(x=y_pred, y=residuals, alpha=0.6)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel('Predicted Quality')
plt.ylabel('Residual (Actual - Predicted)')
plt.title('Residual Plot – Linear Regression')
save_fig('figure_3_residuals.png')
print("Saved figure_3_residuals.png")

print("\n--- Ridge Regression ---")
ridge_pipe = Pipeline([
    ('preprocess', preprocess),
    ('ridge', Ridge(alpha=1.0))
])
ridge_pipe.fit(X_train, y_train)
print('R² on test set:', ridge_pipe.score(X_test, y_test))

print("\n--- Figure 4: Learning Curve ---")
train_sizes, train_scores, test_scores = learning_curve(
    ridge_pipe, X, y, cv=5, scoring='r2',
    train_sizes=np.linspace(.1, 1.0, 5), random_state=RANDOM_STATE
)
plt.plot(train_sizes, np.mean(train_scores, axis=1), 'o-', label='Train')
plt.plot(train_sizes, np.mean(test_scores, axis=1), 's-', label='Cross-val')
plt.xlabel('Training Set Size')
plt.ylabel('R²')
plt.title('Learning Curve – Ridge Regression')
plt.legend()
save_fig('figure_4_learning_curve.png')
print("Saved figure_4_learning_curve.png")

print("\n--- SVR ---")
svr_pipe = Pipeline([
    ('preprocess', preprocess),
    ('svr', SVR(C=10, kernel='rbf', gamma='scale'))
])
svr_pipe.fit(X_train, y_train)
print('SVR R²:', svr_pipe.score(X_test, y_test))

print("\n--- Figure 5: SVC Decision Boundary ---")
X_moon, y_moon = make_moons(noise=0.2, random_state=RANDOM_STATE)
svc = Pipeline([
    ('scale', StandardScaler()),
    ('svc', SVC(kernel='rbf', C=1.0, gamma='auto'))
])
svc.fit(X_moon, y_moon)
xx, yy = np.meshgrid(np.linspace(-1.5, 2.5, 300),
                     np.linspace(-1.0, 1.5, 300))
Z = svc.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
plt.contourf(xx, yy, Z, alpha=0.3, cmap='coolwarm')
plt.scatter(X_moon[:,0], X_moon[:,1], c=y_moon, edgecolor='k')
plt.title('SVC Decision Boundary on make_moons')
save_fig('figure_5_svc_boundary.png')
print("Saved figure_5_svc_boundary.png")

print("\n--- Random Forest (Classification) ---")
y_bin = (y >= 7).astype(int)
X_train_bin, X_test_bin, y_train_bin, y_test_bin = train_test_split(
    X, y_bin, test_size=0.2, random_state=RANDOM_STATE, stratify=y_bin
)

rf_pipe = Pipeline([
    ('preprocess', preprocess),
    ('rf', RandomForestClassifier(
        n_estimators=300,
        max_depth=7,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
        n_jobs=-1
    ))
])
rf_pipe.fit(X_train_bin, y_train_bin)
print('Test accuracy:', rf_pipe.score(X_test_bin, y_test_bin))

print("\n--- Figure 6: Feature Importances ---")
importances = rf_pipe.named_steps['rf'].feature_importances_
feat_names = preprocess.transformers_[0][2]
sorted_idx = np.argsort(importances)[::-1]
plt.figure(figsize=(8,5))
sns.barplot(x=importances[sorted_idx], y=np.array(feat_names)[sorted_idx], palette='viridis')
plt.title('Random Forest – Feature Importances')
plt.xlabel('Mean Decrease in Impurity')
save_fig('figure_6_feature_importance.png')
print("Saved figure_6_feature_importance.png")

print("\n--- Gradient Boosting ---")
gbr_pipe = Pipeline([
    ('preprocess', preprocess),
    ('gbr', GradientBoostingRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=4,
        random_state=RANDOM_STATE
    ))
])
gbr_pipe.fit(X_train, y_train)
print('GBR R²:', gbr_pipe.score(X_test, y_test))

print("\n--- Figure 7: PDP ---")
PartialDependenceDisplay.from_estimator(
    gbr_pipe, X_test, ['alcohol'],
    kind='average', grid_resolution=50
)
plt.title('Partial Dependence of Quality on Alcohol')
save_fig('figure_7_pdp.png')
print("Saved figure_7_pdp.png")

print("\n--- Figure 8: K-Means PCA ---")
pca = PCA(n_components=2, random_state=RANDOM_STATE)
X_pca = pca.fit_transform(preprocess.fit_transform(X))
kmeans = KMeans(n_clusters=3, random_state=RANDOM_STATE, n_init='auto')
labels = kmeans.fit_predict(X_pca)
plt.figure(figsize=(7,5))
sns.scatterplot(x=X_pca[:,0], y=X_pca[:,1], hue=labels, palette='deep', s=60, edgecolor='k')
plt.title('K-Means (k=3) on PCA-reduced Wine Data')
plt.xlabel('PC1'); plt.ylabel('PC2')
plt.legend(title='Cluster')
save_fig('figure_8_kmeans.png')
print("Saved figure_8_kmeans.png")

print("\n--- Figure 9: t-SNE ---")
tsne = TSNE(n_components=2, perplexity=30, learning_rate=200,
            random_state=RANDOM_STATE, init='pca')
X_tsne = tsne.fit_transform(preprocess.fit_transform(X))
plt.figure(figsize=(7,5))
sns.scatterplot(x=X_tsne[:,0], y=X_tsne[:,1], hue=y, palette='coolwarm', s=40, legend=False)
plt.title('t-SNE Embedding of Wine Features coloured by Quality')
save_fig('figure_9_tsne.png')
print("Saved figure_9_tsne.png")

print("\n--- Cross-Validation ---")
rf = RandomForestClassifier(
    n_estimators=200, max_depth=6, random_state=RANDOM_STATE, n_jobs=-1
)
scores = cross_val_score(
    rf, preprocess.fit_transform(X), y_bin,
    cv=5, scoring='accuracy'
)
print('Cross-validated accuracy: %.3f ± %.3f' % (scores.mean(), scores.std()))

print("\n--- Classification Metrics ---")
rf_pipe.fit(X_train_bin, y_train_bin)
y_pred_bin = rf_pipe.predict(X_test_bin)
print(classification_report(y_test_bin, y_pred_bin, target_names=['Bad','Good']))

print("\n--- Figure 10: Confusion Matrix ---")
cm = confusion_matrix(y_test_bin, y_pred_bin)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Bad','Good'], yticklabels=['Bad','Good'])
plt.xlabel('Predicted'); plt.ylabel('Actual')
plt.title('Confusion Matrix – Random Forest')
save_fig('figure_10_confusion_matrix.png')
print("Saved figure_10_confusion_matrix.png")

print("\n--- Figure 11: ROC Curve ---")
y_proba = rf_pipe.predict_proba(X_test_bin)[:,1]
RocCurveDisplay.from_predictions(y_test_bin, y_proba)
plt.title('ROC Curve – Random Forest')
save_fig('figure_11_roc_curve.png')
print("Saved figure_11_roc_curve.png")

print("\n--- Regression Metrics ---")
y_pred_gbr = gbr_pipe.predict(X_test)
print('MAE:', mean_absolute_error(y_test, y_pred_gbr))
print('RMSE:', np.sqrt(mean_squared_error(y_test, y_pred_gbr)))
print('R²:', r2_score(y_test, y_pred_gbr))

print("\n--- Grid Search ---")
param_grid = {
    'rf__n_estimators': [200, 500],
    'rf__max_depth': [5, 7, None],
    'rf__min_samples_leaf': [1, 3, 5]
}
grid = GridSearchCV(
    estimator=rf_pipe,
    param_grid=param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=0
)
grid.fit(X_train_bin, y_train_bin)
print('Best params:', grid.best_params_)
print('Best CV accuracy:', grid.best_score_)

print("\n--- Randomized Search ---")
from scipy.stats import randint
param_dist = {
    'rf__n_estimators': randint(200, 1000),
    'rf__max_depth': randint(3, 15),
    'rf__min_samples_leaf': randint(1, 8)
}
rand_search = RandomizedSearchCV(
    estimator=rf_pipe,
    param_distributions=param_dist,
    n_iter=10, # Reduced for speed in this demo
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    random_state=RANDOM_STATE,
    verbose=0
)
rand_search.fit(X_train_bin, y_train_bin)
print('Best randomised params:', rand_search.best_params_)

print("\n--- Bayesian Optimisation ---")
bayes = BayesSearchCV(
    estimator=rf_pipe,
    search_spaces={
        'rf__n_estimators': (200, 800),
        'rf__max_depth': (3, 15),
        'rf__min_samples_leaf': (1, 10)
    },
    n_iter=10, # Reduced for speed
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    random_state=RANDOM_STATE
)
bayes.fit(X_train_bin, y_train_bin)
print('Bayes best params:', bayes.best_params_)

print("\n--- Custom Transformer ---")
class RatioFeature(BaseEstimator, TransformerMixin):
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator
    def fit(self, X, y=None):
        self.num_idx_ = X.columns.get_loc(self.numerator)
        self.den_idx_ = X.columns.get_loc(self.denominator)
        return self
    def transform(self, X):
        # Use .values to avoid index misalignment and handle NaNs/Infs
        num = X.iloc[:, self.num_idx_].values
        den = X.iloc[:, self.den_idx_].values
        # Avoid division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            ratio = num / den
        ratio = np.nan_to_num(ratio, nan=0.0, posinf=0.0, neginf=0.0)

        ratio_df = pd.DataFrame(ratio, columns=[f'{self.numerator}_to_{self.denominator}'], index=X.index)
        return pd.concat([X, ratio_df], axis=1)

ratio_pipe = Pipeline([
    ('ratio', RatioFeature('alcohol', 'density')),
    ('scale', StandardScaler()),
    ('clf', LogisticRegression(max_iter=500, random_state=RANDOM_STATE))
])
ratio_pipe.fit(X_train_bin, y_train_bin)
print('RatioPipe accuracy:', ratio_pipe.score(X_test_bin, y_test_bin))

print("\n--- Model Persistence ---")
joblib.dump(gbr_pipe, 'gbr_wine_model.joblib')
model_loaded = joblib.load('gbr_wine_model.joblib')
print('Model persisted and loaded successfully.')

print("\n--- Assignment Solution ---")
X_train_as, X_test_as, y_train_as, y_test_as = train_test_split(
    X, y, test_size=.2, random_state=42, stratify=y.astype(int)
)
numeric_cols = X.select_dtypes(include=['float64', 'int64']).columns
preprocess_as = ColumnTransformer([('num', StandardScaler(), numeric_cols)])
gbr_pipe_as = Pipeline([
    ('preprocess', preprocess_as),
    ('gbr', GradientBoostingRegressor(random_state=42))
])
param_grid_as = {
    'gbr__n_estimators': [300, 500],
    'gbr__learning_rate': [0.05, 0.1],
    'gbr__max_depth': [3, 4]
}
grid_as = GridSearchCV(gbr_pipe_as, param_grid_as, cv=5, scoring='neg_root_mean_squared_error', n_jobs=-1)
grid_as.fit(X_train_as, y_train_as)
print('Best RMSE (negative):', grid_as.best_score_)
print('Best hyper-params:', grid_as.best_params_)
best_model_as = grid_as.best_estimator_
y_pred_as = best_model_as.predict(X_test_as)
print('Test MAE  :', mean_absolute_error(y_test_as, y_pred_as))
print('Test RMSE :', np.sqrt(((y_test_as - y_pred_as)**2).mean()))
print('Test R²   :', r2_score(y_test_as, y_pred_as))

plt.figure(figsize=(6,5))
sns.scatterplot(x=y_test_as, y=y_pred_as, alpha=0.6)
plt.plot([y_test_as.min(), y_test_as.max()], [y_test_as.min(), y_test_as.max()], '--r')
plt.xlabel('Actual Quality')
plt.ylabel('Predicted Quality')
plt.title('Actual vs. Predicted – Gradient Boosting')
save_fig('figure_12_actual_vs_predicted.png')
print("Saved figure_12_actual_vs_predicted.png")
