# Testing Guide

## Quick Start

### Install Test Dependencies
```bash
pip install pytest pytest-mock
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Priority 1: Data Quality (validates all 93 YAML files)
pytest tests/data -m data

# Unit Tests
pytest tests/unit -m unit

# LLM Contract Tests (no API calls)
pytest tests/contract -m contract

# Integration Tests
pytest tests/integration -m integration
```

---

## Test Categories

### 1. Data Quality Tests (`tests/data/`) ⭐⭐⭐
**Purpose**: Validate all 93 program YAML files  
**Coverage**:
- Schema compliance (Pydantic validation)
- Required fields presence (code, title, fees, etc.)
- Business rules (ECTS ranges, fee amounts)
- Data completeness (eligibility, documents)

**Run**: `pytest tests/data -v`

---

### 2. Unit Tests (`tests/unit/`) ⭐⭐⭐
**Purpose**: Test individual components in isolation  
**Coverage**:
- `test_models.py`: Pydantic model validation
- `test_session_manager.py`: Session CRUD operations

**Run**: `pytest tests/unit -v`

---

### 3. Contract Tests (`tests/contract/`) ⭐⭐
**Purpose**: Test LLM integration WITHOUT burning API credits  
**Coverage**:
- Prompt structure validation
- Mocked Gemini API responses
- Response parsing logic

**Run**: `pytest tests/contract -v`

---

### 4. Manual Voice Testing
**Purpose**: Validate STT/TTS features (cannot be automated)  
**Location**: `tests/manual_voice_checklist.md`

**Process**:
1. Open `manual_voice_checklist.md`
2. Run each scenario manually
3. Fill in "Expected" checkboxes and notes
4. Track issues in "Known Issues" section

---

## Continuous Integration

### Pre-Commit Hook (Recommended)
Run data quality tests before each commit:
```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/data --tb=short
```

### CI/CD Pipeline
For GitHub Actions or similar:
```yaml
- name: Run Tests
  run: |
    pip install pytest pytest-mock
    pytest tests/data tests/unit tests/contract --tb=short
```

---

## Interpreting Results

### Success Example
```
tests/data/test_yaml_validation.py::test_all_yaml_files_exist PASSED
tests/data/test_yaml_validation.py::test_yaml_schema_validation[ba_business_administration.yaml] PASSED
...
===================== 150 passed in 2.5s =====================
```

### Failure Example
```
FAILED tests/data/test_yaml_validation.py::test_yaml_schema_validation[ba_ai.yaml]
AssertionError: ba_ai.yaml failed validation:
  fees.international_non_eu: field required
```

**Action**: Fix the YAML file and re-run `pytest tests/data`

---

## Debugging Failed Tests

### View Full Error Details
```bash
pytest tests/data --tb=long
```

### Run Single Test File
```bash
pytest tests/data/test_yaml_validation.py -v
```

### Run Single Test Function
```bash
pytest tests/data/test_yaml_validation.py::test_fees_structure_complete -v
```

---

## Next Steps

### Phase 1 (Current) ✅
- [x] Data quality tests
- [x] Unit tests
- [x] LLM contract tests
- [x] Manual voice checklist

### Phase 2 (Future)
- [ ] Integration tests (`tests/integration/`)
- [ ] E2E tests with Playwright (`tests/e2e/`)

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
**Solution**: Run pytest from project root:
```bash
cd "E:\Bachelor Cyber Security\Semester 6\New folder"
pytest
```

### Tests are slow
**Solution**: Run only fast tests:
```bash
pytest -m "not slow"
```

---

## Questions?
Refer to `implementation_plan.md` for detailed testing strategy.
