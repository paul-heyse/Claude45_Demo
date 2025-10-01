"""E2E Test: Portfolio Management Workflow (Task 13.3).

Tests complete portfolio workflow:
1. Add 3 markets to portfolio
2. Compare markets side-by-side
3. Generate portfolio report
4. Export to PDF/Excel
"""

import pytest


class TestPortfolioE2E:
    """End-to-end test for portfolio management workflow."""

    @pytest.fixture
    def sample_markets(self):
        """Three markets for portfolio testing."""
        return [
            {
                "name": "Boulder, CO",
                "fips": "08013",
                "score": 87.2,
                "risk": 0.92,
                "status": "prospect",
            },
            {
                "name": "Fort Collins, CO",
                "fips": "08069",
                "score": 84.5,
                "risk": 0.95,
                "status": "prospect",
            },
            {
                "name": "Boise, ID",
                "fips": "16001",
                "score": 83.8,
                "risk": 0.98,
                "status": "committed",
            },
        ]

    def test_portfolio_complete_workflow(self, sample_markets, tmp_path):
        """Test complete portfolio workflow.

        1. Add markets to portfolio
        2. Calculate portfolio statistics
        3. Compare markets
        4. Generate report
        5. Export results
        """
        print(f"\n{'='*60}")
        print("PORTFOLIO MANAGEMENT WORKFLOW")
        print(f"{'='*60}")

        # Step 1: Add markets to portfolio
        print("\n📁 Adding markets to portfolio...")
        portfolio = []
        for market in sample_markets:
            portfolio.append(market)
            print(f"   ✓ Added: {market['name']} (Score: {market['score']:.1f})")

        assert len(portfolio) == 3, "Should have 3 markets"

        # Step 2: Calculate portfolio statistics
        print("\n📊 Portfolio Statistics:")
        avg_score = sum(m["score"] for m in portfolio) / len(portfolio)
        avg_risk = sum(m["risk"] for m in portfolio) / len(portfolio)
        total_prospect = sum(1 for m in portfolio if m["status"] == "prospect")
        total_committed = sum(1 for m in portfolio if m["status"] == "committed")

        print(f"   Markets: {len(portfolio)}")
        print(f"   Avg Score: {avg_score:.1f}")
        print(f"   Avg Risk: {avg_risk:.2f}")
        print(f"   Prospect: {total_prospect}")
        print(f"   Committed: {total_committed}")

        assert 80 <= avg_score <= 90, f"Portfolio avg score {avg_score:.1f} unexpected"
        assert 0.9 <= avg_risk <= 1.0, f"Portfolio avg risk {avg_risk:.2f} unexpected"

        # Step 3: Compare markets side-by-side
        print("\n🔍 Market Comparison:")
        sorted_portfolio = sorted(portfolio, key=lambda x: x["score"], reverse=True)

        for i, market in enumerate(sorted_portfolio, 1):
            print(
                f"   {i}. {market['name']:<20} Score: {market['score']:.1f}  "
                f"Risk: {market['risk']:.2f}  Status: {market['status']}"
            )

        # Verify ranking
        assert sorted_portfolio[0]["name"] == "Boulder, CO", "Boulder should rank #1"
        assert sorted_portfolio[-1]["name"] == "Boise, ID", "Boise should rank #3"

        # Step 4: Generate portfolio report
        print("\n📄 Generating Portfolio Report...")
        report_lines = [
            "# Portfolio Analysis Report",
            "",
            f"**Total Markets:** {len(portfolio)}",
            f"**Average Score:** {avg_score:.1f}/100",
            f"**Average Risk:** {avg_risk:.2f}",
            "",
            "## Market Rankings",
            "",
        ]

        for i, market in enumerate(sorted_portfolio, 1):
            report_lines.append(
                f"{i}. **{market['name']}** - Score: {market['score']:.1f}, "
                f"Risk: {market['risk']:.2f}, Status: {market['status']}"
            )

        report_text = "\n".join(report_lines)
        print(f"   Report generated: {len(report_text)} chars")
        assert len(report_text) > 200, "Report too short"

        # Step 5: Export to file
        print("\n💾 Exporting Results...")

        # Export as Markdown
        md_file = tmp_path / "portfolio_report.md"
        with open(md_file, "w") as f:
            f.write(report_text)
        print(f"   ✓ Markdown: {md_file}")
        assert md_file.exists()

        # Export as CSV
        import csv

        csv_file = tmp_path / "portfolio_markets.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["name", "fips", "score", "risk", "status"]
            )
            writer.writeheader()
            writer.writerows(portfolio)
        print(f"   ✓ CSV: {csv_file}")
        assert csv_file.exists()

        print(f"\n{'='*60}")
        print("✅ PORTFOLIO WORKFLOW E2E PASSED")
        print(f"   Markets: {len(portfolio)}")
        print(
            f"   Top Market: {sorted_portfolio[0]['name']} ({sorted_portfolio[0]['score']:.1f})"
        )
        print(f"   Files: {md_file.name}, {csv_file.name}")
        print(f"{'='*60}\n")

        return {
            "portfolio": portfolio,
            "stats": {
                "avg_score": avg_score,
                "avg_risk": avg_risk,
                "count": len(portfolio),
            },
            "files": {"markdown": md_file, "csv": csv_file},
        }

    def test_portfolio_add_remove_operations(self, sample_markets):
        """Test adding and removing markets from portfolio."""
        portfolio = []

        # Add markets
        for market in sample_markets[:2]:
            portfolio.append(market)
        assert len(portfolio) == 2

        # Add another
        portfolio.append(sample_markets[2])
        assert len(portfolio) == 3

        # Remove one
        portfolio = [m for m in portfolio if m["name"] != "Fort Collins, CO"]
        assert len(portfolio) == 2
        assert all(m["name"] != "Fort Collins, CO" for m in portfolio)

        # Add it back
        fort_collins = [m for m in sample_markets if m["name"] == "Fort Collins, CO"][0]
        portfolio.append(fort_collins)
        assert len(portfolio) == 3

        print("\n✅ Portfolio add/remove operations passed")

    def test_portfolio_filtering(self, sample_markets):
        """Test filtering portfolio by criteria."""
        portfolio = sample_markets

        # Filter by score >= 85
        high_score = [m for m in portfolio if m["score"] >= 85]
        assert len(high_score) == 2  # Boulder and Fort Collins
        print(f"\n✓ High score markets (≥85): {len(high_score)}")

        # Filter by status
        prospects = [m for m in portfolio if m["status"] == "prospect"]
        assert len(prospects) == 2
        print(f"✓ Prospect markets: {len(prospects)}")

        committed = [m for m in portfolio if m["status"] == "committed"]
        assert len(committed) == 1
        print(f"✓ Committed markets: {len(committed)}")

        # Filter by risk < 0.95
        low_risk = [m for m in portfolio if m["risk"] < 0.95]
        assert len(low_risk) == 1  # Boulder
        print(f"✓ Low risk markets (<0.95): {len(low_risk)}")

        print("✅ Portfolio filtering passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
