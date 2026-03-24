PYTHON    := /Applications/MiniConda/miniconda3/envs/ai-supply-chain-risk-atlas/bin/python
INPUT     := data/models.csv
OUTROOT   := .
TIMESTAMP := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

.PHONY: test ingest scan clean

test:
	$(PYTHON) -m pytest -q

ingest:
	$(PYTHON) scripts/ingest_repo_artifacts.py \
	  --input $(INPUT) \
	  --output-root $(OUTROOT) \
	  --snapshot-timestamp "$(TIMESTAMP)"

scan:
	$(PYTHON) scripts/run_osv_scan.py \
	  --input manifests \
	  --output-root $(OUTROOT) \
	  --snapshot-timestamp "$(TIMESTAMP)"

clean:
	rm -rf manifests/
