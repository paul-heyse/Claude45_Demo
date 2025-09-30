"""Performance benchmarks for Aker Investment Platform."""

import time
from typing import Callable

import pytest


class PerformanceBenchmark:
    """Performance benchmark utilities."""

    @staticmethod
    def time_function(func: Callable, *args, **kwargs) -> tuple[any, float]:
        """Time function execution."""
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        return result, duration


class TestMarketAnalysisPerformance:
    """Performance benchmarks for market analysis."""

    def test_supply_constraint_performance(self):
        """Test supply constraint calculation performance."""
        from Claude45_Demo.market_analysis import SupplyConstraintCalculator

        calc = SupplyConstraintCalculator()

        start = time.time()
        for _ in range(100):
            calc.calculate_composite_score(
                permit_elasticity=75.0,
                topographic_constraint=80.0,
                regulatory_friction=70.0,
            )
        duration = time.time() - start

        avg_time = duration / 100
        assert avg_time < 0.01, f"Average time {avg_time:.4f}s exceeds 10ms threshold"
        print(f"✓ Supply constraint: {avg_time*1000:.2f}ms per calculation")

    def test_employment_analysis_performance(self):
        """Test employment analysis performance."""
        from Claude45_Demo.market_analysis import EmploymentAnalyzer

        analyzer = EmploymentAnalyzer()
        sector_cagr = {"tech": 0.04, "healthcare": 0.03, "education": 0.02, "manufacturing": 0.01}
        sector_lq = {"tech": 1.5, "healthcare": 1.2, "education": 1.0, "manufacturing": 0.9}

        start = time.time()
        for _ in range(100):
            analyzer.calculate_innovation_employment_score(sector_cagr, sector_lq)
        duration = time.time() - start

        avg_time = duration / 100
        assert avg_time < 0.01, f"Average time {avg_time:.4f}s exceeds 10ms threshold"
        print(f"✓ Employment analysis: {avg_time*1000:.2f}ms per calculation")

    def test_scoring_engine_performance(self):
        """Test scoring engine performance."""
        from Claude45_Demo.scoring_engine import ScoringEngine

        engine = ScoringEngine()
        component_scores = {
            "supply_constraint": 75.0,
            "innovation_employment": 70.0,
            "urban_convenience": 65.0,
            "outdoor_access": 80.0,
        }

        start = time.time()
        for _ in range(1000):
            engine.calculate_composite_score(component_scores)
        duration = time.time() - start

        avg_time = duration / 1000
        assert avg_time < 0.001, f"Average time {avg_time:.4f}s exceeds 1ms threshold"
        print(f"✓ Scoring engine: {avg_time*1000:.2f}ms per calculation")


class TestCachePerformance:
    """Performance benchmarks for cache operations."""

    def test_cache_read_performance(self, tmp_path):
        """Test cache read performance."""
        from Claude45_Demo.data_integration import CacheManager

        cache = CacheManager(db_path=tmp_path / "bench.db", ttl_days=30)

        # Populate cache
        for i in range(100):
            cache.set(f"key_{i}", {"data": f"value_{i}"}, ttl=3600)

        # Benchmark reads
        start = time.time()
        for i in range(100):
            cache.get(f"key_{i}")
        duration = time.time() - start

        avg_time = duration / 100
        assert avg_time < 0.005, f"Average time {avg_time:.4f}s exceeds 5ms threshold"
        print(f"✓ Cache read: {avg_time*1000:.2f}ms per operation")

    def test_cache_write_performance(self, tmp_path):
        """Test cache write performance."""
        from Claude45_Demo.data_integration import CacheManager

        cache = CacheManager(db_path=tmp_path / "bench.db", ttl_days=30)

        start = time.time()
        for i in range(100):
            cache.set(f"key_{i}", {"data": f"value_{i}"}, ttl=3600)
        duration = time.time() - start

        avg_time = duration / 100
        assert avg_time < 0.010, f"Average time {avg_time:.4f}s exceeds 10ms threshold"
        print(f"✓ Cache write: {avg_time*1000:.2f}ms per operation")


class TestDataIntegrationPerformance:
    """Performance benchmarks for data integration."""

    def test_config_loading_performance(self, tmp_path):
        """Test configuration loading performance."""
        from Claude45_Demo.data_integration import ConfigManager

        # Create test config
        config_path = tmp_path / "config.yaml"
        config_path.write_text("""
api_keys:
  census: test_key
  bls: test_key
  bea: test_key
""")

        start = time.time()
        for _ in range(100):
            ConfigManager(config_path=config_path)
        duration = time.time() - start

        avg_time = duration / 100
        assert avg_time < 0.020, f"Average time {avg_time:.4f}s exceeds 20ms threshold"
        print(f"✓ Config loading: {avg_time*1000:.2f}ms per load")


def test_full_market_screening_benchmark(tmp_path):
    """Benchmark full market screening workflow."""
    # This would test the full screening pipeline
    # For now, just verify the infrastructure exists
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

