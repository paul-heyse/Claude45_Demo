"""API client for backend communication."""

from typing import Any, Dict, List, Optional

import requests
import streamlit as st


class AkerAPIClient:
    """Client for Aker Investment Platform backend API."""

    def __init__(self, base_url: Optional[str] = None, api_token: Optional[str] = None):
        """Initialize API client.

        Args:
            base_url: Base URL for API (default: from secrets)
            api_token: Authentication token (default: from session state)
        """
        self.base_url = base_url or st.secrets.get("api", {}).get(
            "base_url", "http://localhost:8000"
        )
        self.api_token = api_token or st.session_state.get("api_token")
        self.timeout = st.secrets.get("api", {}).get("timeout", 30)

        self.session = requests.Session()
        if self.api_token:
            self.session.headers["Authorization"] = f"Bearer {self.api_token}"

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and errors.

        Args:
            response: HTTP response object

        Returns:
            Response data

        Raises:
            requests.HTTPError: On HTTP errors
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            st.error(f"API Error: {e}")
            raise
        except requests.JSONDecodeError:
            return response.text

    def screen_markets(
        self,
        search: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Screen markets with filters.

        Args:
            search: Search term for market name
            filters: Filter criteria dictionary
            limit: Maximum number of results

        Returns:
            List of market dictionaries
        """
        payload = {"search": search, "filters": filters or {}, "limit": limit}

        response = self.session.post(
            f"{self.base_url}/api/markets/screen", json=payload, timeout=self.timeout
        )
        return self._handle_response(response)

    def get_market_details(self, market_id: str) -> Dict:
        """Get detailed market information.

        Args:
            market_id: Market identifier

        Returns:
            Market details dictionary
        """
        response = self.session.get(
            f"{self.base_url}/api/markets/{market_id}", timeout=self.timeout
        )
        return self._handle_response(response)

    def get_portfolio(self) -> List[Dict]:
        """Get user's portfolio markets.

        Returns:
            List of portfolio market dictionaries
        """
        response = self.session.get(
            f"{self.base_url}/api/portfolio", timeout=self.timeout
        )
        return self._handle_response(response)

    def add_to_portfolio(
        self, market_id: str, notes: str = "", status: str = "prospect"
    ) -> Dict:
        """Add market to portfolio.

        Args:
            market_id: Market identifier
            notes: Optional notes
            status: Investment status (prospect, committed, active)

        Returns:
            Portfolio entry dictionary
        """
        payload = {"market_id": market_id, "notes": notes, "status": status}

        response = self.session.post(
            f"{self.base_url}/api/portfolio", json=payload, timeout=self.timeout
        )
        return self._handle_response(response)

    def remove_from_portfolio(self, market_id: str) -> Dict:
        """Remove market from portfolio.

        Args:
            market_id: Market identifier

        Returns:
            Success confirmation
        """
        response = self.session.delete(
            f"{self.base_url}/api/portfolio/{market_id}", timeout=self.timeout
        )
        return self._handle_response(response)

    def generate_report(
        self,
        market_ids: List[str],
        template: str = "market_analysis",
        format: str = "pdf",
    ) -> bytes:
        """Generate report for markets.

        Args:
            market_ids: List of market identifiers
            template: Report template name
            format: Output format (pdf, excel, html)

        Returns:
            Report file content as bytes
        """
        payload = {
            "market_ids": market_ids,
            "template": template,
            "format": format,
        }

        response = self.session.post(
            f"{self.base_url}/api/reports/generate", json=payload, timeout=60
        )
        return response.content

    def get_cache_stats(self) -> Dict:
        """Get cache statistics.

        Returns:
            Cache statistics dictionary
        """
        response = self.session.get(
            f"{self.base_url}/api/cache/stats", timeout=self.timeout
        )
        return self._handle_response(response)

    def warm_cache(
        self, markets: List[str], sources: Optional[List[str]] = None
    ) -> Dict:
        """Warm cache for markets.

        Args:
            markets: List of market names
            sources: Optional list of data sources to warm

        Returns:
            Warming results dictionary
        """
        payload = {
            "markets": markets,
            "sources": sources or ["census", "bls", "osm"],
        }

        response = self.session.post(
            f"{self.base_url}/api/cache/warm", json=payload, timeout=300
        )
        return self._handle_response(response)


@st.cache_resource
def get_api_client() -> AkerAPIClient:
    """Get singleton API client instance.

    Returns:
        Configured API client
    """
    return AkerAPIClient()
