import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Data Analysis Example: Sales Performance Analysis
class SalesAnalyzer:
    def __init__(self, data_file=None):
        """Initialize the Sales Analyzer with optional data file"""
        if data_file:
            self.df = pd.read_csv(data_file)
        else:
            # Generate sample data for demonstration
            self.df = self.generate_sample_data()
    
    def generate_sample_data(self):
        """Generate sample sales data for demonstration"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=365, freq='D')
        
        data = {
            'date': dates,
            'product': np.random.choice(['Product A', 'Product B', 'Product C'], 365),
            'sales': np.random.normal(1000, 200, 365),
            'marketing_spend': np.random.normal(100, 30, 365),
            'temperature': np.random.normal(20, 10, 365),
            'region': np.random.choice(['North', 'South', 'East', 'West'], 365)
        }
        
        df = pd.DataFrame(data)
        # Add some correlation between marketing spend and sales
        df['sales'] = df['sales'] + df['marketing_spend'] * 2 + np.random.normal(0, 50, 365)
        df['sales'] = np.maximum(df['sales'], 0)  # Ensure no negative sales
        
        return df
    
    def basic_statistics(self):
        """Generate basic statistical summary"""
        print("=== BASIC STATISTICS ===")
        print(self.df.describe())
        print(f"\nDataset shape: {self.df.shape}")
        print(f"Missing values:\n{self.df.isnull().sum()}")
        
        return self.df.describe()
    
    def analyze_by_product(self):
        """Analyze sales performance by product"""
        print("\n=== PRODUCT ANALYSIS ===")
        product_stats = self.df.groupby('product').agg({
            'sales': ['mean', 'sum', 'std', 'count'],
            'marketing_spend': 'mean'
        }).round(2)
        
        print(product_stats)
        
        # Find best and worst performing products
        avg_sales = self.df.groupby('product')['sales'].mean()
        best_product = avg_sales.idxmax()
        worst_product = avg_sales.idxmin()
        
        print(f"\nBest performing product: {best_product} (${avg_sales[best_product]:.2f} avg)")
        print(f"Worst performing product: {worst_product} (${avg_sales[worst_product]:.2f} avg)")
        
        return product_stats
    
    def time_series_analysis(self):
        """Analyze sales trends over time"""
        print("\n=== TIME SERIES ANALYSIS ===")
        
        # Convert date to datetime if not already
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Create monthly aggregations
        monthly_sales = self.df.groupby(self.df['date'].dt.to_period('M'))['sales'].sum()
        
        print("Monthly sales totals:")
        print(monthly_sales.head(10))
        
        # Calculate month-over-month growth
        monthly_growth = monthly_sales.pct_change() * 100
        print(f"\nAverage monthly growth rate: {monthly_growth.mean():.2f}%")
        
        return monthly_sales, monthly_growth
    
    def correlation_analysis(self):
        """Analyze correlations between variables"""
        print("\n=== CORRELATION ANALYSIS ===")
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        correlation_matrix = self.df[numeric_cols].corr()
        
        print("Correlation Matrix:")
        print(correlation_matrix.round(3))
        
        # Find strongest correlations with sales
        sales_correlations = correlation_matrix['sales'].drop('sales').abs().sort_values(ascending=False)
        print(f"\nStrongest correlations with sales:")
        for var, corr in sales_correlations.items():
            print(f"{var}: {corr:.3f}")
        
        return correlation_matrix
    
    def predictive_model(self):
        """Build a simple predictive model for sales"""
        print("\n=== PREDICTIVE MODELING ===")
        
        # Prepare features for modeling
        features = ['marketing_spend', 'temperature']
        X = self.df[features]
        y = self.df['sales']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Evaluate model
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model Performance:")
        print(f"R² Score: {r2:.3f}")
        print(f"Mean Squared Error: {mse:.2f}")
        print(f"Root Mean Squared Error: {np.sqrt(mse):.2f}")
        
        # Show feature importance
        print(f"\nFeature Coefficients:")
        for feature, coef in zip(features, model.coef_):
            print(f"{feature}: {coef:.2f}")
        
        return model, r2, mse
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("=" * 50)
        print("COMPREHENSIVE SALES ANALYSIS REPORT")
        print("=" * 50)
        
        # Run all analyses
        basic_stats = self.basic_statistics()
        product_analysis = self.analyze_by_product()
        monthly_sales, growth = self.time_series_analysis()
        correlations = self.correlation_analysis()
        model, r2, mse = self.predictive_model()
        
        # Summary insights
        print("\n=== KEY INSIGHTS ===")
        total_sales = self.df['sales'].sum()
        avg_daily_sales = self.df['sales'].mean()
        
        print(f"• Total sales: ${total_sales:,.2f}")
        print(f"• Average daily sales: ${avg_daily_sales:.2f}")
        print(f"• Marketing ROI: {(self.df['sales'].sum() / self.df['marketing_spend'].sum()):.2f}x")
        print(f"• Sales prediction accuracy (R²): {r2:.3f}")
        
        return {
            'total_sales': total_sales,
            'avg_daily_sales': avg_daily_sales,
            'model_accuracy': r2,
            'best_product': self.df.groupby('product')['sales'].mean().idxmax()
        }

# Example usage
if __name__ == "__main__":
    # Initialize analyzer with sample data
    analyzer = SalesAnalyzer()
    
    # Generate comprehensive report
    results = analyzer.generate_report()
    
    # Optional: Save results to file
    # analyzer.df.to_csv('analyzed_sales_data.csv', index=False)
    
    print(f"\nAnalysis complete! Key result: Best product is {results['best_product']}")

