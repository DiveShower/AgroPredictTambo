"""Pruebas de concurrencia multi-hilo para InMemorySectorRepository."""

import threading
from concurrent.futures import ThreadPoolExecutor

from src.domain.entities.sector import Sector
from src.infrastructure.repositories.in_memory_sector_repo import (
    InMemorySectorRepository,
)


def _worker(
    repo: InMemorySectorRepository,
    barrier: threading.Barrier,
    worker_id: int,
    iterations: int,
) -> list[Sector]:
    barrier.wait(timeout=5.0)
    results: list[Sector] = []
    for step in range(iterations):
        is_occupied = (worker_id + step) % 2 == 0
        updated = repo.update_occupancy("corral_espera", is_occupied)
        assert isinstance(updated, Sector)
        assert updated.sector_id == "corral_espera"
        assert isinstance(updated.current_occupancy, bool)
        sectors = repo.get_all_sectors()
        assert len(sectors) == 3
        assert all(isinstance(sec, Sector) for sec in sectors)
        results.append(updated)
    return results


def test_in_memory_sector_repo_concurrent_toggle() -> None:
    """Verifica atomicidad sin excepciones con 10 hilos alternando ocupación."""
    repo = InMemorySectorRepository()
    thread_count = 10
    iterations = 40
    barrier = threading.Barrier(thread_count)

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [
            executor.submit(_worker, repo, barrier, idx, iterations)
            for idx in range(thread_count)
        ]
        all_results = [fut.result(timeout=10.0) for fut in futures]

    assert len(all_results) == thread_count
    assert all(len(batch) == iterations for batch in all_results)
    for expected in (False, True):
        updated = repo.update_occupancy("corral_espera", expected)
        assert isinstance(updated, Sector)
        assert updated.current_occupancy is expected
        corral = next(
            s for s in repo.get_all_sectors() if s.sector_id == "corral_espera"
        )
        assert corral.current_occupancy is expected
