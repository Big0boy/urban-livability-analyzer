from src import LivabilityAnalyzer, AnalysisConfig

config = AnalysisConfig(cities=["Bhopal, India"], num_samples=100)
analyzer = LivabilityAnalyzer(config)
analyzer.run()
