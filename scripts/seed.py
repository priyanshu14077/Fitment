"""Rebuild the catalog in the local database from data/vpic_snapshot.json.

    uv run --project api python scripts/seed.py

Generation and SQL live in the API package (fitment.seed, fitment.repo.seed)
so the tests can import them. ADR 0022.
"""

from fitment.seed import main

if __name__ == "__main__":
    main()
