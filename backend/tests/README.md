# Backend Tests

This directory contains test files for the backend application.

## Test Files

### `test_db_queries.py`
Tests basic database queries to ensure they work without hanging.
- **Purpose**: Verify database connectivity and query performance
- **Usage**: `python tests/test_db_queries.py`

### `test_performance.py`
Tests API endpoint performance improvements.
- **Purpose**: Measure response times and verify optimizations
- **Usage**: `python tests/test_performance.py`
- **Requirements**: FastAPI server must be running on localhost:8000

### `create_indexes.py`
Creates database indexes for better query performance.
- **Purpose**: Add indexes to improve database query speed
- **Usage**: `python tests/create_indexes.py`
- **Note**: Run this after database setup to optimize performance

## Running Tests

From the backend directory:

```bash
# Test database queries
python tests/test_db_queries.py

# Test API performance (requires server running)
python tests/test_performance.py

# Create database indexes
python tests/create_indexes.py
```

## Test Results

Expected performance benchmarks:
- Simple games query: ~60-100ms
- Games with search: ~150-200ms
- Games with filters: ~100-150ms
- Mechanics query: ~50-100ms

## Notes

- All tests include timeout protection to prevent hanging
- Tests are designed to be non-destructive (read-only operations)
- Performance tests require a running FastAPI server
- Database indexes should be created after initial data import 