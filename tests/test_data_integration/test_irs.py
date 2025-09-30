"""Tests for IRS SOI migration data loader."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from Claude45_Demo.data_integration.irs import IRSMigrationLoader


@pytest.fixture()
def migration_loader(tmp_path: Path) -> IRSMigrationLoader:
    """Create CSV fixtures for inflow and outflow data and return loader."""

    inflow = pd.DataFrame(
        [
            {
                "year": 2021,
                "state_fips": "08",
                "county_fips": "031",
                "returns": 120,
                "agi": 6_000_000,
            },
            {
                "year": 2021,
                "state_fips": "49",
                "county_fips": "035",
                "returns": 50,
                "agi": 2_000_000,
            },
            {
                "year": 2022,
                "state_fips": "08",
                "county_fips": "031",
                "returns": 150,
                "agi": 7_500_000,
            },
        ]
    )
    outflow = pd.DataFrame(
        [
            {
                "year": 2021,
                "state_fips": "08",
                "county_fips": "031",
                "returns": 80,
                "agi": 3_200_000,
            },
            {
                "year": 2022,
                "state_fips": "08",
                "county_fips": "031",
                "returns": 110,
                "agi": 5_500_000,
            },
            {
                "year": 2022,
                "state_fips": "08",
                "county_fips": "005",
                "returns": 40,
                "agi": 1_800_000,
            },
        ]
    )

    inflow_path = tmp_path / "migration_inflows.csv"
    outflow_path = tmp_path / "migration_outflows.csv"
    inflow.to_csv(inflow_path, index=False)
    outflow.to_csv(outflow_path, index=False)

    return IRSMigrationLoader(data_dir=tmp_path)


def test_load_county_migration_calculates_net_and_agi(
    migration_loader: IRSMigrationLoader,
) -> None:
    """Scenario: Net migration calculation."""

    result = migration_loader.load_county_migration(state_fips="08", county_fips="031")

    assert list(result["year"]) == [2021, 2022]

    first_year = result[result["year"] == 2021].iloc[0]
    assert first_year["inflow_returns"] == 120
    assert first_year["outflow_returns"] == 80
    assert first_year["net_migration"] == 40
    assert first_year["agi_per_net_migrant"] == pytest.approx(70_000, rel=1e-6)
    assert first_year["agi_per_inflow_return"] == pytest.approx(50_000)


def test_load_county_migration_handles_missing_records(
    migration_loader: IRSMigrationLoader,
) -> None:
    """Loader should return empty DataFrame when county has no records."""

    result = migration_loader.load_county_migration(state_fips="08", county_fips="999")
    assert result.empty
